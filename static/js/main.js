/**
 * Main JavaScript — Theme toggle, toast auto-dismiss, hamburger menu,
 * and general UI interactivity.
 */

(function () {
    'use strict';

    // ────────────────────────────────────────────────────────────
    // 1. THEME TOGGLE
    // ────────────────────────────────────────────────────────────

    const THEME_KEY = 'sms-theme';

    function getStoredTheme() {
        return localStorage.getItem(THEME_KEY) || 'dark';
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
    }

    // Apply saved theme immediately (prevents flash)
    setTheme(getStoredTheme());

    document.addEventListener('DOMContentLoaded', () => {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const current = getStoredTheme();
                const next = current === 'dark' ? 'light' : 'dark';
                setTheme(next);

                // Re-initialize Lucide icons after theme swap
                if (window.lucide) {
                    lucide.createIcons();
                }
            });
        }
    });


    // ────────────────────────────────────────────────────────────
    // 2. TOAST AUTO-DISMISS
    // ────────────────────────────────────────────────────────────

    document.addEventListener('DOMContentLoaded', () => {
        const toasts = document.querySelectorAll('.toast[data-auto-dismiss]');

        toasts.forEach((toast) => {
            const delay = parseInt(toast.dataset.autoDismiss, 10) || 4000;

            setTimeout(() => {
                toast.style.animation = 'toast-slide-out 0.3s var(--ease-out) forwards';
                setTimeout(() => toast.remove(), 300);
            }, delay);
        });
    });


    // ────────────────────────────────────────────────────────────
    // 3. MOBILE HAMBURGER MENU
    // ────────────────────────────────────────────────────────────

    document.addEventListener('DOMContentLoaded', () => {
        const hamburger = document.getElementById('nav-hamburger');
        const mobileMenu = document.getElementById('mobile-menu');

        if (hamburger && mobileMenu) {
            hamburger.addEventListener('click', () => {
                hamburger.classList.toggle('active');
                mobileMenu.classList.toggle('active');

                // Prevent body scroll when menu is open
                document.body.style.overflow =
                    mobileMenu.classList.contains('active') ? 'hidden' : '';
            });

            // Close menu when clicking a link
            mobileMenu.querySelectorAll('.navbar__mobile-link').forEach((link) => {
                link.addEventListener('click', () => {
                    hamburger.classList.remove('active');
                    mobileMenu.classList.remove('active');
                    document.body.style.overflow = '';
                });
            });
        }
    });


    // ────────────────────────────────────────────────────────────
    // 4. CONFIRMATION MODAL HELPERS
    // ────────────────────────────────────────────────────────────

    /**
     * Open a delete confirmation modal.
     * @param {string} studentName — Name displayed in the modal message.
     * @param {string} deleteUrl — The form action URL for the delete POST.
     */
    window.openDeleteModal = function (studentName, deleteUrl) {
        const overlay = document.getElementById('delete-modal-overlay');
        const nameEl = document.getElementById('delete-student-name');
        const form = document.getElementById('delete-form');

        if (overlay && nameEl && form) {
            nameEl.textContent = studentName;
            form.action = deleteUrl;
            overlay.classList.add('active');
        }
    };

    window.closeDeleteModal = function () {
        const overlay = document.getElementById('delete-modal-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    };

    // Close modal on overlay click
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            window.closeDeleteModal();
        }
    });

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            window.closeDeleteModal();
        }
    });


    // ────────────────────────────────────────────────────────────
    // 5. COUNT-UP ANIMATION (Dashboard stat cards)
    // ────────────────────────────────────────────────────────────

    /**
     * Animate a number counting up from 0 to the target value.
     * @param {HTMLElement} el — The element containing the target number.
     * @param {number} duration — Animation duration in milliseconds.
     */
    window.animateCountUp = function (el, duration = 1200) {
        const target = parseFloat(el.textContent);
        if (isNaN(target)) return;

        const isFloat = target % 1 !== 0;
        const start = performance.now();

        function step(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);

            // Ease-out curve
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = eased * target;

            el.textContent = isFloat ? current.toFixed(1) : Math.floor(current);

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = isFloat ? target.toFixed(1) : target;
            }
        }

        el.textContent = '0';
        requestAnimationFrame(step);
    };


    // ────────────────────────────────────────────────────────────
    // 6. UTILITY FUNCTIONS
    // ────────────────────────────────────────────────────────────

    /**
     * Debounce a function call.
     * @param {Function} fn — The function to debounce.
     * @param {number} delay — Delay in ms (default 300).
     * @returns {Function}
     */
    window.debounce = function (fn, delay = 300) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    };

    /**
     * Show a programmatic toast notification.
     * @param {string} message — The toast message.
     * @param {string} type — 'success' | 'error' | 'warning' | 'info'
     */
    window.showToast = function (message, type = 'info') {
        let container = document.getElementById('toast-container');

        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const iconMap = {
            success: 'check-circle',
            error: 'x-circle',
            warning: 'alert-triangle',
            info: 'info',
        };

        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.innerHTML = `
            <div class="toast__icon">
                <i data-lucide="${iconMap[type] || 'info'}"></i>
            </div>
            <span class="toast__message">${message}</span>
            <button class="toast__close" onclick="this.parentElement.remove()">
                <i data-lucide="x"></i>
            </button>
        `;

        container.appendChild(toast);

        // Re-init Lucide for new icons
        if (window.lucide) lucide.createIcons();

        // Auto-dismiss
        setTimeout(() => {
            toast.style.animation = 'toast-slide-out 0.3s var(--ease-out) forwards';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };

})();
