import { createReview } from '../api/reviews-api.js';
import {
    handleAuthenticationError,
    requireAuthentication
} from '../auth/guard.js';
import {
    clearMessage,
    setButtonState,
    showFormMessage
} from '../../utils/dom.js';
import { getQueryParameter } from '../../utils/url.js';

function configureCancelLink(placeId) {
    if (placeId) {
        document.getElementById('review-cancel-link').href = (
            `place.html?id=${encodeURIComponent(placeId)}`
        );
    }
}

function attachReviewFormHandler(form, token, placeId) {
    const reviewInput = document.getElementById('review');
    const ratingInput = document.getElementById('rating');
    const messageElement = document.getElementById('review-message');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearMessage(messageElement);

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const reviewText = reviewInput.value.trim();
        const rating = Number(ratingInput.value);

        if (reviewText.length < 10) {
            showFormMessage(
                messageElement,
                'Your review must be at least 10 characters long.',
                true
            );
            return;
        }

        setButtonState(submitButton, true, 'Submitting…');

        try {
            await createReview(token, placeId, reviewText, rating);
            form.reset();
            showFormMessage(
                messageElement,
                'Review submitted successfully! Returning to the place…'
            );
            window.setTimeout(() => {
                window.location.href = (
                    `place.html?id=${encodeURIComponent(placeId)}`
                );
            }, 1000);
        } catch (error) {
            if (!handleAuthenticationError(error)) {
                showFormMessage(messageElement, error.message, true);
            }
        } finally {
            setButtonState(submitButton, false, 'Submit Review');
        }
    });
}

export function initAddReviewPage() {
    const token = requireAuthentication();

    if (!token) {
        return;
    }

    const form = document.getElementById('review-form');
    const placeId = getQueryParameter('id')?.trim();
    const messageElement = document.getElementById('review-message');
    const submitButton = form.querySelector('button[type="submit"]');
    configureCancelLink(placeId);

    if (!placeId) {
        showFormMessage(
            messageElement,
            'No place was selected. Return to the places page and choose a place.',
            true
        );
        submitButton.disabled = true;
    }

    attachReviewFormHandler(form, token, placeId);
}
