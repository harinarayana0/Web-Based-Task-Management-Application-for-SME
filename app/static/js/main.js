/**
 * ServiceLink Main JavaScript
 * Handles client-side functionality and interactivity
 */

(function() {
    'use strict';

    // ========================================================================
    // INITIALIZATION
    // ========================================================================
    
    /**
     * Initialize the application when DOM is ready
     */
    document.addEventListener('DOMContentLoaded', function() {
        initAlerts();
        initFormValidation();
        initConfirmDialogs();
        initDateTimeInputs();
        initSearchFilters();
        console.log('ServiceLink initialized');
    });

    // ========================================================================
    // ALERT MANAGEMENT
    // ========================================================================
    
    /**
     * Auto-dismiss alerts after 5 seconds
     */
    function initAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }

    // ========================================================================
    // FORM VALIDATION
    // ========================================================================
    
    /**
     * Handle client-side form validation
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        Array.from(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    // ========================================================================
    // CONFIRM DIALOGS
    // ========================================================================
    
    /**
     * Add confirmation dialog to forms with data-confirm attribute
     */
    function initConfirmDialogs() {
        const confirmForms = document.querySelectorAll('form[data-confirm]');
        
        confirmForms.forEach(function(form) {
            form.addEventListener('submit', function(event) {
                const message = form.getAttribute('data-confirm');
                if (!confirm(message)) {
                    event.preventDefault();
                }
            });
        });
    }

    // ========================================================================
    // DATE AND TIME INPUTS
    // ========================================================================
    
    /**
     * Set minimum date for date inputs to today
     */
    function initDateTimeInputs() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        const today = new Date().toISOString().split('T')[0];
        
        dateInputs.forEach(function(input) {
            if (!input.hasAttribute('min')) {
                input.setAttribute('min', today);
            }
        });
    }

    // ========================================================================
    // SEARCH FILTERS
    // ========================================================================
    
    /**
     * Handle search filter changes
     */
    function initSearchFilters() {
        const searchForm = document.getElementById('search-form');
        if (!searchForm) return;
        
        const filterInputs = searchForm.querySelectorAll('input, select');
        
        filterInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                // Auto-submit could be enabled here if desired
                // searchForm.submit();
            });
        });
    }

    // ========================================================================
    // RATING DISPLAY
    // ========================================================================
    
    /**
     * Display star ratings dynamically
     * @param {number} rating - Rating value (0-5)
     * @param {HTMLElement} container - Container element for stars
     */
    window.displayRating = function(rating, container) {
        container.innerHTML = '';
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        
        for (let i = 0; i < 5; i++) {
            const star = document.createElement('i');
            if (i < fullStars) {
                star.className = 'bi bi-star-fill text-warning';
            } else if (i === fullStars && hasHalfStar) {
                star.className = 'bi bi-star-half text-warning';
            } else {
                star.className = 'bi bi-star text-warning';
            }
            container.appendChild(star);
        }
    };

    // ========================================================================
    // AJAX UTILITIES
    // ========================================================================
    
    /**
     * Make an AJAX request
     * @param {string} url - Request URL
     * @param {Object} options - Request options
     * @returns {Promise} - Fetch promise
     */
    window.ajaxRequest = function(url, options = {}) {
        const defaults = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };
        
        const config = Object.assign({}, defaults, options);
        
        return fetch(url, config)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('AJAX request failed:', error);
                throw error;
            });
    };

    // ========================================================================
    // LOADING SPINNER
    // ========================================================================
    
    /**
     * Show loading spinner
     */
    window.showLoading = function() {
        const spinner = document.createElement('div');
        spinner.id = 'loading-spinner';
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        document.body.appendChild(spinner);
    };
    
    /**
     * Hide loading spinner
     */
    window.hideLoading = function() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    };

    // ========================================================================
    // TOAST NOTIFICATIONS
    // ========================================================================
    
    /**
     * Show a toast notification
     * @param {string} message - Notification message
     * @param {string} type - Toast type (success, error, warning, info)
     */
    window.showToast = function(message, type = 'info') {
        const toastContainer = getOrCreateToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    };
    
    /**
     * Get or create toast container
     * @returns {HTMLElement} - Toast container element
     */
    function getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        return container;
    }

    // ========================================================================
    // PRICE FORMATTING
    // ========================================================================
    
    /**
     * Format price for display
     * @param {number} price - Price value
     * @returns {string} - Formatted price string
     */
    window.formatPrice = function(price) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(price);
    };

    // ========================================================================
    // DATE FORMATTING
    // ========================================================================
    
    /**
     * Format date for display
     * @param {string|Date} date - Date to format
     * @returns {string} - Formatted date string
     */
    window.formatDate = function(date) {
        const d = new Date(date);
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    // ========================================================================
    // SMOOTH SCROLLING
    // ========================================================================
    
    /**
     * Enable smooth scrolling for anchor links
     */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ========================================================================
    // BACK TO TOP BUTTON
    // ========================================================================
    
    /**
     * Show/hide back to top button based on scroll position
     */
    window.addEventListener('scroll', function() {
        const backToTop = document.getElementById('back-to-top');
        if (backToTop) {
            if (window.pageYOffset > 300) {
                backToTop.style.display = 'block';
            } else {
                backToTop.style.display = 'none';
            }
        }
    });

    // ========================================================================
    // DEBOUNCE UTILITY
    // ========================================================================
    
    /**
     * Debounce function to limit function calls
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} - Debounced function
     */
    window.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

})();
