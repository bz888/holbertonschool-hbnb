import { deleteCookie, getCookie, setCookie } from '../../utils/cookies.js';

const TOKEN_COOKIE = 'token';

export function getAuthToken() {
    return getCookie(TOKEN_COOKIE);
}

export function storeAuthToken(token) {
    setCookie(TOKEN_COOKIE, token);
    return getAuthToken() === token;
}

export function clearAuthToken() {
    deleteCookie(TOKEN_COOKIE);
}

export function isAuthenticated() {
    return Boolean(getAuthToken());
}
