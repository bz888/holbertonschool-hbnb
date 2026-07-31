import { apiRequest } from './client.js';

export async function getAmenities() {
    const amenities = await apiRequest('/amenities/', {
        networkErrorMessage: 'Unable to load amenities.',
        errorMessage: (status) => `Unable to load amenities (${status}).`
    });

    return Array.isArray(amenities) ? amenities : [];
}
