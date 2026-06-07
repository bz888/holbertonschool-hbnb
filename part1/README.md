# HBNB

This README describes the high-level backend operations, business logic, API structure, service classes, repositories, ORM usage, database choice, frontend consumers, and expected JSON payloads for an Airbnb-style clone.

The backend is designed around Flask, SQLAlchemy ORM, and AWS RDS. The application follows a layered architecture so that API routes, business logic, and database access remain separated.

## High-Level Architecture

```text
---
config:
  layout: elk
---
classDiagram
    class PresentationLayer {
        +REST API endpoints
        +UserController
        +PlaceController
        +ReviewController
        +AmenityController
    }

    class BusinessLogicLayer {
        +User
        +Place
        +Review
        +Amenity
        +HBnBFacade
    }

    class PersistenceLayer {
        +UserRepository
        +PlaceRepository
        +ReviewRepository
        +AmenityRepository
    }

    PresentationLayer --> BusinessLogicLayer : "Facade pattern"
    BusinessLogicLayer --> PersistenceLayer : "Database operations"

```

## Business Logic Overview

The application allows users to list places, review places, and associate amenities with places.

A `User` can own many `Place` records. Each `Place` must belong to exactly one `User`, which means places require an owner before they can be created.

A `User` can write many `Review` records. Each `Review` belongs to one `User` and one `Place`.

A `Place` can have many `Amenity` records, and one `Amenity` can be linked to many places. This is a many-to-many relationship handled through the `place_amenities` join table.

## Potential Tech Stack

### Backend
```text
Python
Flask 
```

### Database

```text
PostgreSQL or MySQL
```
PostgreSQL is a strong choice because it supports relational integrity, joins, constraints, indexing, and production-scale querying.

### Development And Testing

```text
Postman
pytest
Docker
GitHub Actions
```

### Deployment

```text
AWS RDS for the database
AWS Elastic Beanstalk, ECS, or EC2 for the Flask API
AWS CloudWatch for logs and monitoring
```

## Core Data Models

```text
User
- id
- first_name
- last_name
- email
- password

Place
- id
- title
- description
- price
- latitude
- longitude
- owner_id

Review
- id
- comment
- rating
- user_id
- place_id

Amenity
- id
- name

PlaceAmenity
- place_id
- amenity_id
```

## Controllers

Controllers handle HTTP requests and responses. Their job is to read request data, validate it, call the correct service method, and return JSON responses.

Controllers should not contain direct database logic. Database work should be handled by repositories through the ORM.

### UserController

```text
create_user()
get_users()
get_user(user_id)
update_user(user_id)
delete_user(user_id)
```

### PlaceController

```text
create_place(user_id)
get_places()
get_place(place_id)
get_user_places(user_id)
update_place(user_id, place_id)
delete_place(user_id, place_id)
```

Because every place belongs to one user, create, update, and delete operations include `user_id` when ownership needs to be checked.

### ReviewController

```text
create_review()
get_place_reviews(place_id)
get_review(review_id)
update_review(review_id)
delete_review(review_id)
```

### AmenityController

```text
create_amenity()
get_amenities()
get_amenity(amenity_id)
update_amenity(amenity_id)
delete_amenity(amenity_id)
```

## Service Classes

Services contain the main business logic. They sit between the controllers and repositories.

### UserService

```text
create_user(data)
get_user(user_id)
get_all_users()
update_user(user_id, data)
delete_user(user_id)
```

### PlaceService

```text
create_place(user_id, data)
get_place(place_id)
get_all_places()
get_places_by_user(user_id)
update_place(user_id, place_id, data)
delete_place(user_id, place_id)
add_amenity(place_id, amenity_id)
remove_amenity(place_id, amenity_id)
```

The `PlaceService` should check that the user exists before creating a place. It should also confirm that a place belongs to the provided user before allowing update or delete operations.

### ReviewService

```text
create_review(data)
get_review(review_id)
get_reviews_by_place(place_id)
update_review(review_id, data)
delete_review(review_id)
```

The `ReviewService` should check that the referenced user and place exist before creating a review.

### AmenityService

```text
create_amenity(data)
get_amenity(amenity_id)
get_all_amenities()
update_amenity(amenity_id, data)
delete_amenity(amenity_id)
```

## Repository Layer

Repositories isolate database operations from business logic.

```text
UserRepository
PlaceRepository
ReviewRepository
AmenityRepository
```

Common repository methods:

```text
save(entity)
get_by_id(id)
get_all()
update(id, data)
delete(id)
```

Repository-specific methods:

```text
PlaceRepository.get_by_owner(user_id)
ReviewRepository.get_by_place(place_id)
ReviewRepository.get_by_user(user_id)
AmenityRepository.get_by_name(name)
```

## ORM

SQLAlchemy ORM maps Python classes to database tables.

```text
User model -> users table
Place model -> places table
Review model -> reviews table
Amenity model -> amenities table
PlaceAmenity relationship -> place_amenities join table
```

The ORM handles:

```text
INSERT
SELECT
UPDATE
DELETE
JOIN
relationship loading
foreign key constraints
many-to-many relationships
```

## API Endpoints

### Users

Create a user:

```http
POST /api/users
Content-Type: application/json
```

```json
{
  "first_name": "Ben",
  "last_name": "Smith",
  "email": "ben@example.com",
  "password": "securePassword123"
}
```

Example response:

```json
{
  "id": "user_123",
  "first_name": "Ben",
  "last_name": "Smith",
  "email": "ben@example.com"
}
```

Get all users:

```http
GET /api/users
```

Get one user:

```http
GET /api/users/user_123
```

Update a user:

```http
PUT /api/users/user_123
Content-Type: application/json
```

```json
{
  "first_name": "Benjamin",
  "last_name": "Smith",
  "email": "benjamin@example.com",
  "password": "newPassword123"
}
```

Delete a user:

```http
DELETE /api/users/user_123
```

### Places

Every place must belong to a user, so the `user_id` is included in owner-specific place routes.

Create a place:

```http
POST /api/users/user_123/places
Content-Type: application/json
```

```json
{
  "title": "Modern Beach Apartment",
  "description": "A bright apartment close to the beach.",
  "price": 180.0,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "amenities": ["amenity_1", "amenity_2"]
}
```

Example response:

```json
{
  "id": "place_456",
  "title": "Modern Beach Apartment",
  "description": "A bright apartment close to the beach.",
  "price": 180.0,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner": {
    "id": "user_123",
    "first_name": "Ben",
    "last_name": "Smith"
  },
  "amenities": [
    {
      "id": "amenity_1",
      "name": "WiFi"
    },
    {
      "id": "amenity_2",
      "name": "Parking"
    }
  ]
}
```

Get all places:

```http
GET /api/places
```

Get all places owned by a user:

```http
GET /api/users/user_123/places
```

Get one place:

```http
GET /api/places/place_456
```

Update a place:

```http
PUT /api/users/user_123/places/place_456
Content-Type: application/json
```

```json
{
  "title": "Updated Beach Apartment",
  "description": "Updated description.",
  "price": 200.0,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "amenities": ["amenity_1"]
}
```

Delete a place:

```http
DELETE /api/users/user_123/places/place_456
```

### Reviews

Create a review:

```http
POST /api/reviews
Content-Type: application/json
```

```json
{
  "comment": "Great location and very clean.",
  "rating": 5,
  "user_id": "user_123",
  "place_id": "place_456"
}
```

Example response:

```json
{
  "id": "review_789",
  "comment": "Great location and very clean.",
  "rating": 5,
  "user": {
    "id": "user_123",
    "first_name": "Ben"
  },
  "place": {
    "id": "place_456",
    "title": "Modern Beach Apartment"
  }
}
```

Get reviews for a place:

```http
GET /api/places/place_456/reviews
```

Get one review:

```http
GET /api/reviews/review_789
```

Update a review:

```http
PUT /api/reviews/review_789
Content-Type: application/json
```

```json
{
  "comment": "Updated review text.",
  "rating": 4
}
```

Delete a review:

```http
DELETE /api/reviews/review_789
```

### Amenities

Create an amenity:

```http
POST /api/amenities
Content-Type: application/json
```

```json
{
  "name": "WiFi"
}
```

Example response:

```json
{
  "id": "amenity_1",
  "name": "WiFi"
}
```

Get all amenities:

```http
GET /api/amenities
```

Get one amenity:

```http
GET /api/amenities/amenity_1
```

Update an amenity:

```http
PUT /api/amenities/amenity_1
Content-Type: application/json
```

```json
{
  "name": "High-speed WiFi"
}
```

Delete an amenity:

```http
DELETE /api/amenities/amenity_1
```

## Error Responses

Validation error:

```json
{
  "error": "ValidationError",
  "message": "Email is required."
}
```

Not found error:

```json
{
  "error": "NotFound",
  "message": "Place not found."
}
```

Unauthorized error:

```json
{
  "error": "Unauthorized",
  "message": "You are not allowed to perform this action."
}
```

Ownership error:

```json
{
  "error": "Forbidden",
  "message": "This place does not belong to the provided user."
}
```

## Frontend Consumers

Frontend consumers are pages, components, or services that call the backend API using JSON.

```text
Signup Page
- POST /api/users

Profile Page
- GET /api/users/{user_id}
- PUT /api/users/{user_id}

Places Listing Page
- GET /api/places

User Dashboard
- GET /api/users/{user_id}/places
- DELETE /api/users/{user_id}/places/{place_id}

Create Place Form
- POST /api/users/{user_id}/places
- GET /api/amenities

Place Details Page
- GET /api/places/{place_id}
- GET /api/places/{place_id}/reviews

Review Form
- POST /api/reviews

Amenity Management Page
- POST /api/amenities
- GET /api/amenities
- PUT /api/amenities/{amenity_id}
- DELETE /api/amenities/{amenity_id}
```

## Request Flow Example

Creating a place follows this flow:

```text
Frontend sends POST /api/users/user_123/places
Controller validates request body
PlaceService checks that user_123 exists
PlaceService creates the Place model
PlaceRepository saves it through SQLAlchemy
SQLAlchemy inserts the record into AWS RDS
Controller returns the created place as JSON
```

## Summary

The Flask backend exposes REST APIs for frontend consumers. Controllers handle HTTP concerns, services enforce business rules, repositories isolate persistence logic, SQLAlchemy maps Python models to relational tables, and AWS RDS stores the application data.

