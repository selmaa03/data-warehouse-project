'''
STEP 3:
Before starting to silver layer, it is important to explore and understand the data.

Why do this first?
Data Type Validation: Confirm whether columns are correctly typed (integer, float, string, date).
Spot Missing Data: You'll see if there are empty (NULL) cells you need to handle.
Data Consistency Checks: Checks for duplicated rows or IDs
Basic Statistics: Provides descriptive stats for numeric columns (mean, median, std, min, max).
'''

import pandas as pd
import os

script_dir = os.path.dirname(__file__)

base_dir = os.path.dirname(os.path.dirname(script_dir))

'''
uncomment the file that you want to exlpore.
'''
csv_path = os.path.join(base_dir, "datasets", "raw", "olist_customers_dataset.csv")
#csv_path = os.path.join(base_dir, "datasets", "raw", "olist_geolocation_dataset.csv")
#csv_path = os.path.join(base_dir, "datasets", "raw", "olist_sellers_dataset.csv")
#csv_path = os.path.join(base_dir, "datasets", "raw", "product_category_name_translation.csv")
#csv_path = os.path.join(base_dir, "datasets", "raw", "olist_orders_dataset.csv")
#csv_path = os.path.join(base_dir, "datasets", "raw", "olist_products_dataset.csv")
#csv_path = os.path.join(base_dir, "datasets", "raw", "olist_order_items_dataset.csv")
#csv_path = os.path.join(base_dir, "datasets", "raw", "olist_order_payments_dataset.csv")
#csv_path = os.path.join(base_dir, "datasets", "raw", "olist_order_reviews_dataset.csv")


df = pd.read_csv(csv_path)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print('\nCOLUMNS: ')
print(df.dtypes)

print('\nVALUES: ')
print(df.head(10))

print('\nMissing (NULL VALUE) Counts: ')
print(df.isnull().sum())

print('\nDuplicated IDs: ')
print(df.duplicated().sum())
