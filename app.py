import os, application.config
from application.config import LocalDevelopmentConfig
from flask import Flask
from application.database import db


app = None

def create_app():
	app = Flask(__name__, template_folder = "templates", static_folder="static")
	app.secret_key = "thisissecret"
	if (os.getenv('ENV', "development") == "production"):
		raise Exception("Currently no production config is setup.")
	else:
		print("Starting Local Development")
		app.config.from_object(LocalDevelopmentConfig)
	db.init_app(app)
	app.app_context().push()
	return app
app = create_app()
from application.controllers import *

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080)