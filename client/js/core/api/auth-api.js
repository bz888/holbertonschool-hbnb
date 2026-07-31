import { ApiError, apiRequest } from './client.js';

export async function loginUser(email, password) {
    const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: { email, password },
        errorMessage: () => 'Invalid email or password.'
    });

    if (!data?.access_token) {
        throw new ApiError(
            'Login succeeded, but the server did not return a token.'
        );
    }

    return data.access_token;
}

export async function validateAuthToken(token) {
    await apiRequest('/auth/protected', {
        token,
        networkErrorMessage: 'Unable to verify your session. Please try again.',
        errorMessage: (status) => (
            `Unable to verify your session (${status}).`
        )
    });

    return true;
}
