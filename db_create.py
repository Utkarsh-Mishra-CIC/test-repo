from app import db
from models import *

# create the database and the db table
db.create_all()

db.session.add(User("A","a@a.com","1234"))
# insert data
db.session.add(BlogPost("Good", "I\'m good.", 1))
db.session.add(BlogPost("Well", "I\'m well.", 1))
db.session.add(BlogPost("Excellent", "I\'m excellent.", 1))
db.session.add(BlogPost("Okay", "I\'m okay.", 1))

# commit the changes
db.session.commit()