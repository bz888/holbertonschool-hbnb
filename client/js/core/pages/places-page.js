import { getPlaces } from '../api/places-api.js';
import { clearElement } from '../../utils/dom.js';
import { formatCoordinate, formatPrice } from '../../utils/formatters.js';

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

function createPlaceCard(place) {
    const card = document.createElement('article');
    const headingGroup = document.createElement('div');
    const location = document.createElement('p');
    const title = document.createElement('h2');
    const description = document.createElement('p');
    const price = document.createElement('p');
    const priceAmount = document.createElement('strong');
    const detailsLink = document.createElement('a');
    const numericPrice = Number(place.price);

    card.className = 'place-card';
    card.dataset.price = String(Number.isFinite(numericPrice) ? numericPrice : 0);

    location.className = 'card-location';
    location.textContent = (
        `${formatCoordinate(place.latitude)}, `
        + formatCoordinate(place.longitude)
    );
    title.textContent = place.title || 'Untitled place';
    description.className = 'card-description';
    description.textContent = place.description || 'No description available.';
    headingGroup.append(location, title, description);

    price.className = 'price';
    priceAmount.textContent = formatPrice(place.price);
    price.append(priceAmount, ' per night');

    detailsLink.className = 'details-button';
    detailsLink.href = `place.html?id=${encodeURIComponent(place.id)}`;
    detailsLink.textContent = 'View Details';

    card.append(headingGroup, price, detailsLink);
    return card;
}

function renderPlaces(places) {
    const placesList = document.getElementById('places-list');
    clearElement(placesList);

    if (places.length === 0) {
        const message = document.createElement('p');
        message.className = 'places-message';
        message.textContent = 'No places are currently available.';
        placesList.appendChild(message);
        return;
    }

    places.forEach((place) => {
        placesList.appendChild(createPlaceCard(place));
    });

    applyPriceFilter();
}

function showPlacesError(error) {
    const placesList = document.getElementById('places-list');
    clearElement(placesList);

    const message = document.createElement('p');
    message.className = 'places-message form-error';
    message.setAttribute('role', 'alert');
    message.textContent = error.message || 'Unable to load places.';
    placesList.appendChild(message);
}

export async function initPlacesPage() {
    const priceFilter = document.getElementById('price-filter');
    priceFilter.addEventListener('change', applyPriceFilter);

    try {
        renderPlaces(await getPlaces());
    } catch (error) {
        showPlacesError(error);
    }
}
