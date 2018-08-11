from app import db
from app import bcrypt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

eid_to_ename = [
    "Unknown",
    "KnobEx",
    "TorqueEx",
    "TorqueUDEx",
    "pbdUGIBiopsyEx",
    "pbdUGISnareEx",
    "pbdUGIExamEx",
]

ename_to_eid = dict((n,i) for i,n in enumerate(eid_to_ename))


class Report(db.Model):

    __tablename__ = "ExerciseReports"

    rid = db.Column(db.Integer, primary_key=True)
    eid = db.Column(db.Integer, nullable=False)
    report = db.Column(db.String, nullable=False)
    uid = db.Column(db.Integer, ForeignKey('Users.uid'))

    @property
    def ename(self):
        return eid_to_ename[self.eid]

    def __init__(self, eid, report, uid):
        self.eid = eid
        self.report = report
        self.uid = uid


    def __repr__(self):
        return '<title {}'.format(self.eid)

class User(db.Model):

    __tablename__ = "Users"

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True, nullable=False)
    email = db.Column(db.String,unique=True, nullable=True)
    password = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String, nullable=True)
    usertype = db.Column(db.String, nullable = False)
    reports = relationship("Report", backref="user")

    def __init__(self, username, password, usertype , email = None, gender = None):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.gender = gender
        self.usertype = usertype

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.uid)

    def __repr__(self):
        return '<name {}'.format(self.username)
