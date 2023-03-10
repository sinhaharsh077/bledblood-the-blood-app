from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

engine = None
Base = declarative_base()
db = SQLAlchemy()      