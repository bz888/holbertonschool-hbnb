# User

## POST /api/v1/users/

### 201

Req:

```JSON
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com"
}
```

Res:

```JSON
{
  "id": "6497be3e-2a50-4cb7-95b4-07a0fd34ffda",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com"
}
```

Res

### 400

Req:

```JSON
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com"
}
```

Res:

```JSON
{
  "error": "Email 'john.doe@example.com' is already registered"
}
```

Req:

```JSON
{
"first_name": "John",
"last_name": "Doe",
"hello": "john.doe@example.com"
}
```

Res

```JSON
{
  "errors": {
    "email": "'email' is a required property"
  },
  "message": "Input payload validation failed"
}
```

req:

```JSON
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doeexample.com"
}
```

res:

```JSON
{
  "error": "Email must be a valid email address"
}
```

req:

```JSON
{
  "first_name": 1,
  "last_name": "Doe",
  "email": "john.doe@example.com"
}
```

res:

```JSON
{
  "errors": {
    "first_name": "1 is not of type 'string'"
  },
  "message": "Input payload validation failed"
}
```

## GET /api/v1/users/<user_id>

### 200

res

```JSON
{
  "id": "6497be3e-2a50-4cb7-95b4-07a0fd34ffda",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com"
}
```

### 404

res

```
{
  "error": "User '123' not found"
}
```

## GET /api/v1/users/

## 200

```json
[
  {
    "id": "6497be3e-2a50-4cb7-95b4-07a0fd34ffda",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
  },
  {
    "id": "d1179e8c-755a-4f97-bdd1-4a8b3e53da1c",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com"
  }
]
```

## PUT /api/v1/users/<user_id>

- Expected response based on holberton HBNB doc
- Response is not consistent with other PUT routes as there are inconsistencies with the hbnb doc

### 200

req

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "111.doe@example.com"
}
```

res

```json
{
  "id": "bba1db23-6c30-4d24-98c0-b971f32b427d",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "111.doe@example.com"
}
```

### 404

If user id not in db

req:

```JSON
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com"
}
```

res:

```JSON
{
"error": "User '90' not found"
}
```

### 400

req

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "not_email": "jane.doe@example.com"
}
```

res

```json
{
  "error": "Invalid fields for user: not_email. Allowed fields: email, first_name, last_name"
}
```

req

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doeexample.com"
}
```

res

```json
{
  "error": "Email must be a valid email address"
}
```

Duplicate email
req

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com"
}
```

res

```json
{
  "error": "Email 'jane.doe@example.com' is already registered"
}
```

## DEL /api/v1/users/<user_id>

### 200

res

```json
{
  "message": "User permanently deleted"
}
```

### 404

```json
{
  "error": "User 'hello' not found"
}
```

## GET /api/v1/users/{user_id}/reviews

### 200

res

```json
[
  {
    "id": "5c848bc9-908c-48f4-9173-d516d58ee5b8",
    "text": "Excellent location",
    "rating": 5,
    "place_id": "ca544369-e40f-4e16-856c-76303426bd32",
    "user_id": "a20e4b6a-5923-41cd-baf3-9eff45f5347e"
  }
]
```

### 404

```json
{
  "error": "User 'hello' not found"
}
```

# Amenities

## POST /api/v1/amenities

### 201

req

```json
{
  "name": "wifi"
}
```

res

```json
{
  "id": "b597346b-b2ec-4b04-8c69-4dc6aec6aa68",
  "name": "wifi"
}
```

### 400

req

```json
{
  "hello": "wifi"
}
```

res

```json
{
  "errors": {
    "name": "'name' is a required property"
  },
  "message": "Input payload validation failed"
}
```

## GET /api/v1/amenities

### 200

res

```
[
  {
    "id": "b597346b-b2ec-4b04-8c69-4dc6aec6aa68",
    "name": "wifi"
  }
]
```

## GET /api/v1/amenities/{amenity_id}

### 200

res

```
{
  "id": "b597346b-b2ec-4b04-8c69-4dc6aec6aa68",
  "name": "wifi"
}
```

### 404

res

```
{
"error": "Amenity 'hello' not found"
}
```

## PUT /api/v1/amenities/{amenity_id}

### 200

```json
req
{
  "name": "High-speed Wi-Fi"
}

res
{
  "message": "Amenity updated successfully"
}
```

### 400

```json
req
{
  "name": "High-speed Wi-Fi",
  "water": "High-speed Wi-Fi"
}

res
{
  "error": "Invalid fields for amenity: water. Allowed fields: name"
}
```

```json
req
{
  "name": 1
}

res
{
  "errors": {
    "name": "1 is not of type 'string'"
  },
  "message": "Input payload validation failed"
}
```

### 404

res

```json
{
  "error": "Amenity 'hello' not found"
}
```

## DEL /api/v1/amenities/{amenity_id}

### 200

res

```JSOn
{
  "message": "Amenity deleted successfully"
}
```

### 404

res

```JSON
{
  "error": "Amenity 'hello' not found"
}
```

# Places

## GET /api/v1/places

### 200

```json
res
[
  {
    "id": "162954dd-892b-4c18-86a9-b0cb227e6f74",
    "title": "Melbourne Apartment",
    "description": "Central apartment",
    "price": 150.0,
    "latitude": -37.8136,
    "longitude": 144.9631,
    "owner_id": "61418d83-3c1d-4215-aea5-9ad02acad783",
    "owner": {
      "id": "61418d83-3c1d-4215-aea5-9ad02acad783",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com"
    },
    "amenities": [
      {
        "id": "36c39b6f-66cd-4507-97f7-85b1c5dcca0f",
        "name": "wifi"
      }
    ],
    "reviews": []
  }
]
```

## GET /api/v1/places/{place_id}

### 200

```json
res
{
  "id": "162954dd-892b-4c18-86a9-b0cb227e6f74",
  "title": "Melbourne Apartment",
  "description": "Central apartment",
  "price": 150.0,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner_id": "61418d83-3c1d-4215-aea5-9ad02acad783",
  "owner": {
    "id": "61418d83-3c1d-4215-aea5-9ad02acad783",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
  },
  "amenities": [
    {
      "id": "36c39b6f-66cd-4507-97f7-85b1c5dcca0f",
      "name": "wifi"
    }
  ],
  "reviews": []
}
```

### 404

```json
res
{
  "error": "Place 'hello' not found"
}
```

## GET /api/v1/places/{place_id}/reviews

### 200

res

```json
[
  {
    "id": "b021c3f2-4add-444f-9228-7f81131c2323",
    "text": "Excellent location",
    "rating": 5,
    "place_id": "162954dd-892b-4c18-86a9-b0cb227e6f74",
    "user_id": "ba1db5cd-8ec4-4e38-b16d-31075c1582ea"
  }
]
```

### 404

```json
{
  "error": "Place '{{place_id' not found"
}
```

## POST /api/v1/places

### 201

```json
req
{
  "title": "Melbourne Apartment",
  "description": "Central apartment",
  "price": 150.0,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner_id": "{{user_id}}",
  "amenity_ids": ["{{amenity_id}}"]
}
res
{
  "id": "162954dd-892b-4c18-86a9-b0cb227e6f74",
  "title": "Melbourne Apartment",
  "description": "Central apartment",
  "price": 150.0,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner_id": "61418d83-3c1d-4215-aea5-9ad02acad783",
  "owner": {
    "id": "61418d83-3c1d-4215-aea5-9ad02acad783",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
  },
  "amenities": [
    {
      "id": "36c39b6f-66cd-4507-97f7-85b1c5dcca0f",
      "name": "wifi"
    }
  ],
  "reviews": []
}
```

Validation implementation required to fix

```json
req
{
  "title": "Melbourne Apartment",
  "description": "Central apartment",
  "price": 1,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner_id": "{{user_id}}",
  "amenity_ids": ["{{amenity_id}}"],
  "hello": "hello"
}
res
{
  "id": "d04f942b-e958-4e1b-842f-2d80e0000279",
  "title": "Melbourne Apartment",
  "description": "Central apartment",
  "price": 1.0,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner_id": "61418d83-3c1d-4215-aea5-9ad02acad783",
  "owner": {
    "id": "61418d83-3c1d-4215-aea5-9ad02acad783",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
  },
  "amenities": [
    {
      "id": "36c39b6f-66cd-4507-97f7-85b1c5dcca0f",
      "name": "wifi"
    }
  ],
  "reviews": []
}
```

### 400

```json
req
{
  "title": "Melbourne Apartment",
  "description": "Central apartment",
  "price": "hello",
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner_id": "{{user_id}}",
  "amenity_ids": ["{{amenity_id}}"]
}
res
{
  "errors": {
    "price": "'hello' is not of type 'number'"
  },
  "message": "Input payload validation failed"
}
```

```json
req
{
  "title": "Melbourne Apartment",
  "description": "Central apartment",
  "price": 1,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner_i": "{{user_id}}",
  "amenity_ids": ["{{amenity_id}}"]
}
res
{
  "errors": {
    "owner_id": "'owner_id' is a required property"
  },
  "message": "Input payload validation failed"
}
```

### 404

```json
req
{
  "title": "Melbourne Apartment",
  "description": "Central apartment",
  "price": 1,
  "latitude": -37.8136,
  "longitude": 144.9631,
  "owner_id": "hello",
  "amenity_ids": ["{{amenity_id}}"]
}
res
{
  "error": "User 'hello' not found"
}
```

## PUT /api/v1/places/{place_id}

### 400

```json
req
{
  "title": "Updated Melbourne Apartment",
  "price": 1744.0,
  "descriptio": "good place"
}
res
{
  "error": "Invalid fields for place: descriptio. Allowed fields: amenity_ids, description, latitude, longitude, price, title"
}
```

```json
req
{
  "title": "Updated Melbourne Apartment",
  "price": 1744.0,
  "description": 4324
}
res
{
  "errors": {
    "description": "4324 is not of type 'string'"
  },
  "message": "Input payload validation failed"
}
```

### 404

```json
req
{
  "title": "Updated Melbourne Apartment",
  "price": 1744.0,
  "description": "good place"
}

res
{
  "error": "Place 'd04f942b-e958-4e1b-842f-2d80e0000279' not found"
}
```

### 200

```json
req
{
  "title": "Updated Melbourne Apartment",
  "price": 1744.0,
  "description": "good place"
}
res
{
  "message": "Place updated successfully"
}
```

## POST /api/v1/places/{place_id}/reviews

### 201

```json
req
{
  "text": "Great stay",
  "rating": 5,
  "user_id": "{{reviewer_id}}"
}
res
{
  "id": "f9b514ab-f721-40bc-a36b-2c186ccf7ee4",
  "text": "Great stay",
  "rating": 5,
  "place_id": "0a0c20f0-03b9-4538-804e-f0503e008be0",
  "user_id": "4604550f-eec0-4c3b-ae06-b56bb4577e66"
}
```

# Reviews

## GET /api/v1/reviews

### 200

```json
res
[
  {
    "id": "f9b514ab-f721-40bc-a36b-2c186ccf7ee4",
    "text": "Great stay",
    "rating": 5,
    "place_id": "0a0c20f0-03b9-4538-804e-f0503e008be0",
    "user_id": "4604550f-eec0-4c3b-ae06-b56bb4577e66"
  }
]
```

## GET /api/v1/reviews/{{user_id}}

### 200

```json
res
{
  "id": "f9b514ab-f721-40bc-a36b-2c186ccf7ee4",
  "text": "Great stay",
  "rating": 5,
  "place_id": "0a0c20f0-03b9-4538-804e-f0503e008be0",
  "user_id": "4604550f-eec0-4c3b-ae06-b56bb4577e66"
}
```

### 404

```json
{
  "error": "Review '{{review_id' not found"
}
```

## POST /api/v1/reviews/

### 201

```json
req
{
  "text": "Excellent location",
  "rating": 5,
  "user_id": "{{reviewer_id}}",
  "place_id": "{{place_id}}"
}
res
{
  "id": "a27c3382-a66a-4994-8ce7-d5cbe8c0960b",
  "text": "Excellent location",
  "rating": 5,
  "place_id": "0a0c20f0-03b9-4538-804e-f0503e008be0",
  "user_id": "4604550f-eec0-4c3b-ae06-b56bb4577e66"
}
```

### 400

```json
req
{
  "text": "Excellent location",
  "ratin": 5,
  "user_id": "{{reviewer_id}}",
  "place_id": "{{place_id}}"
}
res
{
  "errors": {
    "rating": "'rating' is a required property"
  },
  "message": "Input payload validation failed"
}
```

```json
req
{
  "text": "Excellent location",
  "rating": "10",
  "user_id": "{{reviewer_id}}",
  "place_id": "{{place_id}}"
}
res
{
  "errors": {
    "rating": "'10' is not of type 'integer'"
  },
  "message": "Input payload validation failed"
}
```

```json
req
{
  "text": "Excellent location",
  "rating": 10,
  "user_id": "{{reviewer_id}}",
  "place_id": "{{place_id}}"
}
res
{
  "error": "Review rating must be an integer from 1 to 5"
}

req
{
  "text": "Excellent location",
  "rating": 5,
  "user_id": "7aaf935c-81fa-4982-a1c9-8f6e0b52bd77",
  "place_id": "{{place_id}}"
}
res
{
  "error": "Owners cannot review their own place"
}
```

### 404

```json
req
{
  "text": "Excellent location",
  "rating": 5,
  "user_id": "{{reviewer_id}}",
  "place_id": "{{place_"
}
res
{
  "error": "Place '{{place_' not found"
}
```

```json
req
{
  "text": "Excellent location",
  "rating": 5,
  "user_id": "{{reviewer_i",
  "place_id": "0a0c20f0-03b9-4538-804e-f0503e008be0"
}
res
{
  "error": "User '{{reviewer_i' not found"
}
```

## DEL /api/v1/reviews/{review_id}

### 200

res

```json
{
  "message": "Review deleted successfully"
}
```

### 404

res

```json
{
  "error": "Review '{{review_i' not found"
}
```

## PUT /api/v1/reviews/{review_id}

### 200

```json
req
{
  "text": "Updated review text 2",
  "rating": 5
}
res
{
  "message": "Review updated successfully"
}
```

### 400

```json
req
{
  "hello": "Updated review text 2",
  "rating": 5
}
res
{
  "error": "Invalid fields for review: hello. Allowed fields: rating, text"
}

req
{
  "text": "Updated review text 2",
  "rating": 10
}
res
{
  "error": "Review rating must be an integer from 1 to 5"
}

req
{
  "text": "Updated review text 2",
  "rating": "hgi"
}
res
{
  "errors": {
    "rating": "'hgi' is not of type 'integer'"
  },
  "message": "Input payload validation failed"
}

req
{
  "text": "Updated review text 2",
  "rating": 5,
  "add": 3
}
res
{
  "error": "Invalid fields for review: add. Allowed fields: rating, text"
}
```

### 404

```json
req
{
  "text": "Updated review text 2",
  "rating": 5
}
res
{
  "error": "Review '{{review_' not found"
}
```
