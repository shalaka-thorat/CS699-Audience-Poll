from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property


'''
Flask-login requires a User model with the following properties:

    has an is_authenticated() method that returns True if the user has provided valid credentials
    has an is_active() method that returns True if the user's account is active
    has an is_anonymous() method that returns True if the current user is an anonymous user
    has a get_id() method which, given a User instance, returns the unique ID for that object

UserMixin class provides the implementation of this properties. 
Its the reason you can call for example is_authenticated to check if login credentials provide is correct or not instead of having to write a method to do that yourself.
'''

# email and password shouldn't be greater than 500 characters
# otherwise a malicious user may try to fill up our server space by putting arbitrary large strings
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(500), unique=True, nullable=False)
    password_hash = db.Column(db.String(500), unique=True, nullable=False) # store the hash password
    age=db.Column(db.Integer, nullable=False)
    gender=db.Column(db.String(10), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    polls = db.relationship('Poll', backref='creator', lazy=True, cascade="all, delete")
    votes = db.relationship('Vote', backref='voter', lazy=True, cascade="all, delete")
    # vote_history = db.relationship('UserVoteHistory', backref='user', lazy=True, cascade="all, delete")
    poll_reports = db.relationship('UserPollReport', backref='user', lazy=True, cascade="all, delete")

class Poll(db.Model):
    __tablename__ = 'poll'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at =db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='active')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)
    
    options = db.relationship('Option', backref='poll', cascade="all, delete",lazy=True)
    votes = db.relationship('Vote', backref='poll', cascade="all,delete", lazy=True)
    # vote_history = db.relationship('UserVoteHistory', backref='poll', cascade="all,delete", lazy=True)
    poll_reports = db.relationship('UserPollReport', backref='poll', lazy=True, cascade="all, delete")
    
    @hybrid_property
    def vote_count(self):
        return len(self.votes)
    
    @hybrid_property
    def creator_username(self):
        creator = User.query.get(self.user_id)
        name, _, _ =creator.email.rpartition('@')
        return name
            
            
    
class Option(db.Model):
    __tablename__ = 'option'
    id= db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    
    votes = db.relationship('Vote', backref='option', cascade="all, delete", lazy=True)
    
    @hybrid_property
    def vote_count(self):
        return len(self.votes)
    
class Vote(db.Model):
    __tablename__ = 'vote'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    voted_at = db.Column(db.DateTime, default=datetime.now)

# class UserVoteHistory(db.Model):
#     __tablename__ = 'user_vote_history'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
#     vote_id = db.Column(db.Integer, db.ForeignKey('vote.id'), nullable=False)
    
class UserPollReport(db.Model):
    __tablename__= 'user_poll_report'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    