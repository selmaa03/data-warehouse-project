/*
What has changed when defining silver layer schema?
~ Primary keys and composite keys are added to enforce row uniqueness and prevent duplicate data injection.
~ Optimized data types by converting raw NVARCHAR strings to structured formats.
~ Audit column added (dwh_create_date DATETIME2 DEFAULT SYSDATETIME() to track exactly when the rows loaded into the warehouse.
*/

-- BASE TABLES 

IF OBJECT_ID ('silver.customers', 'U') IS NOT NULL DROP TABLE silver.customers;
CREATE TABLE silver.customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix VARCHAR(15),
    customer_city NVARCHAR(100),
    customer_state CHAR(2),
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);

IF OBJECT_ID ('silver.catogary_name_translation', 'U') IS NOT NULL DROP TABLE silver.catogary_name_translation;
CREATE TABLE silver.catogary_name_translation (
    product_category_name NVARCHAR(100) PRIMARY KEY,
    product_category_name_english NVARCHAR(100) NOT NULL,
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);

IF OBJECT_ID ('silver.sellers', 'U') IS NOT NULL DROP TABLE silver.sellers;
CREATE TABLE silver.sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(15),
    seller_city NVARCHAR(100),
    seller_state CHAR(2),
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);

IF OBJECT_ID ('silver.geolocation', 'U') IS NOT NULL DROP TABLE silver.geolocation;
CREATE TABLE silver.geolocation (
    geolocation_zip_code_prefix VARCHAR(15),
    geolocation_lat DECIMAL(10, 8),
    geolocation_lng DECIMAL(11, 8),
    geolocation_city NVARCHAR(100),
    geolocation_state CHAR(2),
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);


-- DEPENDENT TABLES

IF OBJECT_ID ('silver.orders', 'U') IS NOT NULL DROP TABLE silver.orders;
CREATE TABLE silver.orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status NVARCHAR(50),
    order_purchase_timestamp DATETIME2,
    order_approved_at DATETIME2,
    order_delivered_carrier_date DATETIME2,
    order_delivered_customer_date DATETIME2,
    order_estimated_delivery_date DATETIME2,
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);

IF OBJECT_ID ('silver.products', 'U') IS NOT NULL DROP TABLE silver.products;
CREATE TABLE silver.products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name NVARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT,
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);


-- SUB-DEPENDENT TABLES

IF OBJECT_ID ('silver.order_items', 'U') IS NOT NULL DROP TABLE silver.order_items;
CREATE TABLE silver.order_items (
    order_id VARCHAR(50),
    order_item_id INT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date DATETIME2,
    price DECIMAL(10,2),
    freight_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, order_item_id),
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);

IF OBJECT_ID ('silver.order_payments', 'U') IS NOT NULL DROP TABLE silver.order_payments;
CREATE TABLE silver.order_payments (
    order_id VARCHAR(50),
    payment_sequential INT,
    payment_type NVARCHAR(50),
    payment_installments INT,
    payment_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, payment_sequential),
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);

IF OBJECT_ID ('silver.order_reviews', 'U') IS NOT NULL DROP TABLE silver.order_reviews;
CREATE TABLE silver.order_reviews (
    review_id VARCHAR(50),
    order_id VARCHAR(50),
    review_score INT,
    review_comment_title NVARCHAR(150),
    review_comment_message NVARCHAR(MAX),
    review_creation_date DATETIME2,
    review_answer_timestamp DATETIME2,
    PRIMARY KEY (review_id, order_id),
    dwh_create_date DATETIME2 DEFAULT SYSDATETIME()
);
