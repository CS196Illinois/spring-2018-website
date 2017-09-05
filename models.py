from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

db = SQLAlchemy()

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  netid = db.Column(db.String(8))
  signins = db.relationship('Signin', backref='user', lazy='dynamic')

  def get_dict(self):
    return {
      'id': self.id,
      'netid': str(self.netid),
      'signins': self.signins.count()
    }

class Session(db.Model):
  __tablename__ = 'sessions'
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.DateTime)
  alive = db.Column(db.Boolean)
  signins = db.relationship('Signin', backref='session', lazy='dynamic')

  def get_dict(self):
    return {
      'id': self.id,
      'date': self.date,
      'alive': self.alive,
      'signins': self.signins.count()
    }

class Signin(db.Model):
  __tablename__ = 'signins'
  id = db.Column(db.Integer, primary_key=True)
  userid = db.Column(db.Integer, db.ForeignKey('users.id'))
  sessionid = db.Column(db.Integer, db.ForeignKey('sessions.id'))

