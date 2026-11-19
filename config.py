import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'placement-readiness-secret-key-2026')
    DATABASE_PATH = os.path.join(BASE_DIR, 'placement_readiness.db')
    MODEL_PATH = os.path.join(BASE_DIR, 'placement_model.joblib')
    DEBUG = True
