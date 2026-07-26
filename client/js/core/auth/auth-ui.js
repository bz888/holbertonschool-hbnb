import { clearAuthToken, getAuthToken } from './session.js';

export function updateAuthenticationUI() {
    const token = getAuthToken();
    const authenticated = Boolean(token);

    document.querySelectorAll('.login-button').forEach((loginLink) => {
        loginLink.style.display = authenticated ? 'none' : 'inline-flex';
    });

    document.querySelectorAll('[data-auth-only]').forEach((element) => {
        element.hidden = !authenticated;
    });

    document.querySelectorAll('[data-auth-guest]').forEach((element) => {
        element.hidden = authenticated;
    });

    return token;
}

function logout() {
    clearAuthToken();
    window.location.href = 'index.html';
}

export function initializeAuthenticationUI() {
    const token = updateAuthenticationUI();

    document.querySelectorAll('.logout-button').forEach((logoutButton) => {
        logoutButton.addEventListener('click', logout);
    });

    return token;
}
