document.addEventListener('DOMContentLoaded', () => {
    const cookieNames = document.cookie.split(';').map((cookie) => cookie.trim().split('=')[0]);
    const isAuthenticated = Boolean(
        localStorage.getItem('token')
        || localStorage.getItem('authToken')
        || cookieNames.includes('token')
        || cookieNames.includes('authToken')
    );

    document.querySelectorAll('[data-auth-only]').forEach((element) => {
        element.hidden = !isAuthenticated;
    });

    document.querySelectorAll('[data-auth-guest]').forEach((element) => {
        element.hidden = isAuthenticated;
    });

    const priceFilter = document.getElementById('price-filter');

    if (priceFilter) {
        priceFilter.addEventListener('change', () => {
            const maximumPrice = priceFilter.value;
            const placeCards = document.querySelectorAll('.place-card');

            placeCards.forEach((card) => {
                const price = Number(card.dataset.price);
                card.hidden = maximumPrice !== 'all' && price > Number(maximumPrice);
            });
        });
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
        response = await fetch('http://localhost:8080/api/v1/auth/login', {
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
