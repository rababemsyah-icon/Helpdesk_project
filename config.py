import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre-cle-secrete-par-defaut'
    
    # Remplacez la ligne ci-dessous : 
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Par celle-ci (utilise SQLite par défaut si la variable n'existe pas)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///helpdesk.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False