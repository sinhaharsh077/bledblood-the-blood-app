from .database import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from datetime import datetime

class Badges(db.Model):
	__tablename__ = 'badges'
	badge_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	badge_name = db.Column(db.Text, unique = True)
	badge_description = db.Column(db.Text, unique = False)
	badge_image = db.Column(db.LargeBinary)
	badge_count_required = db.Column(db.Integer)

	def __repr__(self):
        	return f'<Badge {self.badge_name}>'

class Badges_Users_Association(db.Model):
	__tablename__= 'user_badges'
	user_username = db.Column(db.Text, db.ForeignKey('users.username',ondelete = 'CASCADE'), primary_key=True)
	badge_id = db.Column(db.Integer, db.ForeignKey('badges.badge_id', ondelete = 'CASCADE'), primary_key=True)
	badge_earned_date = db.Column(db.DateTime, default=datetime.utcnow)

	#many to many attribute.

	user = db.relationship('Users', backref=db.backref('badge_associations', lazy='dynamic'))
	badge = db.relationship('Badges', backref=db.backref('user_associations', lazy='dynamic'))


class Bloodbank(db.Model):
	__tablename__ = 'bloodbank'
	bank_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	bank_pincode = db.Column(db.Integer, unique = False)
	bank_name = db.Column(db.Text, unique = False)
	bank_address = db.Column(db.Text)

	def __repr__(self):
        	return f"<BloodBank(id={self.bank_id}, name={self.bank_name}, pincode={self.bank_pincode})>"
	

class Users(db.Model):
	__tablename__ = 'users'
	username = db.Column(db.Text, autoincrement = False, primary_key = True)
	pswd = db.Column(db.Text, nullable = False)
	blood_group = db.Column(db.Text, nullable = False)
	fname = db.Column(db.Text)
	lname = db.Column(db.Text)
	age = db.Column(db.Integer)
	pincode = db.Column(db.Integer)
	comorbidities = db.Column(db.Integer)
	Gender = db.Column(db.Text)
	email = db.Column(db.Text)
	donation_count = db.Column(db.Integer, default = 0) 


class BloodstatW(db.Model):
	__tablename__ = 'blood_status_WEAK'
	bank_id = db.Column(db.Integer, db.ForeignKey('bloodbank.bank_id'), primary_key = True, nullable = False)
	A_pos = db.Column(db.Integer, default = 0)
	AB_pos = db.Column(db.Integer, default = 0)
	B_pos = db.Column(db.Integer, default = 0)
	O_pos = db.Column(db.Integer, default = 0)
	A_neg = db.Column(db.Integer, default = 0)
	AB_neg = db.Column(db.Integer, default = 0)
	B_neg = db.Column(db.Integer, default = 0)
	O_neg = db.Column(db.Integer, default = 0)
	bs_id = db.Column(db.Integer, unique = True, nullable = True)
 
class DonationRequests(db.Model):
	__tablename__ = 'donationrequests'
	Req_id = db.Column(db.Integer, autoincrement = True, primary_key = True, nullable = False)
	Received_date = db.Column(db.Date, default = datetime.today(), nullable=False)
	Received_from = db.Column(db.Text, db.ForeignKey('users.username', ondelete = 'CASCADE'), nullable = False)
	Req_status = db.Column(db.Text, default = 'pending')
	Received_by = db.Column(db.Integer,db.ForeignKey('bloodbank.bank_id', ondelete = 'CASCADE'), nullable = False)
	Response_date = db.Column(db.Date, nullable = True)
	rejected_msg = db.Column(db.Text, nullable = True)
	
	user = db.relationship("Users", backref=db.backref("donationrequests", uselist=False))