/* JavaScript for Dark Mode Toggle - Add to a new file dark-mode.js */
document.addEventListener('DOMContentLoaded', function() {
  // Check for saved preference
  const darkMode = localStorage.getItem('darkMode');
  const darkModeToggle = document.getElementById('dark-mode-toggle');

  // Apply dark mode if previously saved
  if (darkMode === 'enabled') {
    document.body.classList.add('dark-mode');
    updateToggleIcon(true);
  }

  // Toggle dark mode when button is clicked
  darkModeToggle.addEventListener('click', function() {
    if (document.body.classList.contains('dark-mode')) {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('darkMode', 'disabled');
      updateToggleIcon(false);
    } else {
      document.body.classList.add('dark-mode');
      localStorage.setItem('darkMode', 'enabled');
      updateToggleIcon(true);
    }
  });

  // Update the icon based on dark mode state
  function updateToggleIcon(isDarkMode) {
    const icon = darkModeToggle.querySelector('i');
    if (isDarkMode) {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
    } else {
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
    }
  }
});