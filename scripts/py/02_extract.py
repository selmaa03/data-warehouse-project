'''
STEP 2 :
This strict is to pull from source and dump raw data to S3.

Boto 3 -> Boto3 is the official Amazon Web Services (AWS) Software Development Kit (SDK) for Python.
It allows developers to directly interact with and manage AWS services—such as S3, EC2, and DynamoDB—using Python code.
for more info about S3 service, check: https://docs.aws.amazon.com/boto3/latest/reference/services/s3.html
'''

import os
import glob
import boto3
import config
import time

def upload_to_s3_bronze():

    start_time = time.perf_counter()

    s3 = boto3.client(
        's3',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
    )

    FOLDER_NAME = "raw-data-folder"
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    search_path = os.path.join(base_dir, "datasets", "raw", "*.csv")

    csv_files = glob.glob(search_path)
    if not csv_files:
        print(f"Warning: No CSV files found in path: {search_path}")
        return

    print(f"Found {len(csv_files)} files to upload...")

    for filepath in csv_files:
        filename = os.path.basename(filepath)
        s3_key = f"{FOLDER_NAME}/{filename}"
        print(f"Uploading {filename} to s3://{config.S3_BUCKET_NAME}/{s3_key}")

        try:
            s3.upload_file(filepath, config.S3_BUCKET_NAME, s3_key)
        except Exception as e:
            print(f"Failed to upload {filename}. Error: {e}")
            continue

    print(f"All available files uploaded to data lake: {config.S3_BUCKET_NAME}")

    end_time = time.perf_counter()
    total_duration = end_time - start_time

    print(f"Total load duration: {total_duration} seconds")

if __name__ == "__main__":
    upload_to_s3_bronze()
