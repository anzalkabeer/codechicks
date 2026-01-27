/**
 * CodeChicks Authentication Module
 * 
 * ⚠️ MOCKUP: This is a temporary implementation for testing.
 * 
 * Include this script on any protected page to enforce authentication.
 * It runs immediately on page load and redirects to login if no token found.
 */

(function () {
    'use strict';

    const TOKEN_KEY = 'access_token';
    const LOGIN_URL = '/';

    /**
     * Check if user is authenticated.
     * Redirects to login if no token found.
     */
    function requireAuth() {
        const token = localStorage.getItem(TOKEN_KEY);
        if (!token) {
            console.warn('[Auth] No token found, redirecting to login');
            window.location.href = LOGIN_URL;
            return false;
        }
        return true;
    }

    /**
     * Get authorization headers for API calls.
     * @returns {Object} Headers object with Authorization bearer token
     */
    window.getAuthHeaders = function () {
        const token = localStorage.getItem(TOKEN_KEY);
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    };

    /**
     * Make an authenticated API request.
     * Automatically handles 401 responses by redirecting to login.
     * @param {string} url - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Response data
     */
    window.authFetch = async function (url, options = {}) {
        const headers = window.getAuthHeaders();
        const response = await fetch(url, {
            ...options,
            headers: { ...headers, ...options.headers }
        });

        if (response.status === 401) {
            console.warn('[Auth] Token expired or invalid, redirecting to login');
            localStorage.removeItem(TOKEN_KEY);
            window.location.href = LOGIN_URL;
            return null;
        }

        return response;
    };

    /**
     * Log out the current user.
     * Clears token and redirects to login.
     */
    window.logout = function () {
        localStorage.removeItem(TOKEN_KEY);
        window.location.href = LOGIN_URL;
    };

    /**
     * Get current user info from /auth/me endpoint.
     * @returns {Promise<Object|null>} User object or null if failed
     */
    window.getCurrentUser = async function () {
        try {
            const response = await window.authFetch('/auth/me');
            if (response && response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('[Auth] Failed to get current user:', error);
        }
        return null;
    };

    // Run auth check immediately
    requireAuth();
})();
