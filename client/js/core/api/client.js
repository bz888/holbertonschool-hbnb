import { API_BASE_URL } from '../../config.js';

export class ApiError extends Error {
    constructor(message, { status = null, data = null, cause = null } = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
        this.cause = cause;
    }
}

export class AuthenticationError extends ApiError {
    constructor(options = {}) {
        super(
            'Your session has expired or is invalid. Please log in again.',
            options
        );
        this.name = 'AuthenticationError';
    }
}

function getResponseErrorMessage(data, status, errorMessage) {
    if (data?.message || data?.error) {
        return data.message || data.error;
    }

    return typeof errorMessage === 'function'
        ? errorMessage(status)
        : errorMessage;
}

export async function apiRequest(
    path,
    {
        method = 'GET',
        token,
        body,
        headers = {},
        networkErrorMessage = 'Unable to connect to the server. Please try again.',
        errorMessage = (status) => `Request failed (${status}).`
    } = {}
) {
    const requestHeaders = { ...headers };

    if (token) {
        requestHeaders.Authorization = `Bearer ${token}`;
    }

    if (body !== undefined) {
        requestHeaders['Content-Type'] = 'application/json';
    }

    let response;

    try {
        response = await fetch(`${API_BASE_URL}${path}`, {
            method,
            headers: requestHeaders,
            body: body === undefined ? undefined : JSON.stringify(body)
        });
    } catch (cause) {
        throw new ApiError(networkErrorMessage, { cause });
    }

    let data = null;

    try {
        data = await response.json();
    } catch (error) {
        // Some successful or failed responses may not include a JSON body.
    }

    if (!response.ok) {
        if (token && (response.status === 401 || response.status === 422)) {
            throw new AuthenticationError({
                status: response.status,
                data
            });
        }

        throw new ApiError(
            getResponseErrorMessage(data, response.status, errorMessage),
            { status: response.status, data }
        );
    }

    return data;
}
