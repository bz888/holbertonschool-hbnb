/*
  HBnB client — scripts.js
  Handles: login, places list + filtering, place details, add review.
  Talks to the Flask API at API_BASE_URL.
*/

const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

/* ---------------------------------------------------------------- */
/* Cookie helpers                                                    */
/* ---------------------------------------------------------------- */

function setCookie(name, value, days) {
    let expires = '';
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
        expires = `; expires=${date.toUTCString()}`;
    }
    document.cookie = `${name}=${value}${expires}; path=/`;
}

function getCookie(name) {
    const match = document.cookie.match(
        new RegExp('(^| )' + name + '=([^;]+)')
    );
    return match ? match[2] : null;
}

/* ---------------------------------------------------------------- */
/* Shared: login link visibility                                     */
/* ---------------------------------------------------------------- */

function updateLoginLink() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    if (!loginLink) return;

    if (token) {
        loginLink.style.display = 'none';
    } else {
        loginLink.style.display = 'block';
    }
}

/* ---------------------------------------------------------------- */
/* Login page                                                        */
/* ---------------------------------------------------------------- */

function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('login-error');
        if (errorEl) errorEl.textContent = '';

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                const data = await response.json();
                setCookie('token', data.access_token, 1);
                window.location.href = 'index.html';
            } else {
                const data = await response.json().catch(() => ({}));
                const message = data.error || 'Invalid email or password.';
                if (errorEl) {
                    errorEl.textContent = message;
                } else {
                    alert(`Login failed: ${message}`);
                }
            }
        } catch (err) {
            if (errorEl) {
                errorEl.textContent = 'Could not reach the server. Please try again.';
            }
        }
    });
}

/* ---------------------------------------------------------------- */
/* Index page — places list + price filter                           */
/* ---------------------------------------------------------------- */

let allPlaces = [];

function setupIndexPage() {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;

    fetchPlaces();
    setupPriceFilter();
}

async function fetchPlaces() {
    const token = getCookie('token');
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
        const response = await fetch(`${API_BASE_URL}/places/`, { headers });
        if (response.ok) {
            allPlaces = await response.json();
            displayPlaces(allPlaces);
        } else {
            console.error('Failed to fetch places:', response.statusText);
        }
    } catch (err) {
        console.error('Error fetching places:', err);
    }
}

function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = '';

    places.forEach((place) => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.dataset.price = place.price;

        card.innerHTML = `
            <h3>${place.title}</h3>
            <p class="price">$${place.price} / night</p>
            <a href="place.html?place_id=${place.id}" class="details-button">View Details</a>
        `;

        placesList.appendChild(card);
    });
}

function setupPriceFilter() {
    const priceFilter = document.getElementById('price-filter');
    if (!priceFilter) return;

    const options = ['10', '50', '100', 'All'];
    options.forEach((value) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value === 'All' ? 'All' : `$${value}`;
        priceFilter.appendChild(option);
    });
    priceFilter.value = 'All';

    priceFilter.addEventListener('change', (event) => {
        const selected = event.target.value;
        const cards = document.querySelectorAll('.place-card');

        cards.forEach((card) => {
            const price = parseFloat(card.dataset.price);
            if (selected === 'All' || price <= parseFloat(selected)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

/* ---------------------------------------------------------------- */
/* Place details page                                                */
/* ---------------------------------------------------------------- */

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('place_id');
}

function setupPlacePage() {
    const placeDetails = document.getElementById('place-details');
    if (!placeDetails) return;

    const placeId = getPlaceIdFromURL();
    const token = getCookie('token');
    const addReviewSection = document.getElementById('add-review');
    const addReviewLink = document.getElementById('add-review-link');

    if (addReviewLink && placeId) {
        addReviewLink.href = `add_review.html?place_id=${placeId}`;
    }

    if (!token) {
        if (addReviewSection) addReviewSection.style.display = 'none';
    } else {
        if (addReviewSection) addReviewSection.style.display = 'block';
    }

    if (placeId) {
        fetchPlaceDetails(token, placeId);
    }
}

async function fetchPlaceDetails(token, placeId) {
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
        const response = await fetch(`${API_BASE_URL}/places/${placeId}`, { headers });
        if (response.ok) {
            const place = await response.json();
            displayPlaceDetails(place);
            displayReviews(place.reviews || []);
        } else {
            document.getElementById('place-details').innerHTML =
                '<p>This place could not be found.</p>';
        }
    } catch (err) {
        console.error('Error fetching place details:', err);
    }
}

function displayPlaceDetails(place) {
    const container = document.getElementById('place-details');
    container.innerHTML = '';

    const info = document.createElement('div');
    info.className = 'place-info';

    const owner = place.owner
        ? `${place.owner.first_name} ${place.owner.last_name}`
        : 'Unknown host';

    const amenitiesList = (place.amenities || [])
        .map((amenity) => `<li>${amenity.name}</li>`)
        .join('');

    info.innerHTML = `
        <h1>${place.title}</h1>
        <p class="host">Hosted by ${owner}</p>
        <p class="price">$${place.price} / night</p>
        <p class="description">${place.description || ''}</p>
        <div class="amenities">
            <h2>Amenities</h2>
            <ul>${amenitiesList || '<li>No amenities listed</li>'}</ul>
        </div>
    `;

    container.appendChild(info);
}

async function displayReviews(reviews) {
    const reviewsSection = document.getElementById('reviews');
    if (!reviewsSection) return;

    // Clear previous review cards but keep the heading
    reviewsSection.querySelectorAll('.review-card').forEach((el) => el.remove());

    if (reviews.length === 0) {
        const empty = document.createElement('p');
        empty.textContent = 'No reviews yet.';
        empty.className = 'no-reviews';
        reviewsSection.appendChild(empty);
        return;
    }

    const userNameCache = {};

    for (const review of reviews) {
        let userName = userNameCache[review.user_id];
        if (!userName) {
            userName = await fetchUserName(review.user_id);
            userNameCache[review.user_id] = userName;
        }

        const card = document.createElement('div');
        card.className = 'review-card';
        card.innerHTML = `
            <p class="review-comment">${review.text}</p>
            <p class="review-user">${userName}</p>
            <p class="review-rating">Rating: ${review.rating} / 5</p>
        `;
        reviewsSection.appendChild(card);
    }
}

async function fetchUserName(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`);
        if (response.ok) {
            const user = await response.json();
            return `${user.first_name} ${user.last_name}`;
        }
    } catch (err) {
        console.error('Error fetching user:', err);
    }
    return 'Anonymous';
}

/* ---------------------------------------------------------------- */
/* Add review page                                                   */
/* ---------------------------------------------------------------- */

function setupAddReviewPage() {
    const reviewForm = document.getElementById('review-form');
    const placeNameEl = document.getElementById('review-place-name');
    // Only run this page's logic when there is no place-details section
    // (this distinguishes add_review.html from place.html's own form).
    if (!reviewForm || document.getElementById('place-details')) return;

    const token = getCookie('token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    const placeId = getPlaceIdFromURL();
    if (!placeId) {
        window.location.href = 'index.html';
        return;
    }

    if (placeNameEl) {
        fetch(`${API_BASE_URL}/places/${placeId}`)
            .then((res) => (res.ok ? res.json() : null))
            .then((place) => {
                if (place) placeNameEl.textContent = `Reviewing: ${place.title}`;
            })
            .catch(() => {});
    }

    const ratingSelect = document.getElementById('rating');
    if (ratingSelect && ratingSelect.options.length === 0) {
        for (let i = 5; i >= 1; i -= 1) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = i;
            ratingSelect.appendChild(option);
        }
    }

    reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const reviewText = document.getElementById('review').value;
        const rating = parseInt(document.getElementById('rating').value, 10);

        const result = await submitReview(token, placeId, reviewText, rating);
        handleReviewResponse(result, reviewForm);
    });
}

async function submitReview(token, placeId, reviewText, rating) {
    try {
        const response = await fetch(`${API_BASE_URL}/places/${placeId}/reviews`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ text: reviewText, rating })
        });
        const data = await response.json().catch(() => ({}));
        return { ok: response.ok, data };
    } catch (err) {
        return { ok: false, data: { error: 'Could not reach the server.' } };
    }
}

function handleReviewResponse(result, form) {
    const messageEl = document.getElementById('review-message');

    if (result.ok) {
        if (messageEl) {
            messageEl.textContent = 'Review submitted successfully!';
            messageEl.className = 'message-success';
        }
        form.reset();
    } else {
        const message = result.data.error || 'Failed to submit review.';
        if (messageEl) {
            messageEl.textContent = message;
            messageEl.className = 'message-error';
        } else {
            alert(`Failed to submit review: ${message}`);
        }
    }
}

/* ---------------------------------------------------------------- */
/* Bootstrap                                                          */
/* ---------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
    updateLoginLink();
    setupLoginForm();
    setupIndexPage();
    setupPlacePage();
    setupAddReviewPage();
});