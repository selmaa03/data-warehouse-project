'''
STEP 1:
The config.py file (The Gatekeeper): This script uses a Python library called python-dotenv to
read .env file and expose those variables to the rest of your application safely.

By building config.py, your ingestion, transformation, and loading scripts can simply import
it to get database passwords or AWS keys without hardcoding them.
'''

# config.py
import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load variables from the .env file
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError('AWS credentials are missing from your .env file!')

if not S3_BUCKET_NAME:
    raise ValueError('S3_BUCKET_NAME is missing from your .env file!')


# database config
DB_SERVER = os.getenv('DB_SERVER')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

if not all([DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError('Database connection credentials (SERVER/NAME/USER/PASSWORD) are missing from your .env file!')

def get_db_engine():
    # Safe-encode password to handle any special characters seamlessly
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

    # Connection string structured for SQL Server Authentication (SQL Login)
    connection_string = (
        f"mssql+pyodbc://{DB_USER}:{encoded_password}@{DB_SERVER}/{DB_NAME}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&Encrypt=yes"
        "&TrustServerCertificate=yes"
    )

    return create_engine(connection_string)
