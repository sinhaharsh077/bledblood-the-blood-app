from .database import db

class User(db.Model):
	__tablename__ = 'user'
	user_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	username = db.Column(db.String, unique = True)
	email = db.Column(db.String, unique = True)
	#abilities = relationship("Ability", secondary = "user_ability")

class Ability(db.Model):
	__tablename__ = 'ability'
	ability_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	name = db.Column(db.String)
	proficiency = db.Column(db.Integer)
	users = db.relationship("User", secondary = "user_ability")

class User_Ability(db.Model):
	__tablename__ = 'user_ability'
	user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), primary_key = True, nullable = False)
	ability_id = db.Column(db.Integer, db.ForeignKey("ability.ability_id"), primary_key = True, nullable = False)