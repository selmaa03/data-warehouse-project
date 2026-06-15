/*
The Golden layer does not have load process, it is using data of Silver layer which is already processed.

View is a virtual table based on the result set of a query, without storing data in the database.
So you can’t write something to the database, you can just view/read.
Views can be used as data marts too.
*/

CREATE VIEW Gold.fact_sales AS
WITH aggregated_payments AS (
    SELECT 
        order_id,
        SUM(payment_value) AS total_payment_value
    FROM Silver.order_payments
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
    ISNULL(ap.total_payment_value, 0) AS total_payment_value
FROM Silver.order_items as oi
INNER JOIN Silver.orders as o
    ON oi.order_id = o.order_id
LEFT JOIN aggregated_payments as ap
    ON oi.order_id = ap.order_id;
GO


CREATE VIEW Gold.dim_customers AS
SELECT 
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM Silver.customers;
GO

CREATE VIEW Gold.dim_products AS
SELECT 
    p.product_id,
    ISNULL(t.product_category_name_english, p.product_category_name) AS product_category_name,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM Silver.products p
LEFT JOIN Silver.catogary_name_translation t
    ON p.product_category_name = t.product_category_name;
GO

CREATE VIEW Gold.dim_sellers AS
SELECT 
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM Silver.sellers;
GO
