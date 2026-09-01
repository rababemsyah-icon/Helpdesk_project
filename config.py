import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre-cle-secrete-par-defaut'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///helpdesk.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False