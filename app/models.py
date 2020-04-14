from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    strava_code = db.Column(db.String())
    access_token = db.Column(db.String())
    refresh_token = db.Column(db.String())
    expires_at = db.Column(db.String())
    timenow = db.Column(db.String(128))
    athlete_id = db.Column(db.Integer)
    number_of_activities = db.Column(db.Integer)
    activities = db.relationship('Activity', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.String(140))
    name = db.Column(db.String(140))
    activity_type = db.Column(db.String(64))
    epoch = db.Column(db.Integer)
    timenow = db.Column(db.String(140))
    timestamp = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    elevation = db.Column(db.String(64))
    distance = db.Column(db.String(64))
    duration = db.Column(db.String(64))
    max_speed = db.Column(db.String(64))
    avg_speed = db.Column(db.String(64))
    max_power = db.Column(db.String(64))
    avg_power = db.Column(db.String(64))
    max_heartrate = db.Column(db.String(64))
    avg_heartrate = db.Column(db.String(64))
    name_id = db.Column(db.String(128))
    is_commute = db.Column(db.Boolean())
    start_lat = db.Column(db.String(64))
    start_lng = db.Column(db.String(64))
    end_lat = db.Column(db.String(64))
    end_lng = db.Column(db.String(64))
    streams = db.Column(db.JSON())
    maxs = db.Column(db.JSON())
    icon_url = db.Column(db.String(128))
    altitude_url = db.Column(db.String(128))

    def __repr__(self):
        return '<Activity {}>'.format(self.name)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))