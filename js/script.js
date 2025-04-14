/**
 * AgriConnect Data System - Main JavaScript
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add smooth scrolling to all links
    const links = document.querySelectorAll('a[href^="#"]');
    for (const link of links) {
        link.addEventListener('click', smoothScroll);
    }
    
    // Handle mobile menu closing when link is clicked
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    for (const link of navLinks) {
        link.addEventListener('click', function() {
            if (navbarCollapse.classList.contains('show')) {
                const navbarToggler = document.querySelector('.navbar-toggler');
                navbarToggler.click();
            }
        });
    }
    
    // Add back-to-top button functionality
    if (document.querySelector('.back-to-top')) {
        window.addEventListener('scroll', toggleBackToTopButton);
        document.querySelector('.back-to-top').addEventListener('click', scrollToTop);
    }
});

/**
 * Smooth scroll function
 */
function smoothScroll(e) {
    e.preventDefault();
    const targetId = this.getAttribute('href');
    if (targetId === '#') return;
    
    const targetPosition = document.querySelector(targetId).offsetTop - 80;
    window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
    });
}

/**
 * Toggle back-to-top button visibility
 */
function toggleBackToTopButton() {
    const backToTopBtn = document.querySelector('.back-to-top');
    if (window.pageYOffset > 300) {
        backToTopBtn.style.display = 'block';
    } else {
        backToTopBtn.style.display = 'none';
    }
}

/**
 * Scroll to top function
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * Display current year in footer copyright
 */
function displayCurrentYear() {
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
}

// Call the function to display current year
displayCurrentYear();

/**
 * Form validation helper
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    form.classList.add('was-validated');
    return form.checkValidity();
} 