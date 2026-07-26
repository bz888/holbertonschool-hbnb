INSERT IGNORE INTO users (
    id, first_name, last_name, email, password, is_admin, is_active,
    created_at, updated_at
)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$AdO2/YbtDgxEARD2tX5Ijef6FvC7qHFK3KHX1Ll3tEbKwmjj5Uq8u',
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

INSERT IGNORE INTO amenities (id, name, created_at, updated_at) VALUES
    ('83edfd03-9d03-4ac0-b9d0-9deb78d43faa', 'WiFi', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('e383daec-5a0d-4ff2-93ca-07e1120acc19', 'Swimming Pool', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('39b9a3d1-0a2f-4a5c-b334-5d26473235b2', 'Air Conditioning', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
