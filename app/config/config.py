import os

user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
database = os.getenv('PG_DB')
port = os.getenv('PG_PORT')

insta_email = os.getenv('INSTA_EMAIL')
insta_password = os.getenv('INSTA_PASSWORD')

DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

INSTA_CONFIG = {
    'email':insta_email,
    'password':insta_password
}