const API_BASE_URL = 'http://localhost:8080/api/v1';

function getCookie(name) {
    const prefix = `${encodeURIComponent(name)}=`;
    const cookie = document.cookie
        .split(';')
        .map((part) => part.trim())
        .find((part) => part.startsWith(prefix));

    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function storeAuthToken(token) {
    const attributes = [
        `token=${encodeURIComponent(token)}`,
        'path=/',
        'SameSite=Lax'
    ];

    if (window.location.protocol === 'https:') {
        attributes.push('Secure');
    }

    document.cookie = attributes.join('; ');
    return getCookie('token') === token;
}

function checkAuthentication() {
    const token = getCookie('token');
    const isAuthenticated = Boolean(token);

    document.querySelectorAll('.login-button').forEach((loginLink) => {
        loginLink.style.display = isAuthenticated ? 'none' : 'inline-flex';
    });

    document.querySelectorAll('[data-auth-only]').forEach((element) => {
        element.hidden = !isAuthenticated;
    });

    document.querySelectorAll('[data-auth-guest]').forEach((element) => {
        element.hidden = isAuthenticated;
    });

    return token;
}

function getPlaceIdFromURL() {
    const placeId = new URLSearchParams(window.location.search).get('id');
    return placeId ? placeId.trim() : null;
}

async function submitReview(token, placeId, reviewText, rating) {
    let response;

    try {
        response = await fetch(`${API_BASE_URL}/reviews/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: reviewText,
                rating,
                place_id: placeId
            })
        });
    } catch (error) {
        throw new Error('Unable to connect to the server. Please try again.');
    }

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        // Keep the fallback message below when the API response has no JSON body.
    }

    if (!response.ok) {
        throw new Error(
            data.message
            || data.error
            || `Failed to submit review (${response.status}).`
        );
    }

    return data;
}

function showReviewMessage(messageElement, message, isError = false) {
    messageElement.textContent = message;
    messageElement.className = isError ? 'form-error' : 'form-success';
    messageElement.setAttribute('role', isError ? 'alert' : 'status');
    messageElement.hidden = false;
}

async function fetchPlaces(token) {
    const headers = {};

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/places/`, { headers });

    if (!response.ok) {
        throw new Error(`Unable to load places (${response.status}).`);
    }

    const places = await response.json();
    displayPlaces(places);
}

async function fetchPlaceDetails(token, placeId) {
    const headers = {};

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_BASE_URL}/places/${encodeURIComponent(placeId)}`,
        { headers }
    );

    if (!response.ok) {
        throw new Error(`Unable to load place details (${response.status}).`);
    }

    const place = await response.json();
    displayPlaceDetails(place);
}

function formatCoordinate(value) {
    const coordinate = Number(value);
    return Number.isFinite(coordinate) ? coordinate.toFixed(4) : 'Unknown';
}

function displayPlaces(places) {
    const placesList = document.getElementById('places-list');

    if (!placesList) {
        return;
    }

    placesList.innerHTML = '';

    if (!Array.isArray(places) || places.length === 0) {
        const message = document.createElement('p');
        message.className = 'places-message';
        message.textContent = 'No places are currently available.';
        placesList.appendChild(message);
        return;
    }

    places.forEach((place) => {
        const card = document.createElement('article');
        const headingGroup = document.createElement('div');
        const location = document.createElement('p');
        const title = document.createElement('h2');
        const description = document.createElement('p');
        const price = document.createElement('p');
        const priceAmount = document.createElement('strong');
        const detailsLink = document.createElement('a');

        card.className = 'place-card';
        card.dataset.price = String(Number(place.price) || 0);

        location.className = 'card-location';
        location.textContent = `${formatCoordinate(place.latitude)}, ${formatCoordinate(place.longitude)}`;
        title.textContent = place.title || 'Untitled place';
        description.className = 'card-description';
        description.textContent = place.description || 'No description available.';
        headingGroup.append(location, title, description);

        price.className = 'price';
        priceAmount.textContent = `$${Number(place.price).toFixed(2)}`;
        price.append(priceAmount, ' per night');

        detailsLink.className = 'details-button';
        detailsLink.href = `place.html?id=${encodeURIComponent(place.id)}`;
        detailsLink.textContent = 'View Details';

        card.append(headingGroup, price, detailsLink);
        placesList.appendChild(card);
    });

    applyPriceFilter();
}

function displayPlaceDetails(place) {
    const placeDetails = document.getElementById('place-details');
    const reviewsList = document.getElementById('reviews-list');

    if (!placeDetails || !reviewsList) {
        return;
    }

    placeDetails.innerHTML = '';
    reviewsList.innerHTML = '';

    const heading = document.createElement('div');
    const headingText = document.createElement('div');
    const location = document.createElement('p');
    const title = document.createElement('h1');
    const price = document.createElement('p');
    const priceAmount = document.createElement('strong');
    const aboutSection = document.createElement('section');
    const aboutHeading = document.createElement('h2');
    const facts = document.createElement('dl');
    const description = document.createElement('p');
    const amenitiesSection = document.createElement('section');
    const amenitiesHeading = document.createElement('h2');
    const amenitiesList = document.createElement('ul');
    const ownerName = [place.owner?.first_name, place.owner?.last_name]
        .filter(Boolean)
        .join(' ') || 'Unknown';
    const numericPrice = Number(place.price);

    heading.className = 'place-heading';
    location.className = 'eyebrow';
    location.textContent = `${formatCoordinate(place.latitude)}, ${formatCoordinate(place.longitude)}`;
    title.textContent = place.title || 'Untitled place';
    headingText.append(location, title);

    price.className = 'price';
    priceAmount.textContent = Number.isFinite(numericPrice)
        ? `$${numericPrice.toFixed(2)}`
        : 'Price unavailable';
    price.append(priceAmount, ' per night');
    heading.append(headingText, price);

    aboutSection.className = 'place-info';
    aboutSection.setAttribute('aria-labelledby', 'about-heading');
    aboutHeading.id = 'about-heading';
    aboutHeading.textContent = 'About this place';
    facts.className = 'place-facts';

    [
        ['Host', ownerName],
        ['Latitude', formatCoordinate(place.latitude)],
        ['Longitude', formatCoordinate(place.longitude)]
    ].forEach(([label, value]) => {
        const fact = document.createElement('div');
        const term = document.createElement('dt');
        const detail = document.createElement('dd');

        term.textContent = label;
        detail.textContent = value;
        fact.append(term, detail);
        facts.appendChild(fact);
    });

    description.textContent = place.description || 'No description available.';
    aboutSection.append(aboutHeading, facts, description);

    amenitiesSection.className = 'place-info';
    amenitiesSection.setAttribute('aria-labelledby', 'amenities-heading');
    amenitiesHeading.id = 'amenities-heading';
    amenitiesHeading.textContent = 'Amenities';
    amenitiesList.className = 'amenities-list';

    if (Array.isArray(place.amenities) && place.amenities.length > 0) {
        place.amenities.forEach((amenity) => {
            const item = document.createElement('li');
            item.textContent = amenity.name || 'Unnamed amenity';
            amenitiesList.appendChild(item);
        });
    } else {
        const item = document.createElement('li');
        item.textContent = 'No amenities listed.';
        amenitiesList.appendChild(item);
    }

    amenitiesSection.append(amenitiesHeading, amenitiesList);
    placeDetails.append(heading, aboutSection, amenitiesSection);

    const reviews = Array.isArray(place.reviews) ? place.reviews : [];

    if (reviews.length === 0) {
        const message = document.createElement('p');
        message.className = 'places-message';
        message.textContent = 'No reviews yet. Be the first to add one.';
        reviewsList.appendChild(message);
    } else {
        reviews.forEach((review) => {
            const card = document.createElement('article');
            const meta = document.createElement('div');
            const author = document.createElement('h3');
            const rating = document.createElement('p');
            const ratingValue = Math.min(
                5,
                Math.max(0, Math.round(Number(review.rating) || 0))
            );
            const ratingText = document.createElement('span');
            const reviewText = document.createElement('p');

            card.className = 'review-card';
            meta.className = 'review-meta';
            author.textContent = review.user?.first_name || 'Guest';
            rating.className = 'rating';
            rating.setAttribute(
                'aria-label',
                `Rating: ${ratingValue} out of 5`
            );
            rating.append(
                `${'★'.repeat(ratingValue)}${'☆'.repeat(5 - ratingValue)} `
            );
            ratingText.textContent = `${ratingValue}/5`;
            rating.appendChild(ratingText);
            meta.append(author, rating);
            reviewText.textContent = review.text || 'No review text provided.';
            card.append(meta, reviewText);
            reviewsList.appendChild(card);
        });
    }

    const addReviewLink = document.getElementById('add-review-link');

    if (addReviewLink && place.id) {
        addReviewLink.href = `add_review.html?id=${encodeURIComponent(place.id)}`;
    }

    document.title = `HBNB | ${place.title || 'Place Details'}`;
}

function applyPriceFilter() {
    const priceFilter = document.getElementById('price-filter');

    if (!priceFilter) {
        return;
    }

    const maximumPrice = priceFilter.value;
    document.querySelectorAll('#places-list .place-card').forEach((card) => {
        const price = Number(card.dataset.price);
        card.style.display = maximumPrice === 'all' || price <= Number(maximumPrice)
            ? 'flex'
            : 'none';
    });
}

function showPlacesError(error) {
    const content = document.getElementById('places-list')
        || document.getElementById('place-details');

    if (!content) {
        return;
    }

    content.innerHTML = '';
    const message = document.createElement('p');
    message.className = 'places-message form-error';
    message.setAttribute('role', 'alert');
    message.textContent = error.message || 'Unable to load places.';
    content.appendChild(message);

    const reviewsSection = document.getElementById('reviews');

    if (reviewsSection) {
        reviewsSection.hidden = true;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const token = checkAuthentication();

    const reviewForm = document.getElementById('review-form');

    if (reviewForm) {
        if (!token) {
            window.location.href = 'index.html';
            return;
        }

        const placeId = getPlaceIdFromURL();
        const reviewInput = document.getElementById('review');
        const ratingInput = document.getElementById('rating');
        const messageElement = document.getElementById('review-message');
        const submitButton = reviewForm.querySelector('button[type="submit"]');
        const cancelLink = document.getElementById('review-cancel-link');

        if (placeId) {
            cancelLink.href = `place.html?id=${encodeURIComponent(placeId)}`;
        } else {
            showReviewMessage(
                messageElement,
                'No place was selected. Return to the places page and choose a place.',
                true
            );
            submitButton.disabled = true;
        }

        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            messageElement.hidden = true;
            messageElement.textContent = '';

            if (!reviewForm.checkValidity()) {
                reviewForm.reportValidity();
                return;
            }

            const reviewText = reviewInput.value.trim();
            const rating = Number(ratingInput.value);

            if (reviewText.length < 10) {
                showReviewMessage(
                    messageElement,
                    'Your review must be at least 10 characters long.',
                    true
                );
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = 'Submitting…';

            try {
                await submitReview(token, placeId, reviewText, rating);
                reviewForm.reset();
                showReviewMessage(
                    messageElement,
                    'Review submitted successfully! Returning to the place…'
                );
                window.setTimeout(() => {
                    window.location.href = (
                        `place.html?id=${encodeURIComponent(placeId)}`
                    );
                }, 1000);
            } catch (error) {
                showReviewMessage(messageElement, error.message, true);
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Submit Review';
            }
        });
    }

    const priceFilter = document.getElementById('price-filter');

    if (priceFilter) {
        priceFilter.addEventListener('change', applyPriceFilter);
        fetchPlaces(token).catch(showPlacesError);
    }

    const placeDetails = document.getElementById('place-details');

    if (placeDetails) {
        const placeId = getPlaceIdFromURL();

        if (placeId) {
            fetchPlaceDetails(token, placeId).catch(showPlacesError);
        } else {
            showPlacesError(new Error('No place was selected.'));
        }
    }

    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const errorMessage = document.getElementById('login-error');
            const submitButton = loginForm.querySelector('button[type="submit"]');

            errorMessage.hidden = true;
            errorMessage.textContent = '';

            if (!loginForm.checkValidity()) {
                loginForm.reportValidity();
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = 'Logging in…';

            try {
                await loginUser(emailInput.value.trim(), passwordInput.value);
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.hidden = false;
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Login';
            }
        });
    }
});

async function loginUser(email, password) {
    let response;

    try {
        response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
    } catch (error) {
        throw new Error('Unable to connect to the server. Please try again.');
    }

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        // Keep the fallback message below when the API response has no JSON body.
    }

    if (!response.ok) {
        throw new Error(data.message || data.error || 'Invalid email or password.');
    }

    if (!data.access_token) {
        throw new Error('Login succeeded, but the server did not return a token.');
    }

    if (!storeAuthToken(data.access_token)) {
        throw new Error(
            'Login succeeded, but the browser could not store your session. '
            + 'Open HBNB through a local web server instead of directly from a file.'
        );
    }

    window.location.href = 'index.html';
}
