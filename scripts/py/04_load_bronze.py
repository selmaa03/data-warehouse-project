'''
STEP 4:
This script connects to the SQL Server database via Azure Data Studio.
It pulls raw CSV files directly from cloud storage (AWS S3) and securely stream them
into the 'bronze' schema of the Data Warehouse.

This is our Raw Ingestion phase in Medallion Architecture, where we keep an exact, unchanged
record of the source data for auditing and reprocessing before applying any transformations.
'''

import boto3
import pyodbc
import pandas as pd
import config

s3 = boto3.client(
    's3',
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
)

S3_BUCKET_NAME = 'dwh-olist-bucket'

# fill  with your connection
conn_str = (
    'DRIVER={...............};'
    'SERVER=.................;'
    'DATABASE=...............;'
    'UID=.........;'
    'PWD=.........;'
    'TrustServerCertificate=yes;'
)

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
    connection = pyodbc.connect(conn_str)
    cursor = connection.cursor()
    cursor.fast_executemany = True
    print('Connection Successful!')

    for s3_key, table_name in datasets.items():
        print(f'\nDownloading {s3_key} from S3...')
        s3_object = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        df = pd.read_csv(s3_object['Body'])

        print(f'Preparing data formatting for {table_name}...')
        df = df.astype(object)
        df = df.where(pd.notnull(df), None)

        print(f'Inserting {len(df)} rows into {table_name}...')

        columns = ', '.join(df.columns)
        placeholders = ', '.join(['?'] * len(df.columns))
        insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

        rows = [tuple(x) for x in df.to_numpy()]
        cursor.executemany(insert_query, rows)
        connection.commit()

        print(f'{table_name} is fully loaded')

    print('All files successfully loaded.')

except Exception as e:
    print(f'Error: {e}')

finally:
    try:
        cursor.close()
        connection.close()
    except Exception:
        pass
