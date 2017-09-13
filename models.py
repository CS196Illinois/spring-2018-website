from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

db = SQLAlchemy()

class Homework(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(8))
  questions = db.relationship('Question', backref='homework', lazy='dynamic')
  description = db.Column(db.String(50))
  opendate = db.Column(db.Integer)
  closedate = db.Column(db.Integer)
  active = db.Column(db.Boolean)

class Question(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  parent_homework = db.Column(db.Integer, db.ForeignKey('homework.id'))
  netid = db.Column(db.String(8))
  runtime = db.Column(db.String(8))
  submitted = db.Column(db.String(12))

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

