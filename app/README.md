## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Review Design

Reviews are written by users about places:

```http
POST /api/v1/places/<place_id>/reviews
GET /api/v1/users/<user_id>/reviews
```

Users do not review other users in the current model.

Users and places use `is_active` for soft deletion, preserving their existing reviews.

`POST /api/v1/reviews/` is included for task compliance, although the place-based POST route represents the relationship more clearly.
