import { apiRequest } from './client.js';

export function createReview(token, placeId, reviewText, rating) {
    return apiRequest('/reviews/', {
        method: 'POST',
        token,
        body: {
            text: reviewText,
            rating,
            place_id: placeId
        },
        errorMessage: (status) => `Failed to submit review (${status}).`
    });
}
