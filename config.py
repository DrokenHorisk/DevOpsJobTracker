import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
SQLALCHEMY_DATABASE_URI = "sqlite:////app/instance/devopsjobs.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
