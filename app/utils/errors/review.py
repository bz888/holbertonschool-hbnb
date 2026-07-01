class ReviewNotFound(Exception):
    """Raised when a review cannot be found."""

    def __init__(self, review_id):
        super().__init__(f"Review '{review_id}' not found")


class OwnerCannotReviewOwnPlace(Exception):
    """Raised when a place owner attempts to review their own place."""

    def __init__(self):
        super().__init__("You cannot review your own place.")


class DuplicateReview(Exception):
    """Raised when a user attempts to review the same place twice."""

    def __init__(self):
        super().__init__("You have already reviewed this place.")
