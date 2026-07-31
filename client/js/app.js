import { initializeAuthenticationUI } from './core/auth/auth-ui.js';
import { initAddPlacePage } from './core/pages/add-place-page.js';
import { initAddReviewPage } from './core/pages/add-review-page.js';
import { initLoginPage } from './core/pages/login-page.js';
import { initPlaceDetailsPage } from './core/pages/place-details-page.js';
import { initPlacesPage } from './core/pages/places-page.js';

const pageInitializers = {
    'add-place': initAddPlacePage,
    'add-review': initAddReviewPage,
    login: initLoginPage,
    'place-details': initPlaceDetailsPage,
    places: initPlacesPage
};

async function initializeApp() {
    initializeAuthenticationUI();

    const initializePage = pageInitializers[document.body.dataset.page];

    if (initializePage) {
        await initializePage();
    }
}

initializeApp().catch((error) => {
    console.error('Unable to initialize the page.', error);
});
