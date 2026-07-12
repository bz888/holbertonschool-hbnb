from __init__ import create_app
from extensions import db

from models.user import User
from models.place import Place
from models.review import Review
from models.amenity import Amenity


app = create_app()

with app.app_context():
    db.create_all()

    print("Database tables created:")
    print(db.metadata.tables.keys())

# to delete db, go to root folder
# check if db exists 'ls instance'
# rm instance/development.db