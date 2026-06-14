'''
Step 5:
This script:
- Reads your bronze CSV data.
- Checks for NULLs and Duplicates in Primary Key. ( Expectation: No Result )
- Drops duplicates and rows missing critical IDs or timestamps.
- Converts all relevant timestamp columns to pandas datetime (handling nulls).
- Filters out canceled orders (if any).
- Renames columns to more standardized silver layer names.
- Load transformed data into sql server silver schema.
'''

import logging
import pandas as pd
from sqlalchemy import text
from config import get_db_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def clean_orders(engine):

    logging.info(">>> Beginning Processing for Table: silver.orders")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.orders"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Trim trailing/leading spaces from string IDs and statuses, and handling NULLs
    df['order_id'] = df['order_id'].astype(str).str.strip()
    df['customer_id'] = df['customer_id'].astype(str).str.strip()
    df['order_status'] = df['order_status'].fillna('unknown').astype(str).str.strip().str.lower()

    # Filtering for canceled orders
    initial_count = len(df)
    df = df[df['order_status'] != 'canceled']
    canceled_count = initial_count - len(df)
    if canceled_count > 0:
        logging.warning(f"Filtered out {canceled_count} canceled orders.")

    # Convert NVARCHAR date strings to actual Pandas Datetime objects
    date_columns = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')  # 'coerce' turns invalid dates into NaT (NULL)

    # Drop rows missing
    df = df.dropna(subset=['order_purchase_timestamp'])

    # Remove duplicates based on Primary Key (order_id)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['order_id'], keep='first')
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        logging.warning(f"Removed {duplicate_count} duplicate order records.")

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.orders;"))

    logging.info("Loading data into silver.orders...")
    # 'append' preserves the table structure we defined in ddl_silver.sql
    df.to_sql(
        name='orders',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows into silver.orders!\n")



def clean_catogary_name_translateion(engine):

    logging.info(">>> Beginning Processing for Table: silver.catogary_name_translation")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.catogary_name_translation"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Drop rows where the Primary Key is missing entirely
    df = df.dropna(subset=['product_category_name'])

    # Trim trailing/leading spaces and lowercase, and Handling NULLs
    df['product_category_name'] = df['product_category_name'].astype(str).str.strip().str.lower()
    df['product_category_name_english'] = df['product_category_name_english'].fillna('unknown').astype(str).str.strip().str.lower()

    # Handle missing values
    df['product_category_name_english'] = df['product_category_name_english'].fillna('unknown')

    # Drop duplicate primary key
    df = df.drop_duplicates(subset=['product_category_name'])

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.catogary_name_translation;"))

    logging.info("Loading data into silver.catogary_name_translation...")
    df.to_sql(
        name='catogary_name_translation',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows silver.catogary_name_translation!\n")



def clean_customers(engine):

    logging.info(">>> Beginning Processing for Table: silver.customers")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.customers"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Drop rows missing the Primary Key
    df = df.dropna(subset=['customer_id'])

    # Trim trailing/leading spaces and format text upper for state and capitalize for city, and handling NULLs
    df['customer_id'] = df['customer_id'].astype(str).str.strip()
    df['customer_unique_id'] = df['customer_unique_id'].astype(str).str.strip()
    df['customer_state'] = df['customer_state'].fillna('UN').astype(str).str.strip().str.upper()
    df['customer_city'] = df['customer_city'].fillna('Unknown').astype(str).str.strip().str.title()

    # Clean zip code prefixes (cast to string, remove decimal artifact if read as float)
    if 'customer_zip_code_prefix' in df.columns:
        df['customer_zip_code_prefix'] = df['customer_zip_code_prefix'].fillna('00000').astype(str).str.split('.').str[0].str.strip().str.zfill(5)

    # Remove duplicates based on Primary Key (customer_id)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['customer_id'], keep='first')
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        logging.warning(f"Removed {duplicate_count} duplicate customer records.")

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.customers;"))

    logging.info("Loading data into silver.customers...")
    df.to_sql(
        name='customers',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows into silver.customers!\n")



def clean_geolocation(engine):

    logging.info(">>> Beginning Processing for Table: silver.geolocation")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.geolocation"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Drop rows missing the Primary Key
    df = df.dropna(subset=['geolocation_zip_code_prefix'])

    # Clean zip code prefixes (cast to string, remove decimal artifact if read as float)
    if 'geolocation_zip_code_prefix' in df.columns:
        df['geolocation_zip_code_prefix'] = df['geolocation_zip_code_prefix'].astype(str).str.split('.').str[0].str.strip().str.zfill(5)

    # Trim trailing/leading spaces and format text upper for state and capitalize for city, and handling NULLs
    df['geolocation_city'] = df['geolocation_city'].fillna('Unknown').astype(str).str.strip().str.title()
    df['geolocation_state'] = df['geolocation_state'].fillna('Unknown').astype(str).str.strip().str.upper()

    # Remove duplicates based on Primary Key (customer_id)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['geolocation_zip_code_prefix'], keep='first')
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        logging.warning(f"Removed {duplicate_count} duplicate geolocation records.")

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.geolocation;"))

    logging.info("Loading data into silver.geolocation...")
    df.to_sql(
        name='geolocation',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows into silver.geolocation!\n")



def clean_order_items(engine):

    logging.info(">>> Beginning Processing for Table: silver.order_items")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.order_items"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Drop rows missing the Primary Keys
    df = df.dropna(subset=['order_id', 'order_item_id'])

    # Trim trailing/leading spaces from string IDs
    df['order_id'] = df['order_id'].astype(str).str.strip()
    df['product_id'] = df['product_id'].astype(str).str.strip()
    df['seller_id'] = df['seller_id'].astype(str).str.strip()

    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['freight_value'] = pd.to_numeric(df['freight_value'], errors='coerce')

    # Drop rows where price is missing or invalid
    df = df.dropna(subset=['price'])

    # Fill missing shipping values with 0.0
    df['freight_value'] = df['freight_value'].fillna(0.0)

    # Convert NVARCHAR date strings to actual Pandas Datetime objects
    df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'], errors='coerce')

    # Remove duplicates based on the Composite Primary Key (order_id + order_item_id)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['order_id', 'order_item_id'], keep='first')
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        logging.warning(f"Removed {duplicate_count} duplicate order_items records.")

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.order_items;"))

    logging.info("Loading data into silver.order_items...")
    df.to_sql(
        name='order_items',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows into silver.order_items!\n")



def clean_order_payments(engine):

    logging.info(">>> Beginning Processing for Table: silver.order_payments")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.order_payments"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Drop rows missing the Primary Key
    df = df.dropna(subset=['order_id', 'payment_sequential'])

    # Trim trailing/leading spaces from string IDs and ensure letters are lower in payment type, and handling NULLS
    df['order_id'] = df['order_id'].astype(str).str.strip()
    df['payment_type'] = df['payment_type'].fillna('unknown').astype(str).str.strip().str.lower()

    df['payment_value'] = pd.to_numeric(df['payment_value'], errors='coerce')
    # Drop rows where payment value is missing or invalid
    df = df.dropna(subset=['payment_value'])

    # Ensure sequential and installments are integers
    df['payment_sequential'] = pd.to_numeric(df['payment_sequential'], errors='coerce').fillna(1).astype(int)
    df['payment_installments'] = pd.to_numeric(df['payment_installments'], errors='coerce').fillna(1).astype(int)

    # Remove duplicates based on the Composite Primary Key (order_id + payment_sequential)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['order_id', 'payment_sequential'], keep='first')
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        logging.warning(f"Removed {duplicate_count} duplicate order_payments records.")

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.order_payments;"))

    logging.info("Loading data into silver.order_payments...")
    df.to_sql(
        name='order_payments',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows into silver.order_payments!\n")



def clean_order_reviews(engine):

    logging.info(">>> Beginning Processing for Table: silver.order_reviews")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.order_reviews"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Drop rows missing the Primary Keys
    df = df.dropna(subset=['order_id','review_id'])

    # Trim trailing/leading spaces
    df['order_id'] = df['order_id'].astype(str).str.strip()
    df['review_id'] = df['review_id'].astype(str).str.strip()
    df['review_comment_title'] = df['review_comment_title'].fillna('Unknown').astype(str).str.strip().str.title()
    df['review_comment_message'] = df['review_comment_message'].fillna('No Comment Provided').astype(str).str.strip().str.capitalize()

    # Convert NVARCHAR date strings to actual Pandas Datetime objects
    df['review_creation_date'] = pd.to_datetime(df['review_creation_date'], errors='coerce')
    df['review_answer_timestamp'] = pd.to_datetime(df['review_answer_timestamp'], errors='coerce')

    # Ensure review score is integer
    df['review_score'] = df['review_score'].astype(int)

    # Remove duplicates based on the Composite Primary Key (order_id + review_id)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['order_id', 'review_id'], keep='first')
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        logging.warning(f"Removed {duplicate_count} duplicate order_reviews records.")

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.order_reviews;"))

    logging.info("Loading data into silver.order_reviews...")
    df.to_sql(
        name='order_reviews',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows into silver.order_reviews!\n")



def clean_products(engine):

    logging.info(">>> Beginning Processing for Table: silver.products")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.products"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Drop rows missing the product_id
    df = df.dropna(subset=['product_id'])

    # Trim trailing/leading spaces, and handling NULLs
    df['product_id'] = df['product_id'].astype(str).str.strip()
    df['product_category_name'] = df['product_category_name'].fillna('Unknown').astype(str).str.strip().str.capitalize()

    # Ensure needed columns are integer
    numeric_cols = [
        'product_name_lenght',
        'product_description_lenght',
        'product_photos_qty',
        'product_weight_g',
        'product_length_cm',
        'product_height_cm',
        'product_width_cm'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    #Fill the NaNs with 0 typecasting
    df[numeric_cols] = df[numeric_cols].fillna(0)

    #Cast to clean integers using double-brackets [[ ]] syntax safely
    df[numeric_cols] = df[numeric_cols].astype(int)

    # Remove duplicates based on the Primary Key (product_id)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['product_id'], keep='first')
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        logging.warning(f"Removed {duplicate_count} duplicate products records.")

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.products;"))

    logging.info("Loading data into silver.products...")
    df.to_sql(
        name='products',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows into silver.products!\n")



def clean_sellers(engine):
    logging.info(">>> Beginning Processing for Table: silver.sellers")

    # 1. EXTRACT FROM BRONZE
    query = "SELECT * FROM bronze.sellers"
    df = pd.read_sql(query, con=engine)

    # 2. TRANSFORM / CLEAN DATA
    logging.info("Cleaning data...")

    # Drop rows missing the seller_id
    df = df.dropna(subset=['seller_id'])

    # Trim trailing/leading spaces
    df['seller_id'] = df['seller_id'].astype(str).str.strip()
    df['seller_city'] = df['seller_city'].fillna('Unknown').astype(str).str.strip().str.title()
    df['seller_state'] = df['seller_state'].fillna('UN').astype(str).str.strip().str.upper()

    # Clean zip code prefixes (cast to string, remove decimal artifact if read as float)
    if 'seller_zip_code_prefix' in df.columns:
        df['seller_zip_code_prefix'] = df['seller_zip_code_prefix'].fillna('00000').astype(str).str.split('.').str[0].str.strip().str.zfill(5)

    # Remove duplicates based on the Primary Key (seller_id)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['seller_id'], keep='first')
    duplicate_count = initial_count - len(df)
    if duplicate_count > 0:
        logging.warning(f"Removed {duplicate_count} duplicate sellers records.")

    # 3. LOAD TO SILVER
    logging.info("Truncating target silver table to refresh...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.sellers;"))

    logging.info("Loading data into silver.sellers...")
    df.to_sql(
        name='sellers',
        con=engine,
        schema='silver',
        if_exists='append',
        index=False
    )
    logging.info(f"Successfully loaded {len(df)} clean rows into silver.sellers!\n")



def run_silver_pipeline():

    engine = get_db_engine()

    functions = [
        clean_orders,
        clean_catogary_name_translateion,
        clean_customers,
        clean_geolocation,
        clean_order_items,
        clean_order_payments,
        clean_order_reviews,
        clean_products,
        clean_sellers
    ]

    for func in functions:
        try:
            func(engine)
        except Exception as e:
            logging.warning(f"Error running {func.__name__}:{e}", exc_info=True)
            # NOTE: Adding exc_info=True will print out the exact line number and problem if the table crashes
            continue

    logging.info("All Silver Layer transformations executed successfully!")

if __name__ == "__main__":
    run_silver_pipeline()
