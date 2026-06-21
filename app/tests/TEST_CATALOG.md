# HBnB Test Catalogue

This document lists every automated test in the `tests/` directory and
summarizes the behavior each test verifies.

Current suite:

- 88 unit tests
- 13 integration tests
- 101 tests total

## Unit Tests

### BaseModel
- `test_base_model_has_id_and_timestamps`
  - Verifies that a new model has a string UUID and `datetime` creation and
    update timestamps.
- `test_base_models_have_unique_ids`
  - Verifies that separate model instances receive different IDs.
- `test_save_updates_updated_at`
  - Verifies that saving a model refreshes its `updated_at` timestamp.
- `test_update_sets_existing_attributes`
  - Verifies that `update()` changes existing attributes and ignores unknown
    attributes.

### User Model and User Facade
#### User model

- `test_create_valid_user`
  - Verifies default values and fields for a valid user.
- `test_user_trims_valid_string_fields`
  - Verifies trimming of names and trimming/lowercasing of email addresses.
- `test_user_rejects_empty_names`
  - Verifies that empty or whitespace-only first and last names are rejected.
- `test_user_rejects_non_string_names_and_email`
  - Verifies that names and email addresses must be strings.
- `test_user_rejects_names_longer_than_50_characters`
  - Verifies the maximum length for first and last names.
- `test_user_accepts_names_at_50_character_boundary`
  - Verifies that names containing exactly 50 characters are accepted.
- `test_user_rejects_invalid_email_format`
  - Verifies rejection of empty, incomplete, malformed, and whitespace-bearing
    email addresses.
- `test_user_update_uses_validation`
  - Verifies that model updates still apply email validation.
- `test_user_to_dict_serializes_complete_model`
  - Verifies the complete user dictionary, including internal flags and ISO
    timestamps.
- `test_add_place`
  - Verifies that a place can be added to the user's owned places.
- `test_add_review`
  - Verifies that a review can be added to the user's written reviews.

#### User facade

- `test_facade_user_update_rejects_unsupported_fields`
  - Verifies that protected or unsupported user fields cannot be updated.
- `test_facade_enforces_unique_email_in_memory`
  - Verifies that two users cannot be created with the same email address.
- `test_facade_normalizes_email_before_uniqueness_check`
  - Verifies that case and surrounding whitespace cannot bypass uniqueness.
- `test_facade_updates_and_normalizes_user_email`
  - Verifies a successful email update and normalized email lookup.
- `test_facade_allows_user_to_keep_same_normalized_email`
  - Verifies that a user may update to the normalized form of their own email.
- `test_facade_rejects_email_update_collision`
  - Verifies that updating to another user's email is rejected without
    modifying either user.
- `test_facade_email_lookup_returns_none_when_missing`
  - Verifies that an unknown email lookup returns `None`.
- `test_facade_user_update_raises_when_user_is_missing`
  - Verifies that updating an unknown user raises `UserNotFound`.
- `test_soft_delete_user_sets_inactive_flag`
  - Verifies that soft deletion deactivates the user without removing it.
- `test_delete_user_hard_deletes_user`
  - Verifies permanent deletion and subsequent `UserNotFound` behavior.

### Amenity Model and Amenity Facade
#### Amenity model

- `test_create_valid_amenity`
  - Verifies creation of an amenity with a valid name.
- `test_amenity_trims_name`
  - Verifies removal of surrounding whitespace from amenity names.
- `test_amenity_rejects_empty_name`
  - Verifies rejection of empty and whitespace-only names.
- `test_amenity_rejects_non_string_name`
  - Verifies that amenity names must be strings.
- `test_amenity_rejects_name_longer_than_50_characters`
  - Verifies the maximum amenity name length.
- `test_amenity_accepts_name_at_50_character_boundary`
  - Verifies that an amenity name containing exactly 50 characters is accepted.
- `test_amenity_update_uses_validation`
  - Verifies that model updates still apply name validation.
- `test_to_dict`
  - Verifies the complete amenity dictionary and ISO timestamps.

#### Amenity facade

- `test_facade_raises_when_amenity_is_not_found`
  - Verifies missing-amenity errors for retrieval and deletion.
- `test_facade_rejects_invalid_amenity_data`
  - Verifies invalid creation and update payload handling.
- `test_update_raises_when_amenity_does_not_exist`
  - Verifies that updating an unknown amenity raises `AmenityNotFound`.
- `test_facade_creates_and_updates_amenity`
  - Verifies normalized creation and a successful name update.
- `test_facade_amenity_update_rejects_unsupported_fields`
  - Verifies that unsupported amenity fields are rejected without partial
    mutation.

### Place Model and Place Facade
#### Place model

- `test_create_valid_place`
  - Verifies fields, defaults, ownership, and empty relationships for a place.
- `test_place_requires_user_owner`
  - Verifies that a place owner must be a `User` instance.
- `test_place_rejects_invalid_title`
  - Verifies rejection of empty, whitespace-only, and oversized titles.
- `test_place_rejects_non_string_title`
  - Verifies that a place title must be a string.
- `test_place_trims_title`
  - Verifies removal of surrounding whitespace from titles.
- `test_place_accepts_title_at_100_character_boundary`
  - Verifies that a title containing exactly 100 characters is accepted.
- `test_place_rejects_non_positive_price`
  - Verifies that prices must be positive numbers and cannot be booleans or
    strings.
- `test_place_validates_coordinate_ranges`
  - Verifies latitude and longitude range enforcement.
- `test_place_rejects_non_numeric_coordinates`
  - Verifies that coordinates cannot be booleans or strings.
- `test_place_accepts_coordinate_boundaries`
  - Verifies acceptance of latitude `-90`/`90` and longitude `-180`/`180`.
- `test_place_update_uses_validation`
  - Verifies that model updates still apply price validation.
- `test_add_review`
  - Verifies adding a review to a place.
- `test_add_amenity`
  - Verifies adding an amenity to a place.
- `test_place_to_dict_serializes_complete_model`
  - Verifies the complete place dictionary, owner ID, amenity IDs, active
    state, and ISO timestamps.

#### Place facade

- `test_facade_validates_owner_exists_in_memory`
  - Verifies that a place cannot be created for an unknown owner.
- `test_facade_place_update_rejects_unsupported_fields`
  - Verifies that ownership cannot be changed through a place update.
- `test_facade_updates_place_fields`
  - Verifies successful updates to title, description, price, and coordinates.
- `test_facade_replaces_and_clears_place_amenities`
  - Verifies replacing the amenity collection and clearing it with an empty
    `amenity_ids` list.
- `test_facade_rejects_unknown_amenity_without_changing_place`
  - Verifies that an unknown amenity ID is rejected atomically.
- `test_facade_place_update_raises_when_place_is_missing`
  - Verifies that updating an unknown place raises `PlaceNotFound`.
- `test_delete_place_hard_deletes_place`
  - Verifies permanent deletion and missing-place behavior afterward.

### Review Model and Review Facade
#### Review model

- `test_create_valid_review`
  - Verifies fields and relationships for a valid review.
- `test_review_requires_place_and_user_instances`
  - Verifies that review relationships require `Place` and `User` instances.
- `test_review_rejects_empty_text`
  - Verifies rejection of empty and whitespace-only review text.
- `test_review_rejects_non_string_text`
  - Verifies that review text must be a string.
- `test_review_trims_text`
  - Verifies removal of surrounding whitespace from review text.
- `test_review_rejects_rating_outside_1_to_5`
  - Verifies rejection of ratings outside 1–5 and non-integer values.
- `test_review_accepts_rating_boundaries`
  - Verifies that ratings `1` and `5` are accepted.
- `test_review_update_uses_validation`
  - Verifies that model updates still enforce the rating range.
- `test_review_to_dict_serializes_complete_model`
  - Verifies the complete review dictionary, relationship IDs, and ISO
    timestamps.

#### Review facade

- `test_facade_review_update_only_changes_text_and_rating`
  - Verifies successful updates while preserving the review relationships.
- `test_facade_review_update_rejects_unsupported_fields`
  - Verifies that user, place, and active-state fields cannot be changed.
- `test_facade_validates_review_relationships_in_memory`
  - Verifies that a review cannot be created for an unknown place.
- `test_facade_links_review_to_place_and_user`
  - Verifies that creation links the review to both its place and author.
- `test_owner_cannot_review_own_place`
  - Verifies the business rule preventing owners from reviewing their own
    places.
- `test_reviews_can_be_listed_by_user`
  - Verifies facade filtering of reviews by author.
- `test_deleting_reviewer_preserves_review`
  - Verifies that soft-deleting a reviewer preserves their reviews and
    relationships.
- `test_deleting_place_preserves_review`
  - Verifies that hard-deleting a place does not delete its review record.
- `test_deleting_owner_deactivates_owned_places`
  - Verifies that soft-deleting an owner deactivates their places.
- `test_deleting_review_unlinks_relationships`
  - Verifies that deleting a review removes it from the place and user lists.

### In-Memory Repository
- `test_find_one_returns_first_matching_object`
  - Verifies returning the first object matching all supplied filters.
- `test_find_one_returns_none_when_no_object_matches`
  - Verifies `None` is returned when no object matches.
- `test_find_all_filters_by_multiple_attributes`
  - Verifies filtering objects using multiple attributes.
- `test_find_all_without_filters_returns_every_object`
  - Verifies that an unfiltered query returns all stored objects.
- `test_find_all_does_not_match_missing_attributes`
  - Verifies that objects lacking a requested attribute are not matched.
- `test_get_by_attribute_uses_dynamic_lookup`
  - Verifies lookup using a dynamically supplied attribute name.

### API Error Handlers
- `test_registers_all_application_errors`
  - Verifies registration of all domain, validation, and business-rule error
    handlers.
- `test_not_found_handler_returns_404`
  - Verifies the standard error body and HTTP 404 status.
- `test_duplicate_email_handler_returns_400`
  - Verifies duplicate-email errors return the standard body and HTTP 400.
- `test_invalid_request_handler_returns_400`
  - Verifies validation and business-rule errors return HTTP 400.

## Integration Tests
### Global Error Handling and Missing Resources

- `test_not_found_and_validation_errors_use_global_handlers`
  - Routes: user, place, amenity, and review `GET`; amenity `POST` and `PUT`.
  - Verifies standard 404 and validation-error responses from global handlers.
- `test_missing_mutation_and_nested_routes_return_404`
  - Routes:
    - `PUT` and `DELETE /api/v1/users/<user_id>`
    - `DELETE /api/v1/users/<user_id>/soft-delete`
    - `GET /api/v1/users/<user_id>/reviews`
    - `PUT` and `DELETE /api/v1/amenities/<amenity_id>`
    - `PUT` and `DELETE /api/v1/places/<place_id>`
    - `GET` and `POST /api/v1/places/<place_id>/reviews`
    - `PUT` and `DELETE /api/v1/reviews/<review_id>`
  - Verifies that mutation and nested routes return HTTP 404 with the correct
    resource-specific body.
- `test_conflict_and_business_rule_errors_use_global_handlers`
  - Routes: `POST /users`, `POST /places`, and nested `POST /places/<id>/reviews`.
  - Verifies duplicate-email and owner-review business-rule responses.

### User Routes

- `test_user_responses_exclude_internal_model_fields`
  - Routes: user `POST`, `GET`, `PUT`, and collection `GET`.
  - Verifies public response schemas and the successful update response.
- `test_user_soft_and_hard_delete_routes`
  - Routes: `DELETE /users/<id>/soft-delete` and `DELETE /users/<id>`.
  - Verifies soft deactivation, permanent deletion, response status, and body.

### Amenity, Review, and Related Routes

- `test_amenity_and_review_responses_exclude_timestamps`
  - Routes: amenity and review creation, retrieval, listing, and update; place
    update; user/place review listings.
  - Verifies public response schemas, successful update messages, and persisted
    updates.
- `test_review_update_rejects_user_and_place_changes`
  - Route: `PUT /api/v1/reviews/<review_id>`.
  - Verifies rejection of attempts to change review ownership or place.
- `test_amenity_and_review_delete_routes`
  - Routes: `DELETE /api/v1/amenities/<amenity_id>` and
    `DELETE /api/v1/reviews/<review_id>`.
  - Verifies success responses and removal from the repositories.

### Cross-Resource Update Validation

- `test_updates_reject_unsupported_fields`
  - Routes: user, amenity, and place `PUT`.
  - Verifies HTTP 400 responses and absence of partial mutation for unsupported
    fields.

### Place Routes

- `test_place_delete_route_hard_deletes_place`
  - Route: `DELETE /api/v1/places/<place_id>`.
  - Verifies the success response, repository deletion, and subsequent 404.
- `test_place_update_route_succeeds`
  - Route: `PUT /api/v1/places/<place_id>`.
  - Verifies the success response and persisted title update.
- `test_place_list_and_nested_review_creation_routes`
  - Routes: `GET /api/v1/places/` and
    `POST /api/v1/places/<place_id>/reviews`.
  - Verifies place listing and successful nested review creation.
- `test_place_details_include_nested_relationships`
  - Route: `GET /api/v1/places/<place_id>`.
  - Verifies nested owner, amenity, and review representations.
