'''
STEP 1 :
The config.py file (The Gatekeeper): This script uses a Python library called python-dotenv to read .env file 
and expose those variables to the rest of your application safely.

By building config.py, your ingestion, transformation, and loading scripts can simply import it to get 
database passwords or AWS keys without hardcoding them.
'''

# config.py
import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("AWS credentials are missing from your .env file!")

if not S3_BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME is missing from your .env file!")
