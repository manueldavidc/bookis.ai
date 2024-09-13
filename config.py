import os

class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require'.format(
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        host=os.environ.get('PGHOST'),
        port=os.environ.get('PGPORT'),
        database=os.environ.get('PGDATABASE')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
