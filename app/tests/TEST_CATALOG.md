# HBnB Test Catalog

This document lists every automated test currently defined in the `tests/`
directory and summarizes the behavior each one verifies.

Current suite:

- 9 test files
- 129 automated tests

Helper methods, fixtures, and fake classes are not counted as tests.

## `tests/test_base_model.py`

### `TestBaseModel`

- `test_base_model_has_id_and_timestamps`
  - Verifies that a new base model receives a string UUID plus `created_at`
    and `updated_at` datetime values.
- `test_base_models_have_unique_ids`
  - Verifies that separate model instances receive different IDs.
- `test_save_updates_updated_at`
  - Verifies that `save()` refreshes the `updated_at` timestamp.
- `test_update_sets_existing_attributes`
  - Verifies that `update()` changes existing attributes and ignores unknown
    attributes.

## `tests/test_user.py`

### `TestUser`

- `test_create_valid_user`
  - Verifies valid user creation, default admin/active flags, and empty
    relationship lists.
- `test_user_trims_valid_string_fields`
  - Verifies trimming of names and trimming/lowercasing of email addresses.
- `test_user_rejects_empty_names`
  - Verifies that empty or whitespace-only first and last names are rejected.
- `test_user_rejects_non_string_names_and_email`
  - Verifies that first name, last name, and email must be strings.
- `test_user_rejects_names_longer_than_50_characters`
  - Verifies the 50-character maximum for first and last names.
- `test_user_accepts_names_at_50_character_boundary`
  - Verifies that first and last names of exactly 50 characters are accepted.
- `test_user_rejects_invalid_email_format`
  - Verifies rejection of empty, malformed, incomplete, and whitespace-bearing
    email addresses.
- `test_user_update_uses_validation`
  - Verifies that model updates still apply email validation.
- `test_user_to_dict_serializes_complete_model`
  - Verifies complete user serialization, including admin/active flags and ISO
    timestamps.
- `test_facade_user_update_rejects_unsupported_fields`
  - Verifies that unsupported user update fields, such as `is_admin`, are
    rejected and do not mutate the user.
- `test_facade_create_user_requires_password`
  - Verifies that facade user creation requires a password and leaves the
    repository unchanged when missing.
- `test_add_place`
  - Verifies that a place can be added to a user's owned places list.
- `test_add_review`
  - Verifies that a review can be added to a user's written reviews list.
- `test_facade_enforces_unique_email_in_memory`
  - Verifies that duplicate email addresses cannot be registered.
- `test_facade_normalizes_email_before_uniqueness_check`
  - Verifies that case and surrounding whitespace cannot bypass email
    uniqueness.
- `test_facade_updates_own_user_details`
  - Verifies that a user can update their own first and last name while email
    remains unchanged.
- `test_facade_rejects_update_for_another_user`
  - Verifies that one user cannot update another user's details.
- `test_facade_rejects_email_update`
  - Verifies that email updates through the user update facade raise
    `RestrictedUserFieldUpdate`.
- `test_facade_rejects_password_update`
  - Verifies that password updates through the user update facade raise
    `RestrictedUserFieldUpdate` and preserve the existing password hash.
- `test_facade_email_lookup_returns_none_when_missing`
  - Verifies that looking up an unknown email returns `None`.
- `test_facade_user_update_raises_when_user_is_missing`
  - Verifies that updating a missing user raises `UserNotFound`.
- `test_soft_delete_user_sets_inactive_flag`
  - Verifies that soft deletion deactivates a user without removing it from
    storage.
- `test_delete_user_hard_deletes_user`
  - Verifies permanent user deletion and subsequent `UserNotFound` behavior.

## `tests/test_amenity.py`

### `TestAmenity`

- `test_create_valid_amenity`
  - Verifies valid amenity creation.
- `test_amenity_trims_name`
  - Verifies removal of surrounding whitespace from amenity names.
- `test_amenity_rejects_empty_name`
  - Verifies rejection of empty and whitespace-only amenity names.
- `test_amenity_rejects_non_string_name`
  - Verifies that amenity names must be strings.
- `test_amenity_rejects_name_longer_than_50_characters`
  - Verifies the 50-character maximum for amenity names.
- `test_amenity_accepts_name_at_50_character_boundary`
  - Verifies that an amenity name of exactly 50 characters is accepted.
- `test_amenity_update_uses_validation`
  - Verifies that model updates still apply amenity name validation.
- `test_to_dict`
  - Verifies complete amenity serialization with ID and ISO timestamps.
- `test_facade_raises_when_amenity_is_not_found`
  - Verifies that retrieving or deleting a missing amenity raises
    `AmenityNotFound`.
- `test_facade_rejects_invalid_amenity_data`
  - Verifies invalid amenity create/update payloads are rejected.
- `test_update_raises_when_amenity_does_not_exist`
  - Verifies that updating a missing amenity raises `AmenityNotFound`.
- `test_facade_creates_and_updates_amenity`
  - Verifies facade creation trims names and update changes the amenity name.
- `test_facade_amenity_update_rejects_unsupported_fields`
  - Verifies unsupported amenity fields are rejected without partial mutation.

## `tests/test_place.py`

### `TestPlace`

- `test_create_valid_place`
  - Verifies valid place creation, default active flag, owner relationship, and
    empty review/amenity lists.
- `test_place_requires_user_owner`
  - Verifies that a place owner must be a `User` instance.
- `test_place_rejects_invalid_title`
  - Verifies rejection of empty, whitespace-only, and overlong place titles.
- `test_place_rejects_non_string_title`
  - Verifies that place titles must be strings.
- `test_place_trims_title`
  - Verifies removal of surrounding whitespace from place titles.
- `test_place_accepts_title_at_100_character_boundary`
  - Verifies that a title of exactly 100 characters is accepted.
- `test_place_rejects_non_positive_price`
  - Verifies rejection of zero, negative, boolean, and string prices.
- `test_place_validates_coordinate_ranges`
  - Verifies latitude and longitude range enforcement.
- `test_place_rejects_non_numeric_coordinates`
  - Verifies rejection of boolean and string coordinates.
- `test_place_accepts_coordinate_boundaries`
  - Verifies acceptance of latitude `-90`/`90` and longitude `-180`/`180`.
- `test_place_update_uses_validation`
  - Verifies that model updates still apply price validation.
- `test_add_review`
  - Verifies that a review can be added to a place.
- `test_add_amenity`
  - Verifies that an amenity can be added to a place.
- `test_place_to_dict_serializes_complete_model`
  - Verifies complete place serialization, including owner ID, amenity IDs,
    active flag, and ISO timestamps.
- `test_facade_validates_owner_exists_in_memory`
  - Verifies that creating a place for an unknown owner raises `UserNotFound`.
- `test_facade_place_update_rejects_unsupported_fields`
  - Verifies that `owner_id` cannot be changed through place updates.
- `test_facade_updates_place_fields`
  - Verifies owner-authorized updates to title, description, price, latitude,
    and longitude.
- `test_facade_rejects_place_update_by_non_owner`
  - Verifies that non-owner place updates raise `UnauthorizedAction` and do not
    mutate the place.
- `test_facade_rejects_place_update_without_authenticated_user`
  - Verifies that facade place updates require an authenticated user ID.
- `test_facade_replaces_and_clears_place_amenities`
  - Verifies owner-authorized amenity replacement and clearing via
    `amenity_ids`.
- `test_facade_rejects_unknown_amenity_without_changing_place`
  - Verifies that an unknown amenity ID raises `AmenityNotFound` without
    changing existing amenities.
- `test_facade_place_update_raises_when_place_is_missing`
  - Verifies that updating a missing place raises `PlaceNotFound`.
- `test_delete_place_hard_deletes_place`
  - Verifies permanent place deletion and missing-place behavior afterward.

## `tests/test_review.py`

### `TestReview`

- `test_create_valid_review`
  - Verifies valid review creation with text, rating, place, and user.
- `test_review_requires_place_and_user_instances`
  - Verifies that review relationships require `Place` and `User` instances.
- `test_review_rejects_empty_text`
  - Verifies rejection of empty and whitespace-only review text.
- `test_review_rejects_non_string_text`
  - Verifies that review text must be a string.
- `test_review_trims_text`
  - Verifies removal of surrounding whitespace from review text.
- `test_review_rejects_rating_outside_1_to_5`
  - Verifies rejection of ratings outside `1..5`, non-integers, booleans, and
    strings.
- `test_review_accepts_rating_boundaries`
  - Verifies that ratings `1` and `5` are accepted.
- `test_review_update_uses_validation`
  - Verifies that model updates still enforce rating validation.
- `test_review_to_dict_serializes_complete_model`
  - Verifies complete review serialization, including place/user IDs and ISO
    timestamps.
- `test_facade_review_update_only_changes_text_and_rating`
  - Verifies author-authorized review updates and relationship preservation.
- `test_facade_rejects_review_update_by_non_author`
  - Verifies that non-authors cannot update a review.
- `test_facade_review_update_rejects_unsupported_fields`
  - Verifies that review `user_id`, `place_id`, and `is_active` cannot be
    updated.
- `test_facade_validates_review_relationships_in_memory`
  - Verifies that reviews cannot be created for unknown places or users.
- `test_facade_links_review_to_place_and_user`
  - Verifies that review creation links the review to both place and user.
- `test_owner_cannot_review_own_place`
  - Verifies that owners cannot review their own places.
- `test_user_cannot_review_same_place_twice`
  - Verifies that a user cannot review the same place more than once.
- `test_reviews_can_be_listed_by_user`
  - Verifies facade filtering of reviews by author.
- `test_deleting_reviewer_preserves_review`
  - Verifies that soft-deleting a reviewer preserves reviews and relationships.
- `test_deleting_place_preserves_review`
  - Verifies that hard-deleting a place preserves the review record but makes
    place-review lookup fail for the deleted place.
- `test_deleting_owner_deactivates_owned_places`
  - Verifies that soft-deleting a place owner deactivates their owned places
    while preserving reviews.
- `test_deleting_review_unlinks_relationships`
  - Verifies that deleting a review removes it from the user and place
    relationship lists.
- `test_facade_rejects_review_delete_by_non_author`
  - Verifies that non-authors cannot delete reviews and relationships remain
    intact.

## `tests/test_repository.py`

### `TestInMemoryRepository`

- `test_find_one_returns_first_matching_object`
  - Verifies returning the first object matching all supplied filters.
- `test_find_one_returns_none_when_no_object_matches`
  - Verifies that `find_one()` returns `None` when no object matches.
- `test_find_all_filters_by_multiple_attributes`
  - Verifies filtered lookup using multiple attributes.
- `test_find_all_without_filters_returns_every_object`
  - Verifies that unfiltered lookup returns every stored object.
- `test_find_all_does_not_match_missing_attributes`
  - Verifies that objects lacking a requested attribute are not matched.
- `test_get_by_attribute_uses_dynamic_lookup`
  - Verifies lookup through a dynamically supplied attribute name.

## `tests/test_api_errors.py`

### `TestApiErrorHandlers`

- `test_registers_all_application_errors`
  - Verifies registration of all application error handlers, including domain,
    auth, business-rule, authorization, and validation errors.
- `test_not_found_handler_returns_404`
  - Verifies the standard error body and HTTP 404 for missing resources.
- `test_duplicate_email_handler_returns_400`
  - Verifies the duplicate-email error body and HTTP 400.
- `test_invalid_credentials_handler_returns_401`
  - Verifies invalid credentials return the standard error body and HTTP 401.
- `test_invalid_request_handler_returns_400`
  - Verifies business-rule and restricted-field errors return the standard body
    and HTTP 400.
- `test_forbidden_handler_returns_403`
  - Verifies unauthorized actions return the standard error body and HTTP 403.

## `tests/test_auth.py`

### `TestAuthUnit`

- `test_login_returns_token_with_user_identity_and_admin_claim`
  - Verifies `/login` delegates authentication to the facade and creates a JWT
    with the user ID identity plus the `is_admin` claim.
- `test_facade_authenticate_user_rejects_invalid_credentials`
  - Verifies facade authentication rejects incorrect passwords with
    `InvalidCredentials`.
- `test_protected_response_uses_current_identity_and_admin_claim`
  - Verifies the protected auth resource builds its response from
    `get_jwt_identity()` and JWT claims.

### `TestAuthIntegration`

- `test_login_token_allows_protected_request_with_expected_body`
  - Verifies login returns a usable JWT and `/api/v1/auth/protected` responds
    with the authenticated user ID and admin claim.
- `test_login_rejects_bad_password`
  - Verifies bad login credentials return HTTP 401 and the invalid credentials
    error body.
- `test_login_rejects_extra_request_fields`
  - Verifies login rejects request bodies containing fields beyond `email` and
    `password`.
- `test_protected_requires_jwt`
  - Verifies `/api/v1/auth/protected` returns HTTP 401 when no JWT is supplied.

## `tests/test_api_integration.py`

### `TestApiErrorHandlerIntegration`

- `test_not_found_and_validation_errors_use_global_handlers`
  - Verifies global API error bodies/statuses for missing users, places,
    amenities, reviews, and invalid amenity create/update payloads.
- `test_missing_mutation_and_nested_routes_return_404`
  - Verifies missing-resource responses for user, amenity, place, nested review,
    and review mutation/list routes.
- `test_conflict_and_business_rule_errors_use_global_handlers`
  - Verifies duplicate user registration returns HTTP 400 and owners cannot
    review their own places through the nested review route.
- `test_duplicate_review_attempt_returns_bad_request`
  - Verifies duplicate reviews return HTTP 400, the expected error body, and no
    extra review is stored.
- `test_jwt_protected_write_routes_require_token`
  - Verifies protected write routes return HTTP 401 when the Authorization
    header is missing:
    - `POST /api/v1/places/`
    - `PUT /api/v1/places/<place_id>`
    - `POST /api/v1/reviews/`
    - `POST /api/v1/places/<place_id>/reviews`
    - `PUT /api/v1/reviews/<review_id>`
    - `DELETE /api/v1/reviews/<review_id>`
    - `PUT /api/v1/users/<user_id>`
- `test_jwt_protected_write_routes_reject_invalid_tokens`
  - Verifies the same protected write routes reject malformed, tampered, and
    expired JWTs without mutating place, review, or user state.
- `test_place_get_routes_remain_public`
  - Verifies `GET /api/v1/places/` and `GET /api/v1/places/<place_id>` remain
    accessible without a JWT.
- `test_create_routes_use_jwt_identity_for_relationships`
  - Verifies place and review creation use the JWT identity instead of spoofed
    `owner_id` or `user_id` request-body values.
- `test_user_responses_exclude_internal_model_fields`
  - Verifies user create/get/update/list responses expose only public fields and
    that stored passwords are hashed.
- `test_user_update_allows_own_user_token`
  - Verifies a user can update their own first and last name with their JWT.
- `test_user_update_rejects_other_user_token`
  - Verifies updating another user's details returns HTTP 403 and leaves the
    target unchanged.
- `test_user_update_rejects_email_change`
  - Verifies user update rejects email changes with HTTP 400 and the restricted
    field error body.
- `test_user_update_rejects_password_change`
  - Verifies user update rejects password changes with HTTP 400 and preserves
    the existing password hash.
- `test_user_registration_hashes_password_and_hides_it`
  - Verifies registration hashes stored passwords and never exposes passwords in
    create/get responses.
- `test_amenity_and_review_responses_exclude_timestamps`
  - Verifies amenity and review API response schemas exclude timestamps,
    amenity/review updates succeed, and place review listing has the expected
    public fields.
- `test_hard_delete_routes`
  - Verifies `DELETE /api/v1/users/<user_id>` permanently deletes a user and
    returns the expected success body.
- `test_review_update_rejects_user_and_place_changes`
  - Verifies review updates reject attempts to change `user_id` or `place_id`.
- `test_updates_reject_unsupported_fields`
  - Verifies unsupported user, amenity, and place update fields return HTTP 400
    and do not mutate stored state.
- `test_place_delete_route_hard_deletes_place`
  - Verifies `DELETE /api/v1/places/<place_id>` removes the place and later
    retrieval returns HTTP 404.
- `test_place_update_route_succeeds`
  - Verifies place owners can update their place and receive the expected
    success body.
- `test_place_update_by_non_owner_returns_forbidden`
  - Verifies non-owner place updates return HTTP 403 with
    `{"error": "Unauthorized action"}` and do not mutate the place.
- `test_place_list_and_nested_review_creation_routes`
  - Verifies place listing and authenticated nested review creation, including
    response fields and JWT-derived reviewer ID.
- `test_amenity_and_review_delete_routes`
  - Verifies amenity deletion and author-authorized review deletion remove the
    records and return expected success bodies.
- `test_review_update_and_delete_by_non_author_return_forbidden`
  - Verifies non-authors cannot update or delete reviews and receive the
    standard unauthorized error body.
- `test_place_details_include_nested_relationships`
  - Verifies place detail responses include nested owner, amenities, and reviews
    in the expected public shape.
