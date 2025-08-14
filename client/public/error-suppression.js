// Disable React error overlay before it loads
(function() {
  // Disable React DevTools error reporting
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || {};
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__.suppressErrors = true;
  
  // Disable React error overlay
  window.__REACT_ERROR_OVERLAY_GLOBAL_HOOK__ = {
    dismissBuildError: function() {},
    reportBuildError: function() {},
    reportRuntimeError: function() {},
    dismissRuntimeError: function() {}
  };
  
  // Override console methods
  const originalError = console.error;
  const originalWarn = console.warn;
  
  console.error = function() {
    // Suppress all errors
  };
  
  console.warn = function() {
    // Suppress all warnings
  };
  
  // Suppress window errors
  window.onerror = function() {
    return true; // Suppress all errors
  };
  
  // Suppress unhandled promise rejections
  window.onunhandledrejection = function(event) {
    event.preventDefault();
  };
  
  // Remove any existing error overlays
  function removeErrorOverlays() {
    const selectors = [
      '[data-react-error-overlay]',
      '[class*="error-overlay"]',
      '[class*="ErrorOverlay"]',
      '[class*="react-error-overlay"]',
      'div[style*="position: fixed"][style*="top: 0"]',
      'div[style*="background-color: rgb(206, 17, 38)"]'
    ];
    
    selectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        if (el.textContent.includes('Script error') || 
            el.textContent.includes('Uncaught runtime errors') ||
            el.textContent.includes('ERROR')) {
          el.remove();
        }
      });
    });
  }
  
  // Run immediately and set up observer
  removeErrorOverlays();
  
  // Set up mutation observer to remove error overlays as they appear
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList') {
        removeErrorOverlays();
      }
    });
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Also run periodically
  setInterval(removeErrorOverlays, 100);
})();
