# HBnB - Part 4: Simple Web Client

Front-end client for the HBnB application. It's a static HTML/CSS/JavaScript
(ES6) site that talks to the Flask REST API built in Parts 2-3, using the
Fetch API for all data and `fetch`-based JWT auth stored in a cookie.

## Structure

```
part4/
├── index.html        # List of places (Task 3)
├── login.html         # Login form (Task 2)
├── place.html          # Place details + reviews (Task 4)
├── add_review.html      # Add review form (Task 5)
├── scripts.js             # All client-side logic
├── styles.css               # Shared styles for every page
└── images/
    ├── logo.png
    ├── icon.png
    ├── icon_bath.png
    ├── icon_bed.png
    └── icon_wifi.png
```

## Pages

| Page              | Purpose                                                                 |
|-------------------|--------------------------------------------------------------------------|
| `index.html`      | Lists all places as cards, with a client-side max-price filter (10/50/100/All). Login link hides once a JWT cookie is present. |
| `login.html`      | Email/password form. Posts to `/api/v1/auth/login`, stores the returned `access_token` in a `token` cookie, redirects to `index.html`. |
| `place.html`      | Shows one place's details (host, price, description, amenities) and its reviews. "Add a Review" link only shows when logged in. |
| `add_review.html` | Review submission form. Redirects to `index.html` if there's no `token` cookie. Posts to `/api/v1/places/<place_id>/reviews`. |

## How it works

- **Auth**: `login.html` stores the JWT in a `token` cookie (`document.cookie`).
  Every page checks that cookie with `getCookie('token')` to decide what to
  show and whether to attach an `Authorization: Bearer <token>` header.
- **Data fetching**: all API calls use `fetch()` against the endpoints in the
  Part 2/3 API (`/api/v1/auth/login`, `/api/v1/places/`,
  `/api/v1/places/<id>`, `/api/v1/places/<id>/reviews`, `/api/v1/users/<id>`).
- **Filtering**: the price filter on `index.html` is purely client-side —
  places are fetched once and re-shown/hidden by comparing `data-price` on
  each card, no extra API calls.
- **Reviewer names**: the review API only returns `user_id`, so `place.html`
  makes one extra `GET /api/v1/users/<id>` per unique reviewer (cached per
  page load) to show a name on each review card.

## Configuration

At the top of `scripts.js`:

```javascript
const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';
```

Update this to match wherever your Flask API is actually running.

## Running it

This is a static site — no build step. Options:

- Open the HTML files directly in a browser, or
- Serve the folder locally, e.g. `python3 -m http.server 8000` from inside
  `part4/`, then visit `http://localhost:8000/index.html`.

Either way, the Flask API must be running and reachable at `API_BASE_URL`.

## Backend requirement: CORS

The client and API run on different origins during local development, so the
Flask API needs CORS enabled or requests will be blocked by the browser.

Add `flask-cors` to the API's `requirements.txt`, then in `app/__init__.py`:

```python
from flask_cors import CORS

CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## Design notes

- Header includes the logo (`class="logo"`) and a login link/button
  (`class="login-button"`).
- Footer includes a rights-reserved notice on every page.
- Place and review cards use `place-card` / `review-card` with a `20px`
  margin, `10px` padding, `1px solid #ddd` border, and `10px` border radius,
  per the design spec.
- Forms use the shared `.form` styling (`login-form`, `review-form`).
