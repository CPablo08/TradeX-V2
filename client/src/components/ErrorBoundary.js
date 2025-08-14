import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Suppress script errors and return null to prevent error state
    if (error && error.message && (
      error.message.includes('Script error') ||
      error.message.includes('tradingview') ||
      error.message.includes('external-embedding') ||
      error.message.includes('bundle.js')
    )) {
      return { hasError: false };
    }
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Suppress script errors from logging
    if (error && error.message && (
      error.message.includes('Script error') ||
      error.message.includes('tradingview') ||
      error.message.includes('external-embedding') ||
      error.message.includes('bundle.js')
    )) {
      return;
    }
    
    // Log other errors normally
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong.</div>;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
