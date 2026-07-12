# HBnB — Experimental ER Diagram (Draft `Reservation` Entity)

**Status: experimental / not part of the official schema.** This is a
sketch for a possible future `Reservation` (booking) entity and is kept
separate from `erDiagram.md' so it doesn't get
mistaken for the current, implemented schema.

```mermaid
erDiagram
    USER ||--o{ PLACE : owns
    USER ||--o{ REVIEW : writes
    PLACE ||--o{ REVIEW : receives
    PLACE ||--o{ PLACE_AMENITY : "has"
    AMENITY ||--o{ PLACE_AMENITY : "belongs to"
    USER ||--o{ RESERVATION : books
    PLACE ||--o{ RESERVATION : "is booked via"

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

    RESERVATION {
        char_36 id PK
        char_36 user_id FK
        char_36 place_id FK
        date start_date
        date end_date
        decimal total_price
        string status
    }
```

## Draft relationships

- **User → Reservation (one-to-many):** one `User` can make many
  `Reservation` records; each `Reservation` belongs to exactly one
  `User` via `reservations.user_id`.
- **Place → Reservation (one-to-many):** one `Place` can have many
  `Reservation` records booked against it; each `Reservation` belongs to
  exactly one `Place` via `reservations.place_id`.

## Open questions before this could move to the official schema

- Should overlapping date ranges for the same `place_id` be rejected at
  the database level (e.g. an exclusion constraint) or in the business
  logic layer?
- Does `status` need to be an enum (`pending`, `confirmed`, `cancelled`)
  enforced with a `CHECK` constraint?
- Is `total_price` computed and stored, or derived on read from
  `place.price` and the date range?
