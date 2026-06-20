
```
python3 -m venv venv

pip install -r requirements.txt

python run.py
```

note:
Reviews are associated with places rather than users. A user authors a review for a place using POST /api/v1/places/<place_id>/reviews. Reviews written by a specific user can be retrieved with GET /api/v1/users/<user_id>/reviews. A separate user-review endpoint is unnecessary because the current model does not support users reviewing other users.