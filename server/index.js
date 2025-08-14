require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');

// Import modules
const Database = require('./modules/Database');
const DataRetriever = require('./modules/DataRetriever');
const LogicEngine = require('./modules/LogicEngine');
const Executor = require('./modules/Executor');
const Watchdog = require('./modules/Watchdog');

// Import routes
const dataRoutes = require('./routes/data');
const tradingRoutes = require('./routes/trading');
const strategiesRoutes = require('./routes/strategies');
const performanceRoutes = require('./routes/performance');
const systemRoutes = require('./routes/system');

// Create Express app
const app = express();
const PORT = process.env.PORT || 5000;

// Initialize logger
const winston = require('winston');
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'tradex' },
  transports: [
    new winston.transports.File({ 
      filename: process.env.LOG_FILE_PATH || './logs/tradex.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Initialize modules
let db, dataRetriever, logicEngine, executor, watchdog;
let tradingTasks = {
  dataRetrieval: null,
  tradingLogic: null,
  healthCheck: null
};
let isTradingActive = false;
let systemInitialized = false;

// Middleware
app.use(helmet());
app.use(cors());
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs
  message: 'Too many requests from this IP'
});
app.use('/api/', limiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    tradingMode: process.env.TRADING_MODE
  });
});

// API routes
app.use('/api/data', dataRoutes);
app.use('/api/trading', tradingRoutes);
app.use('/api/strategies', strategiesRoutes);
app.use('/api/performance', performanceRoutes);
app.use('/api/system', systemRoutes);

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../client/build')));
  
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../client/build/index.html'));
  });
}

// Initialize system
async function initializeSystem() {
  try {
    logger.info('Initializing TradeX system...');
    
    // Initialize database
    db = new Database(logger);
    await db.initialize();
    logger.info('Database initialized');
    
    // Initialize DataRetriever
    dataRetriever = new DataRetriever(logger, db);
    await dataRetriever.initialize();
    logger.info('DataRetriever initialized');
    
    // Initialize LogicEngine
    logicEngine = new LogicEngine(logger, db, dataRetriever);
    await logicEngine.initialize();
    logger.info('LogicEngine initialized');
    
    // Initialize Executor
    executor = new Executor(logger, db);
    await executor.initialize();
    logger.info('Executor initialized');
    
    // Initialize Watchdog
    watchdog = new Watchdog(logger, {
      dataRetriever,
      logicEngine,
      executor,
      db
    });
    await watchdog.initialize();
    logger.info('Watchdog initialized');
    
    // Make modules available to routes
    app.locals.db = db;
    app.locals.dataRetriever = dataRetriever;
    app.locals.logicEngine = logicEngine;
    app.locals.executor = executor;
    app.locals.watchdog = watchdog;
    app.locals.startTrading = startTrading;
    app.locals.stopTrading = stopTrading;
    app.locals.getTradingStatus = getTradingStatus;
    app.locals.getSystemStatus = getSystemStatus;
    
    systemInitialized = true;
    logger.info('TradeX system initialized successfully');
    
  } catch (error) {
    logger.error('System initialization failed:', error);
    process.exit(1);
  }
}

// Start scheduled tasks
function startScheduledTasks() {
  const cron = require('node-cron');
  
  // Data retrieval every 30 seconds
  tradingTasks.dataRetrieval = cron.schedule('*/30 * * * * *', async () => {
    if (!isTradingActive) return;
    try {
      await dataRetriever.fetchInitialData();
    } catch (error) {
      logger.error('Scheduled data retrieval failed:', error);
    }
  });
  
  // Trading logic evaluation every minute
  tradingTasks.tradingLogic = cron.schedule('0 * * * * *', async () => {
    if (!isTradingActive) return;
    try {
      const decision = await logicEngine.processData();
      if (decision && decision.action !== 'HOLD') {
        await executor.executeTrade(decision);
      }
    } catch (error) {
      logger.error('Scheduled trading logic failed:', error);
    }
  });
  
  // Health check every 30 seconds
  tradingTasks.healthCheck = cron.schedule('*/30 * * * * *', async () => {
    try {
      await watchdog.performHealthCheck();
    } catch (error) {
      logger.error('Scheduled health check failed:', error);
    }
  });
  
  logger.info('Scheduled tasks started (trading disabled by default)');
}

// Trading control functions
function startTrading() {
  if (isTradingActive) {
    return { success: false, message: 'Trading is already active' };
  }
  
  isTradingActive = true;
  logger.info('Trading system activated');
  return { success: true, message: 'Trading system started successfully' };
}

function stopTrading() {
  if (!isTradingActive) {
    return { success: false, message: 'Trading is not active' };
  }
  
  isTradingActive = false;
  logger.info('Trading system deactivated');
  return { success: true, message: 'Trading system stopped successfully' };
}

function getTradingStatus() {
  return {
    isActive: isTradingActive,
    mode: process.env.TRADING_MODE || 'paper'
  };
}

function getSystemStatus() {
  return {
    initialized: systemInitialized,
    components: {
      database: !!db,
      dataRetriever: !!dataRetriever,
      logicEngine: !!logicEngine,
      executor: !!executor,
      watchdog: !!watchdog
    },
    tradingActive: isTradingActive,
    uptime: process.uptime(),
    memory: process.memoryUsage()
  };
}

// Graceful shutdown
function gracefulShutdown(signal) {
  logger.info(`Received ${signal}. Starting graceful shutdown...`);
  
  // Close database connection
  if (db) {
    db.close();
  }
  
  // Close WebSocket connections
  if (dataRetriever && typeof dataRetriever.close === 'function') {
    dataRetriever.close();
  }
  
  // Stop watchdog
  if (watchdog) {
    watchdog.stop();
  }
  
  logger.info('Graceful shutdown completed');
  process.exit(0);
}

// Start server
async function startServer() {
  try {
    await initializeSystem();
    startScheduledTasks();
    
    app.listen(PORT, () => {
      logger.info(`TradeX server running on port ${PORT}`);
    });
    
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Handle shutdown signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  gracefulShutdown('uncaughtException');
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  gracefulShutdown('unhandledRejection');
});

// Start the server
startServer();
