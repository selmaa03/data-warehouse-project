'''
STEP 4:
This script connects to the SQL Server database via Azure Data Studio.
It pulls raw CSV files directly from cloud storage (AWS S3) and securely stream them
into the 'bronze' schema of the Data Warehouse.

This is our Raw Ingestion phase in Medallion Architecture, where we keep an exact, unchanged
record of the source data for auditing and reprocessing before applying any transformations.
'''

import boto3
import pandas as pd
import logging
import config
from config import get_db_engine
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

s3 = boto3.client(
    's3',
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
)

S3_BUCKET_NAME = 'dwh-olist-bucket'

datasets = {
    'raw-data-folder/olist_customers_dataset.csv': 'bronze.customers',
    'raw-data-folder/olist_geolocation_dataset.csv': 'bronze.geolocation',
    'raw-data-folder/olist_sellers_dataset.csv': 'bronze.sellers',
    'raw-data-folder/product_category_name_translation.csv': 'bronze.catogary_name_translation',
    'raw-data-folder/olist_orders_dataset.csv': 'bronze.orders',
    'raw-data-folder/olist_products_dataset.csv': 'bronze.products',
    'raw-data-folder/olist_order_items_dataset.csv': 'bronze.order_items',
    'raw-data-folder/olist_order_payments_dataset.csv': 'bronze.order_payments',
    'raw-data-folder/olist_order_reviews_dataset.csv': 'bronze.order_reviews'
}

try:
    engine = get_db_engine()
    logging.info('Connection Successful!')

    for s3_key, table_name in datasets.items():
        logging.info(f'\nDownloading {s3_key} from S3...')
        s3_object = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        df = pd.read_csv(s3_object['Body'])

        schema, table = table_name.split('.')

        logging.info(f'Truncating {table_name} to ensure a fresh load...')
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {schema}.{table}"))

        logging.info(f'Inserting {len(df)} rows into {table_name}...')
        df.to_sql(
            name=table,
            con=engine,
            schema=schema,
            if_exists='append',
            index=False,
            chunksize=1000
        )

        logging.info(f'{table_name} is fully loaded')

    logging.info('All files successfully loaded.')

except Exception as e:
    logging.error(f'Error: {e}')
