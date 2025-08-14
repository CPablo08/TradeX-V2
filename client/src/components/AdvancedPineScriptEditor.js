import React, { useState, useEffect, useRef } from 'react';
import './AdvancedPineScriptEditor.css';
import BacktestingEngine from './BacktestingEngine';
import ChartPreview from './ChartPreview';

const AdvancedPineScriptEditor = ({ 
  value, 
  onChange, 
  placeholder = "Enter Pine Script strategy...",
  onSave,
  onValidate,
  symbol = "BTC"
}) => {
  const [isValid, setIsValid] = useState(true);
  const [validationMessage, setValidationMessage] = useState('');
  const [showLineNumbers, setShowLineNumbers] = useState(true);
  const [fontSize, setFontSize] = useState(14);
  const [theme, setTheme] = useState('dark');
  const textareaRef = useRef(null);
  const lineNumbersRef = useRef(null);

  // Pine Script keywords for syntax highlighting
  const pineKeywords = [
    'ta.', 'strategy.', 'request.security', 'plot', 'plotshape', 'plotchar',
    'if', 'else', 'for', 'while', 'return', 'var', 'float', 'int', 'bool',
    'close', 'open', 'high', 'low', 'volume', 'time', 'bar_index',
    'sma', 'ema', 'rsi', 'macd', 'bb', 'stoch', 'atr', 'adx',
    'crossover', 'crossunder', 'rising', 'falling',
    'and', 'or', 'not', 'true', 'false'
  ];

  // Auto-complete suggestions
  const suggestions = [
    { text: 'ta.rsi(close, 14)', description: 'RSI indicator' },
    { text: 'ta.sma(close, 20)', description: 'Simple Moving Average' },
    { text: 'ta.ema(close, 20)', description: 'Exponential Moving Average' },
    { text: 'ta.macd(close, 12, 26, 9)', description: 'MACD indicator' },
    { text: 'ta.bb(close, 20, 2)', description: 'Bollinger Bands' },
    { text: 'ta.stoch(high, low, close, 14)', description: 'Stochastic oscillator' },
    { text: 'ta.atr(high, low, close, 14)', description: 'Average True Range' },
    { text: 'return { action: "BUY", reason: "Signal", confidence: 80 }', description: 'Buy signal' },
    { text: 'return { action: "SELL", reason: "Signal", confidence: 80 }', description: 'Sell signal' },
    { text: 'return { action: "HOLD", reason: "No signal", confidence: 0 }', description: 'Hold signal' }
  ];

  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState([]);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [showBacktest, setShowBacktest] = useState(false);
  const [showChart, setShowChart] = useState(false);
  const [backtestResults, setBacktestResults] = useState(null);

  useEffect(() => {
    updateLineNumbers();
  }, [value]);

  const updateLineNumbers = () => {
    if (!lineNumbersRef.current) return;
    
    const lines = value.split('\n');
    const lineNumbers = lines.map((_, index) => index + 1).join('\n');
    lineNumbersRef.current.value = lineNumbers;
  };

  const handleChange = (e) => {
    const newValue = e.target.value;
    onChange(newValue);
    updateLineNumbers();
    validateCode(newValue);
  };

  const validateCode = async (code) => {
    if (!code.trim()) {
      setIsValid(true);
      setValidationMessage('');
      return;
    }

    try {
      if (onValidate) {
        const result = await onValidate(code);
        setIsValid(result.valid);
        setValidationMessage(result.error || 'Valid Pine Script');
      }
    } catch (error) {
      setIsValid(false);
      setValidationMessage('Validation error');
    }
  };

  const handleKeyDown = (e) => {
    const { key, ctrlKey, metaKey } = e;
    
    // Auto-complete on Ctrl+Space
    if ((ctrlKey || metaKey) && key === ' ') {
      e.preventDefault();
      setShowSuggestions(true);
      return;
    }

    // Tab completion
    if (key === 'Tab') {
      e.preventDefault();
      const textarea = e.target;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = textarea.value;
      
      // Insert tab or complete suggestion
      const newText = text.substring(0, start) + '    ' + text.substring(end);
      onChange(newText);
      
      // Set cursor position after tab
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }, 0);
    }

    // Save on Ctrl+S
    if ((ctrlKey || metaKey) && key === 's') {
      e.preventDefault();
      if (onSave) onSave();
    }
  };

  const handleInput = (e) => {
    const textarea = e.target;
    const cursorPos = textarea.selectionStart;
    setCursorPosition(cursorPos);
    
    // Auto-complete logic
    const text = textarea.value;
    const beforeCursor = text.substring(0, cursorPos);
    const lastWord = beforeCursor.split(/\s+/).pop();
    
    if (lastWord && lastWord.length > 1) {
      const filtered = suggestions.filter(s => 
        s.text.toLowerCase().includes(lastWord.toLowerCase()) ||
        s.description.toLowerCase().includes(lastWord.toLowerCase())
      );
      setFilteredSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setShowSuggestions(false);
    }
  };

  const insertSuggestion = (suggestion) => {
    const textarea = textareaRef.current;
    const text = textarea.value;
    const beforeCursor = text.substring(0, cursorPosition);
    const afterCursor = text.substring(cursorPosition);
    
    // Find the last word to replace
    const words = beforeCursor.split(/\s+/);
    const lastWord = words[words.length - 1];
    const newBeforeCursor = beforeCursor.substring(0, beforeCursor.lastIndexOf(lastWord));
    
    const newText = newBeforeCursor + suggestion.text + afterCursor;
    onChange(newText);
    
    setShowSuggestions(false);
    
    // Set cursor position after insertion
    setTimeout(() => {
      const newCursorPos = newBeforeCursor.length + suggestion.text.length;
      textarea.selectionStart = textarea.selectionEnd = newCursorPos;
    }, 0);
  };

  const formatCode = () => {
    // Basic code formatting
    let formatted = value
      .replace(/\s+/g, ' ') // Remove extra spaces
      .replace(/\s*{\s*/g, ' {\n  ') // Format opening braces
      .replace(/\s*}\s*/g, '\n}') // Format closing braces
      .replace(/\s*,\s*/g, ', ') // Format commas
      .replace(/\s*=\s*/g, ' = ') // Format equals
      .replace(/\s*\+\s*/g, ' + ') // Format plus
      .replace(/\s*-\s*/g, ' - ') // Format minus
      .replace(/\s*\*\s*/g, ' * ') // Format multiply
      .replace(/\s*\/\s*/g, ' / ') // Format divide
      .replace(/\s*>\s*/g, ' > ') // Format greater than
      .replace(/\s*<\s*/g, ' < ') // Format less than
      .replace(/\s*and\s*/g, ' and ') // Format and
      .replace(/\s*or\s*/g, ' or ') // Format or
      .replace(/\s*not\s*/g, ' not '); // Format not
    
    onChange(formatted);
  };

  const clearCode = () => {
    onChange('');
  };

  return (
    <div className={`pine-script-editor ${theme}`}>
      {/* Editor Toolbar */}
      <div className="editor-toolbar">
        <div className="toolbar-left">
          <span className="symbol-badge">{symbol}</span>
          <button 
            className={`toolbar-btn ${isValid ? 'valid' : 'invalid'}`}
            title={validationMessage}
          >
            {isValid ? '✓' : '✗'}
          </button>
        </div>
        
        <div className="toolbar-center">
          <button className="toolbar-btn" onClick={formatCode} title="Format Code">
            <span>⚙️</span>
          </button>
          <button className="toolbar-btn" onClick={clearCode} title="Clear">
            <span>🗑️</span>
          </button>
          <button 
            className="toolbar-btn" 
            onClick={() => setShowBacktest(!showBacktest)} 
            title="Toggle Backtesting"
          >
            <span>📊</span>
          </button>
          <button 
            className="toolbar-btn" 
            onClick={() => setShowChart(!showChart)} 
            title="Toggle Chart Preview"
          >
            <span>📈</span>
          </button>
        </div>
        
        <div className="toolbar-right">
          <select 
            value={fontSize} 
            onChange={(e) => setFontSize(Number(e.target.value))}
            className="font-size-select"
          >
            <option value={12}>12px</option>
            <option value={14}>14px</option>
            <option value={16}>16px</option>
            <option value={18}>18px</option>
          </select>
          
          <select 
            value={theme} 
            onChange={(e) => setTheme(e.target.value)}
            className="theme-select"
          >
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
          
          <button 
            className="toolbar-btn"
            onClick={() => setShowLineNumbers(!showLineNumbers)}
            title="Toggle Line Numbers"
          >
            <span>📋</span>
          </button>
        </div>
      </div>

      {/* Editor Container */}
      <div className="editor-container">
        {showLineNumbers && (
          <textarea
            ref={lineNumbersRef}
            className="line-numbers"
            readOnly
            style={{ fontSize: `${fontSize}px` }}
          />
        )}
        
        <div className="code-container">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder={placeholder}
            className="code-editor"
            style={{ fontSize: `${fontSize}px` }}
            spellCheck={false}
          />
          
          {/* Auto-complete Suggestions */}
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div className="suggestions-panel">
              {filteredSuggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="suggestion-item"
                  onClick={() => insertSuggestion(suggestion)}
                >
                  <div className="suggestion-text">{suggestion.text}</div>
                  <div className="suggestion-description">{suggestion.description}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <div className="status-left">
          <span>Pine Script v5</span>
          <span>•</span>
          <span>{value.split('\n').length} lines</span>
          <span>•</span>
          <span>{value.length} characters</span>
        </div>
        
        <div className="status-right">
          <span>Ctrl+Space: Auto-complete</span>
          <span>•</span>
          <span>Ctrl+S: Save</span>
        </div>
      </div>

      {/* Backtesting Engine */}
      {showBacktest && (
        <BacktestingEngine
          strategy={value}
          symbol={symbol}
          onResults={setBacktestResults}
        />
      )}

      {/* Chart Preview */}
      {showChart && (
        <ChartPreview
          data={backtestResults?.data || []}
          trades={backtestResults?.trades || []}
          strategy={value}
          symbol={symbol}
        />
      )}
    </div>
  );
};

export default AdvancedPineScriptEditor;
