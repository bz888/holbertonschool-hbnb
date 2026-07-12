from models.user import User
from persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        """Return the user matching a normalized email address."""
        return self.find_one(email=email)
