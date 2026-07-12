# HBnB — Database ER Diagram

This diagram documents the database schema defined in
`schema.sql`. It mirrors the `User`, `Place`,
`Review`, and `Amenity` models in `app/models/`, plus the `place_amenity`
join table used for the many-to-many place/amenity relationship.

```mermaid
erDiagram
    USER ||--o{ PLACE : owns
    USER ||--o{ REVIEW : writes
    PLACE ||--o{ REVIEW : receives
    PLACE ||--o{ PLACE_AMENITY : "has"
    AMENITY ||--o{ PLACE_AMENITY : "belongs to"

    USER {
        char_36 id PK
        string first_name
        string last_name
        string email UK
        string password
        boolean is_admin
    }

    PLACE {
        char_36 id PK
        string title
        string description
        decimal price
        float latitude
        float longitude
        char_36 owner_id FK
    }

    REVIEW {
        char_36 id PK
        string text
        int rating
        char_36 user_id FK
        char_36 place_id FK
    }

    AMENITY {
        char_36 id PK
        string name UK
    }

    PLACE_AMENITY {
        char_36 place_id PK, FK
        char_36 amenity_id PK, FK
    }
```

## Relationships

- **User → Place (one-to-many):** one `User` owns many `Place` records;
  each `Place` belongs to exactly one `User` via `places.owner_id`.
- **User → Review (one-to-many):** one `User` writes many `Review`
  records; each `Review` belongs to exactly one `User` via
  `reviews.user_id`.
- **Place → Review (one-to-many):** one `Place` receives many `Review`
  records; each `Review` belongs to exactly one `Place` via
  `reviews.place_id`. The `(user_id, place_id)` pair is unique, so a user
  can only review a given place once.
- **Place ↔ Amenity (many-to-many):** one `Place` can have many
  `Amenity` records, and one `Amenity` can belong to many `Place`
  records, resolved through the `place_amenity` join table with a
  composite primary key on `(place_id, amenity_id)`.
