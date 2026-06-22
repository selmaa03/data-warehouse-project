# Data Warehouse Project
Building an end-to-end data warehouse using SQL Server, AWS S3, ETL pipelines, dimensional modeling, and analytics.

## Project Overview
This project implements a modern data warehouse architecture using SQL Server and AWS S3. The solution ingests CSV datasets, stores them in a multi-layered data lake, applies data cleaning and transformation processes, and loads them into an analytical data model to support reporting and decision-making.

## Data Architecture
![Data Medallion Architecture](docs/Data%20Medallion%20Architecture.jpg)
The project follows the Medallion Architecture Bronze, Silver, and Gold layers:
**1. Bronze Layer:** Ingest raw CSV files from the Olist dataset into AWS S3, maintain the original format as a source of truth.
**2. Silver Layer:** Process raw data, handle missing values, standardize data types, and establish clean relational schemas and store processed data in both AWS S3 and SQL Server.
**3. Gold Layer:** Transform the cleaned data into star schema with dimensional modeling (Fact and Dimension tables) for reporting and analytics.

## Project Structure
```
datasource/    -> Source CSV datasets
docs/          -> Documentation and architecture diagrams
scripts/py/    -> Python ETL scripts
scripts/sql/   -> SQL DDL scripts

data-warehouse-project/
│
├── datasource/  # Source of CSV datasets
├── docs/        # Documentation and architecture diagrams
├── scripts
│ ├── py/
│ │   ├── config.py                  # Environment and configuration setup
│ │   ├── 02_extract_bronze.py       # Ingests raw CSVs to S3 Bronze
│ │   ├── 03_explore_bronze.py       # Data exploration and profiling (OPTIONAL)
│ │   ├── 04_load_bronze.py          # Loads raw data into SQL Server Bronze
│ │   ├── 05_transform_silver.py     # Cleanses and transforms data and load to S3 as Parquet
│ │   ├── 06_load_silver.py          # Loads clean data into SQL Server Silver
│ │   └── 07_transform_gold.py       # Builds analytical Fact/Dim tables and loads into SQL Server Gold
│ └── sql/
│     ├── 01_setup_database.sql      # Database initialization
│     ├── 02_DDL_bronze.sql          # Schema definition for Bronze layer
│     ├── 03_DDL_silver.sql          # Schema definition for Silver layer
│     └── 04_DDL_gold.sql            # Schema definition for Gold star schema
|
├── requirements.txt
└── README.md
```

## Important Notes
Please note the following:
- Inside the py folder, 01_config.py demonstrates the first step of the pipeline. To import config in other files, you must use the name only config.py. For other files you can keep the names with numbers for order clarity.
- In the product_category_name_translation table, category is spelled as catogary. For sql and py files, you should consider the misspelling and correct them.
- Create a .env file containing your own aws access keys, user, and db connection details and other environment variables.

## S3 Data Lake Structure
```
dwh-olist-bucket/
│
├── raw-data-folder/
│ ├── olist_customers_dataset.csv
| ├── olist_geolocation_dataset.csv
| ├── olist_order_items_dataset.csv
| ├── olist_order_payments_dataset.csv
| ├── olist_order_reviews_dataset.csv
| ├── olist_orders_dataset.csv
| ├── olist_products_dataset.csv
| ├── olist_sellers_dataset.csv
| └── product_category_name_translation.csv
│
├── processed-data-folder/
│ ├── catogary_name_translation/
| | ├── catogary_name_translation_clean.parquet
│ ├── customers/
│ ├── geolocation/
│ ├── order_items/
│ ├── order_payments/
│ ├── order_reviews/
│ ├── orders/
│ ├── products/
│ └── sellers/
│
├── gold-data-folder/
│ ├── dim_customers.parquet
│ ├── dim_products.parquet
│ ├── dim_sellers.parquet
│ └── fact_sales.parquet
└──
```
