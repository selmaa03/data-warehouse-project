'''
STEP 4:
This script connects to SQL Server using SQLAlchemy.
It supports loading raw CSV files from either a local directory or AWS S3 into the Bronze schema.

This represents the Raw Ingestion phase of the Medallion Architecture, preserving source data for auditing
and reprocessing before applying transformations.
'''

import logging
import os
import boto3
import pandas as pd
import config
from config import get_db_engine
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
local_data_folder = os.path.join(base_dir, 'datasets', 'raw')

S3_BUCKET_NAME = 'dwh-olist-bucket'
DATA_SOURCE = 'local'  # Change to 's3' if AWS is available

datasets = {
    'olist_customers_dataset.csv': 'bronze.customers',
    'olist_geolocation_dataset.csv': 'bronze.geolocation',
    'olist_sellers_dataset.csv': 'bronze.sellers',
    'product_category_name_translation.csv': 'bronze.catogary_name_translation',
    'olist_orders_dataset.csv': 'bronze.orders',
    'olist_products_dataset.csv': 'bronze.products',
    'olist_order_items_dataset.csv': 'bronze.order_items',
    'olist_order_payments_dataset.csv': 'bronze.order_payments',
    'olist_order_reviews_dataset.csv': 'bronze.order_reviews',
}

engine = None

try:
  engine = get_db_engine()
  logging.info('Connection Successful!')

  for file_name, table_name in datasets.items():
    if DATA_SOURCE == 'local':
      logging.info(f'Reading {file_name} locally from datasets/raw...')
      file_path = os.path.join(local_data_folder, file_name)
      df = pd.read_csv(file_path)

    elif DATA_SOURCE == 's3':
      logging.info(f'Downloading {file_name} from S3...')
      s3 = boto3.client(
          's3',
          aws_access_key_id=config.AWS_ACCESS_KEY_ID,
          aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
      )
      s3_object = s3.get_object(Bucket=S3_BUCKET_NAME, Key=f'raw-data-folder/{file_name}')
      df = pd.read_csv(s3_object['Body'])

    schema, table = table_name.split('.')

    with engine.begin() as conn:
      logging.info(f'Truncating {table_name}...')
      conn.execute(text(f'TRUNCATE TABLE {schema}.{table}'))

      logging.info(f'Inserting {len(df)} rows into {table_name}...')
      df.to_sql(
          name=table,
          con=conn,
          schema=schema,
          if_exists='append',
          index=False,
          chunksize=1000,
      )

    logging.info(f'{table_name} is fully loaded.')

  logging.info('All files successfully loaded.')

except Exception:
  logging.exception('Error during Bronze ingestion.')

finally:
  if engine is not None:
    engine.dispose()
