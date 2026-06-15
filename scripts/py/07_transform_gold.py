'''
Step 7:
This script is designed to model a Star Schema.
It pulls data from Silver layer which is already processed data, transform as fact or dimension tables
and securely stream/load them into AWS S3 bucket(gold-data-folder) of Datalake.

DuckDB -> DuckDB is an open-source column-oriented relational database, in-process SQL database management
system specifically built for Online Analytical Processing (OLAP).
'''

import duckdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

silver_category_name_translation_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/catogary_name_translation/catogary_name_translation_clean.parquet')
silver_customers_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/customers/customers_clean.parquet')
#silver_geolocation_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/geolocation/geolocation_clean.parquet')
silver_order_items_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/order_items/order_items_clean.parquet')
silver_order_payments_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/order_payments/order_payments_clean.parquet')
#silver_order_reviews_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/order_reviews/order_reviews_clean.parquet')
silver_orders_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/orders/orders_clean.parquet')
silver_products_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/products/products_clean.parquet')
silver_sellers_df = pd.read_parquet('s3://dwh-olist-bucket/processed-data-folder/sellers/sellers_clean.parquet')


# FACT TABLE
fact_sales_df = duckdb.sql(
    '''
    WITH aggregated_payments AS (
        SELECT 
            order_id,
            SUM(payment_value) AS total_payment_value
        FROM silver_order_payments_df
        GROUP BY order_id
    )
    SELECT
        oi.order_id,
        oi.order_item_id,
        o.customer_id,
        oi.product_id,
        oi.seller_id,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        oi.price,
        oi.freight_value,
        COALESCE(ap.total_payment_value, 0) AS total_payment_value
    FROM silver_order_items_df as oi
    INNER JOIN silver_orders_df as o
        ON oi.order_id = o.order_id
    LEFT JOIN aggregated_payments as ap
        ON oi.order_id = ap.order_id
    ORDER BY o.order_purchase_timestamp DESC
    '''
).df()


# DIMENSION TABLES
dim_customers_df = duckdb.sql(
    '''
    SELECT 
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    FROM silver_customers_df
    '''
).df()

dim_sellers_df = duckdb.sql(
    '''
    SELECT 
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state
    FROM silver_sellers_df
    '''
).df()

dim_products_df = duckdb.sql(
    '''
    SELECT 
        p.product_id,
        COALESCE(t.product_category_name_english, p.product_category_name) AS product_category_name,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM silver_products_df p
    LEFT JOIN silver_category_name_translation_df t 
        ON p.product_category_name = t.product_category_name
    '''
).df()

fact_sales_df.to_parquet("s3://dwh-olist-bucket/gold-data-folder/fact_sales.parquet", index=False)
dim_customers_df.to_parquet("s3://dwh-olist-bucket/gold-data-folder/dim_customers.parquet", index=False)
dim_sellers_df.to_parquet("s3://dwh-olist-bucket/gold-data-folder/dim_sellers.parquet", index=False)
dim_products_df.to_parquet("s3://dwh-olist-bucket/gold-data-folder/dim_products.parquet", index=False)

print("Gold layer successfully uploaded into S3")
