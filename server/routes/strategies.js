const express = require('express');
const router = express.Router();

// Get all strategies
router.get('/', async (req, res) => {
  try {
    const logicEngine = req.app.locals.logicEngine;
    const strategies = await logicEngine.getAllStrategies();
    
    res.json({
      success: true,
      data: strategies
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get strategy for specific symbol
router.get('/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const logicEngine = req.app.locals.logicEngine;
    const strategy = await logicEngine.getStrategy(symbol);
    
    if (!strategy) {
      return res.status(404).json({
        success: false,
        error: `No strategy found for ${symbol}`
      });
    }
    
    res.json({
      success: true,
      data: strategy
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Update strategy for specific symbol
router.put('/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const { name, code } = req.body;
    
    if (!name || !code) {
      return res.status(400).json({
        success: false,
        error: 'Name and code are required'
      });
    }
    
    const logicEngine = req.app.locals.logicEngine;
    await logicEngine.updateStrategy(symbol, name, code);
    
    res.json({
      success: true,
      message: `Strategy updated for ${symbol}`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Validate Pine Script code
router.post('/validate', async (req, res) => {
  try {
    const { code } = req.body;
    
    if (!code) {
      return res.status(400).json({
        success: false,
        error: 'Code is required'
      });
    }
    
    const logicEngine = req.app.locals.logicEngine;
    const validation = logicEngine.validatePineScript(code);
    
    res.json({
      success: true,
      validation: validation
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Test strategy for specific symbol
router.post('/:symbol/test', async (req, res) => {
  try {
    const { symbol } = req.params;
    const logicEngine = req.app.locals.logicEngine;
    
    const decision = await logicEngine.evaluateStrategy(symbol);
    
    res.json({
      success: true,
      data: decision
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
