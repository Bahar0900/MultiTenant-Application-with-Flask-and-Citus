import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:mysecretpassword@localhost:5432/postgres?sslmode=disable'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
