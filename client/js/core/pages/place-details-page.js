import { getPlace } from '../api/places-api.js';
import { clearElement } from '../../utils/dom.js';
import {
    formatCoordinate,
    formatPrice,
    normalizeRating
} from '../../utils/formatters.js';
import { getQueryParameter } from '../../utils/url.js';

function createPlaceHeading(place) {
    const heading = document.createElement('div');
    const headingText = document.createElement('div');
    const location = document.createElement('p');
    const title = document.createElement('h1');
    const price = document.createElement('p');
    const priceAmount = document.createElement('strong');

    heading.className = 'place-heading';
    location.className = 'eyebrow';
    location.textContent = (
        `${formatCoordinate(place.latitude)}, `
        + formatCoordinate(place.longitude)
    );
    title.textContent = place.title || 'Untitled place';
    headingText.append(location, title);

    price.className = 'price';
    priceAmount.textContent = formatPrice(place.price);
    price.append(priceAmount, ' per night');
    heading.append(headingText, price);

    return heading;
}

function createPlaceFact(label, value) {
    const fact = document.createElement('div');
    const term = document.createElement('dt');
    const detail = document.createElement('dd');

    term.textContent = label;
    detail.textContent = value;
    fact.append(term, detail);
    return fact;
}

function createAboutSection(place) {
    const section = document.createElement('section');
    const heading = document.createElement('h2');
    const facts = document.createElement('dl');
    const description = document.createElement('p');
    const ownerName = [place.owner?.first_name, place.owner?.last_name]
        .filter(Boolean)
        .join(' ') || 'Unknown';

    section.className = 'place-info';
    section.setAttribute('aria-labelledby', 'about-heading');
    heading.id = 'about-heading';
    heading.textContent = 'About this place';
    facts.className = 'place-facts';
    facts.append(
        createPlaceFact('Host', ownerName),
        createPlaceFact('Latitude', formatCoordinate(place.latitude)),
        createPlaceFact('Longitude', formatCoordinate(place.longitude))
    );
    description.textContent = place.description || 'No description available.';
    section.append(heading, facts, description);

    return section;
}

function createAmenitiesSection(amenities) {
    const section = document.createElement('section');
    const heading = document.createElement('h2');
    const list = document.createElement('ul');
    const availableAmenities = Array.isArray(amenities) ? amenities : [];

    section.className = 'place-info';
    section.setAttribute('aria-labelledby', 'amenities-heading');
    heading.id = 'amenities-heading';
    heading.textContent = 'Amenities';
    list.className = 'amenities-list';

    if (availableAmenities.length === 0) {
        const item = document.createElement('li');
        item.textContent = 'No amenities listed.';
        list.appendChild(item);
    } else {
        availableAmenities.forEach((amenity) => {
            const item = document.createElement('li');
            item.textContent = amenity.name || 'Unnamed amenity';
            list.appendChild(item);
        });
    }

    section.append(heading, list);
    return section;
}

function createReviewCard(review) {
    const card = document.createElement('article');
    const meta = document.createElement('div');
    const author = document.createElement('h3');
    const rating = document.createElement('p');
    const ratingValue = normalizeRating(review.rating);
    const ratingText = document.createElement('span');
    const reviewText = document.createElement('p');

    card.className = 'review-card';
    meta.className = 'review-meta';
    author.textContent = review.user?.first_name || 'Guest';
    rating.className = 'rating';
    rating.setAttribute('aria-label', `Rating: ${ratingValue} out of 5`);
    rating.append(`${'★'.repeat(ratingValue)}${'☆'.repeat(5 - ratingValue)} `);
    ratingText.textContent = `${ratingValue}/5`;
    rating.appendChild(ratingText);
    meta.append(author, rating);
    reviewText.textContent = review.text || 'No review text provided.';
    card.append(meta, reviewText);

    return card;
}

function renderReviews(reviews) {
    const reviewsList = document.getElementById('reviews-list');
    const availableReviews = Array.isArray(reviews) ? reviews : [];
    clearElement(reviewsList);

    if (availableReviews.length === 0) {
        const message = document.createElement('p');
        message.className = 'places-message';
        message.textContent = 'No reviews yet. Be the first to add one.';
        reviewsList.appendChild(message);
        return;
    }

    availableReviews.forEach((review) => {
        reviewsList.appendChild(createReviewCard(review));
    });
}

function renderPlaceDetails(place) {
    const placeDetails = document.getElementById('place-details');
    clearElement(placeDetails);
    placeDetails.append(
        createPlaceHeading(place),
        createAboutSection(place),
        createAmenitiesSection(place.amenities)
    );

    renderReviews(place.reviews);

    const addReviewLink = document.getElementById('add-review-link');
    if (place.id) {
        addReviewLink.href = (
            `add_review.html?id=${encodeURIComponent(place.id)}`
        );
    }

    document.title = `HBNB | ${place.title || 'Place Details'}`;
}

function showPlaceDetailsError(error) {
    const placeDetails = document.getElementById('place-details');
    clearElement(placeDetails);

    const message = document.createElement('p');
    message.className = 'places-message form-error';
    message.setAttribute('role', 'alert');
    message.textContent = error.message || 'Unable to load place details.';
    placeDetails.appendChild(message);

    document.getElementById('reviews').hidden = true;
}

export async function initPlaceDetailsPage() {
    const placeId = getQueryParameter('id')?.trim();

    if (!placeId) {
        showPlaceDetailsError(new Error('No place was selected.'));
        return;
    }

    try {
        renderPlaceDetails(await getPlace(placeId));
    } catch (error) {
        showPlaceDetailsError(error);
    }
}
