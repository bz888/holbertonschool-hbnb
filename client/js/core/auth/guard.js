import { AuthenticationError } from '../api/client.js';
import {
    getCurrentPageDestination,
    getQueryParameter,
    getSafeLocalDestination
} from '../../utils/url.js';
import { clearAuthToken, getAuthToken } from './session.js';

export function getSafeLoginDestination() {
    return getSafeLocalDestination(
        getQueryParameter('next'),
        'index.html'
    );
}

export function redirectToLogin(
    destination = getCurrentPageDestination()
) {
    window.location.href = (
        `login.html?next=${encodeURIComponent(destination)}`
    );
}

export function requireAuthentication(
    destination = getCurrentPageDestination()
) {
    const token = getAuthToken();

    if (!token) {
        redirectToLogin(destination);
        return null;
    }

    return token;
}

export function handleAuthenticationError(
    error,
    destination = getCurrentPageDestination()
) {
    if (!(error instanceof AuthenticationError)) {
        return false;
    }

    clearAuthToken();
    redirectToLogin(destination);
    return true;
}
