const API_BASE_URL = 'http://localhost:8080/api/v1';

function getCookie(name) {
    const prefix = `${encodeURIComponent(name)}=`;
    const cookie = document.cookie
        .split(';')
        .map((part) => part.trim())
        .find((part) => part.startsWith(prefix));

    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (loginLink) {
        loginLink.style.display = token ? 'none' : 'inline-flex';
    }

    return token;
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
    const placesList = document.getElementById('places-list');

    if (!placesList) {
        return;
    }

    placesList.innerHTML = '';
    const message = document.createElement('p');
    message.className = 'places-message form-error';
    message.setAttribute('role', 'alert');
    message.textContent = error.message || 'Unable to load places.';
    placesList.appendChild(message);
}

document.addEventListener('DOMContentLoaded', () => {
    const token = checkAuthentication();
    const isAuthenticated = Boolean(token);

    document.querySelectorAll('[data-auth-only]').forEach((element) => {
        element.hidden = !isAuthenticated;
    });

    document.querySelectorAll('[data-auth-guest]').forEach((element) => {
        element.hidden = isAuthenticated;
    });

    const priceFilter = document.getElementById('price-filter');

    if (priceFilter) {
        priceFilter.addEventListener('change', applyPriceFilter);
        fetchPlaces(token).catch(showPlacesError);
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

    document.cookie = `token=${encodeURIComponent(data.access_token)}; path=/; SameSite=Lax`;
    window.location.href = 'index.html';
}
