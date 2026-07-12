-- 2-seed.sql
-- Initial data for the HBnB database. Run after 1-schema.sql.

-- Fixed administrator account.
-- Password hash below is bcrypt('admin1234'); never store the
-- plaintext password in this script.
INSERT INTO users (id, first_name, last_name, email, password, is_admin)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$AdO2/YbtDgxEARD2tX5Ijef6FvC7qHFK3KHX1Ll3tEbKwmjj5Uq8u',
    TRUE
);

-- Initial amenities (UUID4 ids).
INSERT INTO amenities (id, name) VALUES
    ('83edfd03-9d03-4ac0-b9d0-9deb78d43faa', 'WiFi'),
    ('e383daec-5a0d-4ff2-93ca-07e1120acc19', 'Swimming Pool'),
    ('39b9a3d1-0a2f-4a5c-b334-5d26473235b2', 'Air Conditioning');