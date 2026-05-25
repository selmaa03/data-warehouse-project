-- BASE TABLES 

IF OBJECT_ID ('bronze.customers', 'U') IS NOT NULL DROP TABLE bronze.customers;
CREATE TABLE bronze.customers (
    customer_id NVARCHAR(50) PRIMARY KEY,
    customer_unique_id NVARCHAR(50) NOT NULL,
    customer_zip_code_prefix NVARCHAR(15),
    customer_city NVARCHAR(100),
    customer_state NVARCHAR(10)
);

IF OBJECT_ID ('bronze.catogary_name_translation', 'U') IS NOT NULL DROP TABLE bronze.catogary_name_translation;
CREATE TABLE bronze.catogary_name_translation (
    product_category_name NVARCHAR(100) PRIMARY KEY,
    product_category_name_english NVARCHAR(100)
);

IF OBJECT_ID ('bronze.sellers', 'U') IS NOT NULL DROP TABLE bronze.sellers;
CREATE TABLE bronze.sellers (
    seller_id NVARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix NVARCHAR(15),
    seller_city NVARCHAR(100),
    seller_state NVARCHAR(10)
);

IF OBJECT_ID ('bronze.geolocation', 'U') IS NOT NULL DROP TABLE bronze.geolocation;
CREATE TABLE bronze.geolocation (
    geolocation_zip_code_prefix NVARCHAR(15),
    geolocation_lat DECIMAL(10, 8),
    geolocation_lng DECIMAL(11, 8),
    geolocation_city NVARCHAR(100),
    geolocation_state NVARCHAR(10)
);


-- DEPENDENT TABLES

IF OBJECT_ID ('bronze.orders', 'U') IS NOT NULL DROP TABLE bronze.orders;
CREATE TABLE bronze.orders (
    order_id NVARCHAR(50) PRIMARY KEY,
    customer_id NVARCHAR(50),
    order_status NVARCHAR(50),
    order_purchase_timestamp NVARCHAR(50),
    order_approved_at NVARCHAR(50),
    order_delivered_carrier_date NVARCHAR(50),
    order_delivered_customer_date NVARCHAR(50),
    order_estimated_delivery_date NVARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES bronze.customers(customer_id)
);

IF OBJECT_ID ('bronze.products', 'U') IS NOT NULL DROP TABLE bronze.products;
CREATE TABLE bronze.products (
    product_id NVARCHAR(50) PRIMARY KEY,
    product_category_name NVARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT,
    FOREIGN KEY (product_category_name) REFERENCES bronze.catogary_name_translation(product_category_name)
);


-- SUB-DEPENDENT TABLES

IF OBJECT_ID ('bronze.order_payments', 'U') IS NOT NULL DROP TABLE bronze.order_payments;
CREATE TABLE bronze.order_payments (
    order_id NVARCHAR(50),
    payment_sequential INT,
    payment_type NVARCHAR(50),
    payment_installments INT,
    payment_value DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES bronze.orders(order_id)
);

IF OBJECT_ID ('bronze.order_reviews', 'U') IS NOT NULL DROP TABLE bronze.order_reviews;
CREATE TABLE bronze.order_reviews (
    review_id NVARCHAR(50) PRIMARY KEY,
    order_id NVARCHAR(50),
    review_score INT,
    review_comment_title NVARCHAR(150),
    review_comment_message NVARCHAR(MAX),
    review_creation_date NVARCHAR(50),
    review_answer_timestamp NVARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES bronze.orders(order_id)
);

IF OBJECT_ID ('bronze.order_items', 'U') IS NOT NULL DROP TABLE bronze.order_items;
CREATE TABLE bronze.order_items (
    order_id NVARCHAR(50),
    order_item_id INT,
    product_id NVARCHAR(50),
    seller_id NVARCHAR(50),
    shipping_limit_date NVARCHAR(50),
    price DECIMAL(10,2),
    freight_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES bronze.orders(order_id),
    FOREIGN KEY (product_id) REFERENCES bronze.products(product_id),
    FOREIGN KEY (seller_id) REFERENCES bronze.sellers(seller_id)
);
