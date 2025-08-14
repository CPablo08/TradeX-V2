const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class Database {
  constructor(logger) {
    this.logger = logger;
    this.db = null;
    this.dbPath = process.env.DATABASE_PATH || './data/tradex.db';
  }

  async initialize() {
    try {
      // Ensure data directory exists
      const dataDir = path.dirname(this.dbPath);
      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }

      // Connect to database
      this.db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) {
          this.logger.error('Error opening database:', err);
          throw err;
        }
        this.logger.info('Connected to SQLite database');
      });

      // Create tables
      await this.createTables();
      
      this.logger.info('Database initialized successfully');
    } catch (error) {
      this.logger.error('Database initialization failed:', error);
      throw error;
    }
  }

  async createTables() {
    const tables = [
      // Market data table
      `CREATE TABLE IF NOT EXISTS market_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        price REAL NOT NULL,
        change_24h REAL,
        volume REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,

      // Account data table
      `CREATE TABLE IF NOT EXISTS account_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        balance REAL NOT NULL,
        positions TEXT,
        pnl REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,

      // Strategies table
      `CREATE TABLE IF NOT EXISTS strategies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,

      // Trade history table
      `CREATE TABLE IF NOT EXISTS trade_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        quantity REAL,
        price REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'executed',
        pnl REAL
      )`,

      // Performance metrics table
      `CREATE TABLE IF NOT EXISTS performance_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        total_trades INTEGER DEFAULT 0,
        winning_trades INTEGER DEFAULT 0,
        total_pnl REAL DEFAULT 0,
        win_rate REAL DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,

      // System logs table
      `CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,

      // Historical data table
      `CREATE TABLE IF NOT EXISTS historical_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume REAL,
        timestamp DATETIME NOT NULL
      )`
    ];

    for (const table of tables) {
      await this.run(table);
    }

    this.logger.info('Database tables created successfully');
  }

  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id: this.lastID, changes: this.changes });
        }
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // Market data methods
  async saveMarketData(data) {
    const sql = `
      INSERT INTO market_data (symbol, price, change_24h, volume)
      VALUES (?, ?, ?, ?)
    `;
    await this.run(sql, [data.symbol, data.price, data.change24h, data.volume]);
  }

  async getLatestMarketData(symbol) {
    const sql = `
      SELECT * FROM market_data 
      WHERE symbol = ? 
      ORDER BY timestamp DESC 
      LIMIT 1
    `;
    return await this.get(sql, [symbol]);
  }

  // Account data methods
  async saveAccountData(data) {
    const sql = `
      INSERT INTO account_data (balance, positions, pnl)
      VALUES (?, ?, ?)
    `;
    const positions = JSON.stringify(data.positions || []);
    await this.run(sql, [data.balance, positions, data.pnl]);
  }

  async getLatestAccountData() {
    const sql = `
      SELECT * FROM account_data 
      ORDER BY timestamp DESC 
      LIMIT 1
    `;
    const data = await this.get(sql);
    if (data) {
      data.positions = JSON.parse(data.positions || '[]');
    }
    return data;
  }

  // Strategy methods
  async saveStrategy(symbol, name, code) {
    const sql = `
      INSERT OR REPLACE INTO strategies (symbol, name, code, is_active, updated_at)
      VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
    `;
    await this.run(sql, [symbol, name, code]);
  }

  async getStrategy(symbol) {
    const sql = `SELECT * FROM strategies WHERE symbol = ? AND is_active = 1`;
    return await this.get(sql, [symbol]);
  }

  async getAllStrategies() {
    const sql = `SELECT * FROM strategies WHERE is_active = 1`;
    return await this.all(sql);
  }

  // Trade history methods
  async saveTrade(trade) {
    const sql = `
      INSERT INTO trade_history (symbol, action, quantity, price, pnl)
      VALUES (?, ?, ?, ?, ?)
    `;
    await this.run(sql, [trade.symbol, trade.action, trade.quantity, trade.price, trade.pnl]);
  }

  async getTradeHistory(limit = 100) {
    const sql = `
      SELECT * FROM trade_history 
      ORDER BY timestamp DESC 
      LIMIT ?
    `;
    return await this.all(sql, [limit]);
  }

  // Performance methods
  async savePerformanceMetrics(metrics) {
    const sql = `
      INSERT OR REPLACE INTO performance_metrics 
      (date, total_trades, winning_trades, total_pnl, win_rate)
      VALUES (?, ?, ?, ?, ?)
    `;
    await this.run(sql, [
      metrics.date,
      metrics.totalTrades,
      metrics.winningTrades,
      metrics.totalPnl,
      metrics.winRate
    ]);
  }

  async getPerformanceMetrics(date) {
    const sql = `SELECT * FROM performance_metrics WHERE date = ?`;
    return await this.get(sql, [date]);
  }

  // Historical data methods
  async saveHistoricalData(symbol, data) {
    const sql = `
      INSERT INTO historical_data (symbol, open, high, low, close, volume, timestamp)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `;
    await this.run(sql, [
      symbol,
      data.open,
      data.high,
      data.low,
      data.close,
      data.volume,
      data.timestamp
    ]);
  }

  async getHistoricalData(symbol, limit = 100) {
    const sql = `
      SELECT * FROM historical_data 
      WHERE symbol = ? 
      ORDER BY timestamp DESC 
      LIMIT ?
    `;
    return await this.all(sql, [symbol, limit]);
  }

  // System log methods
  async saveSystemLog(level, message) {
    const sql = `INSERT INTO system_logs (level, message) VALUES (?, ?)`;
    await this.run(sql, [level, message]);
  }

  async getSystemLogs(limit = 100) {
    const sql = `
      SELECT * FROM system_logs 
      ORDER BY timestamp DESC 
      LIMIT ?
    `;
    return await this.all(sql, [limit]);
  }

  // Database maintenance
  async vacuum() {
    await this.run('VACUUM');
  }

  async getDatabaseStats() {
    const tables = ['market_data', 'account_data', 'strategies', 'trade_history', 'performance_metrics', 'system_logs', 'historical_data'];
    const stats = {};
    
    for (const table of tables) {
      const result = await this.get(`SELECT COUNT(*) as count FROM ${table}`);
      stats[table] = result.count;
    }
    
    return stats;
  }

  close() {
    if (this.db) {
      this.db.close((err) => {
        if (err) {
          this.logger.error('Error closing database:', err);
        } else {
          this.logger.info('Database connection closed');
        }
      });
    }
  }
}

module.exports = Database;
