'''
Step 6:
This script connects to the SQL Server database via Azure Data Studio.
It pulls data from Silver Schema and securely stream them into
AWS S3 bucket(processed-data-folder) of Datalake.

In the Validation and Synchronization phase of Medallion Architecture, we take cleaned,
organized data from our relational warehouse and store it in a centralized,
cloud-based Silver Data Lake for long-term storage.
'''

import io
import time
import logging
import boto3
import pandas as pd
import config
from config import get_db_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def upload_to_s3_silver():

    start_time = time.perf_counter()

    s3 = boto3.client(
        's3',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
    )

    S3_BUCKET_NAME = 'dwh-olist-bucket'
    FOLDER_NAME = 'processed-data-folder'

    silver_tables = [
        'customers',
        'catogary_name_translation',
        'sellers',
        'geolocation',
        'orders',
        'products',
        'order_items',
        'order_payments',
        'order_reviews'
    ]

    try:
        engine = get_db_engine()
        logging.info('Database Connection Successful!')

        for table_name in silver_tables:
            try:
                logging.info(f"Extracting table: silver.{table_name}")
                query = f"SELECT * FROM silver.{table_name}"

                df = pd.read_sql(query, con=engine)
                logging.info(f"Fetched {len(df)} rows from silver.{table_name}")

                parquet_buffer = io.BytesIO()
                df.to_parquet(parquet_buffer, index=False, engine='pyarrow', compression='snappy')
                s3_key = f"{FOLDER_NAME}/{table_name}/{table_name}_clean.parquet"

                s3.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=parquet_buffer.getvalue()
                )
                logging.info(f"Successfully streamed Parquet to s3://{S3_BUCKET_NAME}/{s3_key}\n")

                # --- If you want CSV :---
                # csv_buffer = io.StringIO()
                # df.to_csv(csv_buffer, index=False)
                # s3_key = f"{FOLDER_NAME}/{table_name}_silver_export.csv"
                # s3.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=csv_buffer.getvalue())

            except Exception as e:
                logging.error(f"Error processing table {table_name}: {e}\n")

    except Exception as e:
        logging.error(f'Error connecting to database: {e}')

    end_time = time.perf_counter()
    total_duration = end_time - start_time
    logging.info(f'Total load duration: {total_duration:.2f} seconds')

if __name__ == '__main__':
    upload_to_s3_silver()
