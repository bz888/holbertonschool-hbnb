import { apiRequest } from './client.js';

export async function getPlaces() {
    const places = await apiRequest('/places/', {
        networkErrorMessage: 'Unable to load places.',
        errorMessage: (status) => `Unable to load places (${status}).`
    });

    return Array.isArray(places) ? places : [];
}

export function getPlace(placeId) {
    return apiRequest(`/places/${encodeURIComponent(placeId)}`, {
        networkErrorMessage: 'Unable to load place details.',
        errorMessage: (status) => (
            `Unable to load place details (${status}).`
        )
    });
}

export function createPlace(token, placeData) {
    return apiRequest('/places/', {
        method: 'POST',
        token,
        body: placeData,
        errorMessage: (status) => `Failed to create place (${status}).`
    });
}
