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
});
