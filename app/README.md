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

Users can also be permanently deleted. Hard deletion currently leaves existing reviews and places holding their in-memory user reference; soft deletion or anonymization should be preferred when those relationships must remain valid.

```http
DELETE /api/v1/users/<user_id>/soft-delete
DELETE /api/v1/users/<user_id>
```

`POST /api/v1/reviews/` is included for task compliance, although the place-based POST route represents the relationship more clearly.
