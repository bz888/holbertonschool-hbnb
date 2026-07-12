DROP TABLE IF EXISTS place_amenity;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS amenities;
DROP TABLE IF EXISTS users;

-- ---------------------------------------------------------------
-- users
-- ---------------------------------------------------------------
CREATE TABLE users (
    id          CHAR(36)     NOT NULL,
    first_name  VARCHAR(255) NOT NULL,
    last_name   VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    password    VARCHAR(255) NOT NULL,
    is_admin    BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                             ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email)
);

-- ---------------------------------------------------------------
-- places
-- ---------------------------------------------------------------
CREATE TABLE places (
    id          CHAR(36)       NOT NULL,
    title       VARCHAR(255)   NOT NULL,
    description TEXT,
    price       DECIMAL(10,2)  NOT NULL,
    latitude    FLOAT          NOT NULL,
    longitude   FLOAT          NOT NULL,
    owner_id    CHAR(36)       NOT NULL,
    is_active   BOOLEAN        NOT NULL DEFAULT TRUE,
    created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_places_owner
        FOREIGN KEY (owner_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- reviews
-- ---------------------------------------------------------------
CREATE TABLE reviews (
    id          CHAR(36)  NOT NULL,
    text        TEXT      NOT NULL,
    rating      INT       NOT NULL,
    user_id     CHAR(36)  NOT NULL,
    place_id    CHAR(36)  NOT NULL,
    created_at  DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP
                          ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_reviews_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_reviews_place
        FOREIGN KEY (place_id) REFERENCES places(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_reviews_user_place UNIQUE (user_id, place_id),
    CONSTRAINT chk_reviews_rating CHECK (rating BETWEEN 1 AND 5)
);

-- ---------------------------------------------------------------
-- amenities
-- ---------------------------------------------------------------
CREATE TABLE amenities (
    id          CHAR(36)     NOT NULL,
    name        VARCHAR(255) NOT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                             ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_amenities_name (name)
);

-- ---------------------------------------------------------------
-- place_amenities
-- ---------------------------------------------------------------
CREATE TABLE place_amenities (
    place_id    CHAR(36) NOT NULL,
    amenity_id  CHAR(36) NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    CONSTRAINT fk_place_amenity_place
        FOREIGN KEY (place_id) REFERENCES places(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_place_amenity_amenity
        FOREIGN KEY (amenity_id) REFERENCES amenities(id)
        ON DELETE CASCADE
);
