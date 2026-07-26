import { getAmenities } from '../api/amenities-api.js';
import { validateAuthToken } from '../api/auth-api.js';
import { createPlace } from '../api/places-api.js';
import {
    handleAuthenticationError,
    requireAuthentication
} from '../auth/guard.js';
import {
    clearElement,
    clearMessage,
    setButtonState,
    showFormMessage
} from '../../utils/dom.js';

function renderAmenityOptions(amenities) {
    const container = document.getElementById('amenities-options');
    clearElement(container);

    if (amenities.length === 0) {
        const message = document.createElement('p');
        message.className = 'form-hint';
        message.textContent = 'No amenities are currently available.';
        container.appendChild(message);
        return;
    }

    amenities.forEach((amenity) => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        const name = document.createElement('span');

        label.className = 'checkbox-option';
        checkbox.type = 'checkbox';
        checkbox.name = 'amenity_ids';
        checkbox.value = amenity.id;
        name.textContent = amenity.name || 'Unnamed amenity';
        label.append(checkbox, name);
        container.appendChild(label);
    });
}

function showAmenityLoadError(error) {
    const container = document.getElementById('amenities-options');
    clearElement(container);

    const message = document.createElement('p');
    message.className = 'form-hint';
    message.setAttribute('role', 'status');
    message.textContent = (
        `${error.message} You can still create the place without amenities.`
    );
    container.appendChild(message);
}

function collectPlaceData(form) {
    const amenityIds = Array.from(
        form.querySelectorAll('input[name="amenity_ids"]:checked')
    ).map((checkbox) => checkbox.value);

    return {
        title: document.getElementById('title').value.trim(),
        description: document.getElementById('description').value.trim(),
        price: Number(document.getElementById('price').value),
        latitude: Number(document.getElementById('latitude').value),
        longitude: Number(document.getElementById('longitude').value),
        amenity_ids: amenityIds
    };
}

function attachPlaceFormHandler(form, token) {
    const messageElement = document.getElementById('place-message');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearMessage(messageElement);

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        setButtonState(submitButton, true, 'Creating…');

        try {
            const place = await createPlace(token, collectPlaceData(form));
            form.reset();
            showFormMessage(
                messageElement,
                'Place created successfully! Opening its details…'
            );
            window.setTimeout(() => {
                window.location.href = (
                    `place.html?id=${encodeURIComponent(place.id)}`
                );
            }, 1000);
        } catch (error) {
            if (!handleAuthenticationError(error)) {
                showFormMessage(messageElement, error.message, true);
            }
        } finally {
            setButtonState(submitButton, false, 'Create Place');
        }
    });
}

export async function initAddPlacePage() {
    const token = requireAuthentication('add_place.html');

    if (!token) {
        return;
    }

    const form = document.getElementById('place-form');
    const messageElement = document.getElementById('place-message');
    const submitButton = form.querySelector('button[type="submit"]');
    attachPlaceFormHandler(form, token);
    setButtonState(submitButton, true, 'Checking session…');

    try {
        await validateAuthToken(token);
    } catch (error) {
        if (!handleAuthenticationError(error, 'add_place.html')) {
            showFormMessage(messageElement, error.message, true);
            setButtonState(submitButton, true, 'Create Place');
        }
        return;
    }

    setButtonState(submitButton, false, 'Create Place');

    try {
        renderAmenityOptions(await getAmenities());
    } catch (error) {
        showAmenityLoadError(error);
    }
}
