# Data Dictionary for Gold Layer

## Overview
The Gold Layer provides business-ready data marts, structured to support analytical and reporting use cases. It consists of **dimension** and **fact tables** for specific business metrics.

### Design Principles
* No ETL/load process exists in the Gold layer.
* Gold objects are implemented as SQL Views.
* Views do not store data physically; they provide a virtual representation of transformed Silver layer data.
* The Gold layer follows a star-schema approach with fact and dimension views.

## Fact Table

### `Gold.fact_sales`
* **Purpose:** Contains order item level transactions enriched with customer and payment information.
*  **Grain:** One row per order item.
* **Source Tables:**
	* *Silver.order_items*
	* *Silver.orders*
	* *Silver.order_payments*
* **Columns:**


| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `order_id` | `VARCHAR(50)` | Unique identifier for each order |
| `order_item_id` | `INT` | Item sequence within an order |
| `customer_id` | `VARCHAR(50)` | Unique identifier for each customer |
| `product_id` | `VARCHAR(50)` | Unique identifier for each product |
| `seller_id` | `VARCHAR(50)` | Unique identifier for each seller |
| `order_status` | `NVARCHAR(50)` | Current order status (e.g., 'delivered', 'shipped', 'unavailable') |
| `order_purchase_timestamp` | `DATETIME2` | Order purchase timestamp formatted as YYYY-MM-DD HH:MI:SS.nnnnnnn (e.g., '2018-08-06 16:20:23.0000000') |
| `order_delivered_customer_date` | `DATETIME2` | Delivery date timestamp when the product reached the customer formatted as YYYY-MM-DD HH:MI:SS.nnnnnnn (e.g., '2018-08-22 14:40:48.0000000') |
| `price` | `DECIMAL(10,2)` | Product sale price |
| `freight_value` | `DECIMAL(10,2)` | Shipping cost |
|`total_payment_value` | `DECIMAL(10,2)` | Total payment amount associated with the order. This value is repeated for all items belonging to the same order (defaults to '0' if missing).|


## Dimension Tables

### `Gold.dim_customers`
* **Purpose:** Contains customer identification attributes and location.
* **Source Table:** *Silver.customers*
* **Columns:**

| Column Name | Data Type | Description |
| :--- | :--- | :--- | 
| customer_id | VARCHAR(50) | Unique identifier for each customer |
| customer_unique_id | VARCHAR(50) | Unique identifier tracking the same physical customer across multiple accounts |
| customer_zip_code_prefix | VARCHAR(15) | Customer's ZIP code prefix |
| customer_city | NVARCHAR(100) | City name of the customer's billing/delivery address |
| customer_state | CHAR(2)| State code of the customer's address |

### `Gold.dim_products`
* **Purpose:** Contains product identifier and physical attributes enriched with English translations of category names.
* **Source Tables:**
	* *Silver.products*
	* *Silver.catogary_name_translation*
* **Columns:**
	
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| product_id | VARCHAR(50)| Unique identifier for each product |
| product_category_name | NVARCHAR(100) | English name of product category (defaults to Portuguese if missing) |
| product_weight_g | INT | Product weight in grams |
| product_length_cm| INT | Product length in centimeters |
| product_height_cm| INT | Product height in centimeters |
| product_width_cm | INT | Product width in centimeters |

### `Gold.dim_sellers`
* **Purpose:** Contains seller identification attributes and location.
* **Source Table:** *Silver.sellers*
* **Columns:**

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| seller_id | VARCHAR(50) | Unique identifier for each seller |
| seller_zip_code_prefix | VARCHAR(15) | Seller's ZIP code prefix |
| seller_city | NVARCHAR(100) | City name where the seller is based |
| seller_state | CHAR(2) | State code where the seller is located |
