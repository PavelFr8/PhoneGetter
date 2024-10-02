document.addEventListener('DOMContentLoaded', function () {
  const navLinks = document.querySelectorAll('.sidebar .nav-link');
  const sidebar = document.querySelector('.sidebar');
  const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');

  // Load the sidebar state from local storage
  const sidebarState = localStorage.getItem('sidebarState');

  if (sidebarState === 'hidden') {
    sidebar.classList.add('hidden');
    toggleSidebarBtn.style.left = '5px'; // Adjust button position when sidebar is hidden
  } else {
    toggleSidebarBtn.style.left = '85px'; // Adjust button position when sidebar is visible
  }

  navLinks.forEach(link => {
    link.addEventListener('mouseover', () => {
      link.style.transform = 'scale(1.1)';
    });

    link.addEventListener('mouseout', () => {
      link.style.transform = 'scale(1)';
    });
  });

  toggleSidebarBtn.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');

    // Save the sidebar state in local storage
    if (sidebar.classList.contains('hidden')) {
      localStorage.setItem('sidebarState', 'hidden');
      toggleSidebarBtn.style.left = '5px'; // Position when sidebar is hidden
    } else {
      localStorage.setItem('sidebarState', 'visible');
      toggleSidebarBtn.style.left = '85px'; // Position when sidebar is visible
    }
  });
});

/* global bootstrap: false */
(() => {
  'use strict'
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(tooltipTriggerEl => {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})();


document.querySelectorAll('.qwertr').forEach(function (item) {
    item.addEventListener('click', function () {
        let selectedLang = this.getAttribute('data-lang');
        document.cookie = "language=" + selectedLang + "; path=/";
        location.reload();
    });
});