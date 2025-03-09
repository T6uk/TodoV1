/**
 * Enhanced Dark Mode functionality
 *
 * This script handles toggling between light and dark mode,
 * saving user preferences, and updating visual indicators.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Check for saved preference
  const darkModeSetting = localStorage.getItem('darkMode');
  const darkModeToggle = document.getElementById('dark-mode-toggle');
  const darkModeIcon = darkModeToggle ? darkModeToggle.querySelector('i') : null;

  // Function to update theme
  function setDarkMode(enabled) {
    if (enabled) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('darkMode', 'enabled');
      if (darkModeIcon) {
        darkModeIcon.classList.remove('fa-moon');
        darkModeIcon.classList.add('fa-sun');
      }
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('darkMode', 'disabled');
      if (darkModeIcon) {
        darkModeIcon.classList.remove('fa-sun');
        darkModeIcon.classList.add('fa-moon');
      }
    }
  }

  // Apply dark mode if previously saved
  if (darkModeSetting === 'enabled') {
    setDarkMode(true);
  }

  // Toggle dark mode when button is clicked
  if (darkModeToggle) {
    darkModeToggle.addEventListener('click', function() {
      const isDarkMode = document.body.classList.contains('dark-mode');
      setDarkMode(!isDarkMode);
    });
  }

  // Check if user prefers dark mode at the system level
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

  // If no saved preference and system prefers dark mode, enable it
  if (!darkModeSetting && prefersDarkScheme.matches) {
    setDarkMode(true);
  }

  // Listen for changes to the prefers-color-scheme media query
  prefersDarkScheme.addEventListener('change', (event) => {
    // Only apply if user hasn't set a preference
    if (!localStorage.getItem('darkMode')) {
      setDarkMode(event.matches);
    }
  });
});