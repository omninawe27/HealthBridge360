// HealthKart 360 Main JavaScript File

// Global variables
let currentUser = null;
let notifications = [];
let cart = JSON.parse(localStorage.getItem('healthkart_cart')) || [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserPreferences();
});

// Initialize the application
function initializeApp() {
    console.log('HealthKart 360 Initializing...');
    
    // Add loading spinner
    addLoadingSpinner();
    
  // Initialize tooltips
    initializeTooltips();
    
    // Initialize notifications
    initializeNotifications();
    
    // Check for service worker
    if ('serviceWorker' in navigator) {
        registerServiceWorker();
    }
    
    // Remove loading spinner
  setTimeout(() => {
        removeLoadingSpinner();
    }, 1000);
}

// Setup event listeners
function setupEventListeners() {
  // Search functionality
    const searchForm = document.querySelector('form[action*="search"]');
  if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
    
    // Add to cart buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('.add-to-cart, [onclick*="addToCart"]')) {
            e.preventDefault();
            const medicineId = e.target.dataset.medicineId || 
                              e.target.getAttribute('onclick').match(/\d+/)[0];
            addToCart(medicineId);
        }
    });
    
    // Emergency mode toggle
    const emergencyBtn = document.querySelector('.emergency-toggle');
    if (emergencyBtn) {
        emergencyBtn.addEventListener('click', toggleEmergencyMode);
    }
    
    // Language switcher
    const languageSelect = document.querySelector('select[name="language"]');
    if (languageSelect) {
        languageSelect.addEventListener('change', changeLanguage);
    }
    
    // Form validation
    setupFormValidation();
}

// Search functionality
function handleSearch(e) {
    const searchInput = e.target.querySelector('input[name="q"]');
    const query = searchInput.value.trim();
    
    if (query.length < 2) {
        showToast('Please enter at least 2 characters to search', 'warning');
        e.preventDefault();
        return false;
    }
    
    // Add loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
        submitBtn.disabled = true;
    }
}

// Add to cart functionality
function addToCart(medicineId) {
    fetch(`/orders/add-to-cart/${medicineId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count);
            showToast('Medicine added to cart!', 'success');
        } else {
            showToast(data.message || 'Failed to add medicine to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showToast('Network error. Please try again.', 'error');
    });
}

// Update cart count in UI
function updateCartCount(count) {
    const cartBadge = document.querySelector('.cart-count');
    if (cartBadge) {
        cartBadge.textContent = count;
        cartBadge.style.display = count > 0 ? 'inline' : 'none';
    }
}

// Emergency mode toggle
function toggleEmergencyMode() {
    const body = document.body;
    const isEmergency = body.classList.toggle('emergency-mode-active');
    
    if (isEmergency) {
        showToast('Emergency mode activated', 'warning');
        // Redirect to emergency page
        window.location.href = '/emergency/';
    } else {
        showToast('Emergency mode deactivated', 'info');
    }
}

// Language change
function changeLanguage(e) {
    const language = e.target.value;
    
    fetch('/users/change-language/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            language: language
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Language changed successfully', 'success');
            // Reload page to apply new language
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showToast('Failed to change language', 'error');
        }
    })
    .catch(error => {
        console.error('Error changing language:', error);
        showToast('Network error. Please try again.', 'error');
    });
}

// Toast notifications
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Show animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, duration);
}

// Get toast icon based on type
function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Initialize notifications
function initializeNotifications() {
    // Check for browser notifications permission
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
    
    // Setup notification styles
    const style = document.createElement('style');
    style.textContent = `
        .toast-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 15px 20px;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
        }
        .toast-notification.show {
            transform: translateX(0);
        }
        .toast-content {
            display: flex;
            align-items: center;
        }
        .toast-success { border-left: 4px solid #28a745; }
        .toast-error { border-left: 4px solid #dc3545; }
        .toast-warning { border-left: 4px solid #ffc107; }
        .toast-info { border-left: 4px solid #17a2b8; }
    `;
    document.head.appendChild(style);
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                showToast('Please fill all required fields correctly', 'warning');
            }
            form.classList.add('was-validated');
        });
    });
}

// Loading spinner functions
function addLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.id = 'loading-spinner';
    spinner.innerHTML = `
        <div class="spinner-overlay">
            <div class="spinner">
                <i class="fas fa-heartbeat fa-2x text-primary"></i>
                <p class="mt-2">Loading HealthKart 360...</p>
            </div>
        </div>
    `;
    document.body.appendChild(spinner);
}

function removeLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Get CSRF token
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Load user preferences
function loadUserPreferences() {
    const preferences = JSON.parse(localStorage.getItem('healthkart_preferences')) || {};
    
    // Apply theme
    if (preferences.theme) {
        document.body.setAttribute('data-theme', preferences.theme);
    }
    
    // Apply language
    if (preferences.language) {
        const languageSelect = document.querySelector('select[name="language"]');
        if (languageSelect) {
            languageSelect.value = preferences.language;
        }
    }
}

// Save user preferences
function saveUserPreferences(preferences) {
    const current = JSON.parse(localStorage.getItem('healthkart_preferences')) || {};
    const updated = { ...current, ...preferences };
    localStorage.setItem('healthkart_preferences', JSON.stringify(updated));
}

// Service Worker Registration
function registerServiceWorker() {
    navigator.serviceWorker.register('/static/js/sw.js')
        .then(function(registration) {
            console.log('Service Worker registered successfully:', registration);
        })
        .catch(function(error) {
            console.log('Service Worker registration failed:', error);
        });
}

// Geolocation functions
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation not supported'));
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => resolve({
                lat: position.coords.latitude,
                lng: position.coords.longitude
            }),
            error => reject(error),
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    });
}

// Share location
function shareLocation() {
    getCurrentLocation()
        .then(coords => {
            const url = `https://www.google.com/maps?q=${coords.lat},${coords.lng}`;
            
            if (navigator.share) {
                navigator.share({
                    title: 'My Location',
                    text: 'I need help at this location',
                    url: url
                });
        } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(url).then(() => {
                    showToast('Location copied to clipboard!', 'success');
                });
            }
        })
        .catch(error => {
            showToast('Unable to get location: ' + error.message, 'error');
        });
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.HealthKart360 = {
    showToast,
    addToCart,
    shareLocation,
    getCurrentLocation,
    formatCurrency,
    formatDate,
    saveUserPreferences
};
