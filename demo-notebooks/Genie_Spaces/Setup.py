# Databricks notebook source
# DBTITLE 1,Setup - Schema and imports
# Demo: Genie Spaces — Setup
# Creates data assets for all Genie Spaces demos:
#   1. customers         — 100-row customer dimension (segment, region, city)
#   2. sales_orders      — 1000-row order fact table (product, channel, revenue, cost)
#   3. vw_monthly_sales  — pre-aggregated monthly summary view
#   4. sales_targets     — 20-row regional quarterly targets (Demo 2)
#   5. fn_profit_margin  — Unity Catalog SQL function (Demo 2)

import re
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DoubleType
)
from datetime import date, timedelta
import random

# --- Schema setup ---
username = spark.sql("SELECT current_user()").collect()[0][0]
clean_username = re.sub(r'[^a-zA-Z0-9]', '_', username.split('@')[0])
catalog = "workspace"
schema  = f"demo_genie_{clean_username}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")
spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

print(f"Catalog : {catalog}")
print(f"Schema  : {schema}")

# COMMAND ----------

# DBTITLE 1,Create customers table
# =============================================================
# TABLE 1: CUSTOMERS (100 rows)
# =============================================================
# A dimension table describing who bought from us.
# Useful for questions like: "How many customers per segment?"
# or "Which cities have the most customers?"

random.seed(99)

segments = ['Consumer', 'Corporate', 'Home Office']
regions  = ['Northeast', 'Southeast', 'Midwest', 'West', 'Northwest']
cities_by_region = {
    'Northeast': ['New York', 'Boston', 'Philadelphia'],
    'Southeast': ['Atlanta', 'Miami', 'Charlotte'],
    'Midwest':   ['Chicago', 'Detroit', 'Columbus'],
    'West':      ['Los Angeles', 'San Francisco', 'Denver'],
    'Northwest': ['Seattle', 'Portland', 'Boise'],
}
first_names = [
    'Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Cameron',
    'Sam', 'Drew', 'Avery', 'Blake', 'Quinn', 'Logan', 'Hayden', 'Skyler',
    'Reese', 'Dylan', 'Peyton', 'Parker', 'Jamie'
]
last_names = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
    'Davis', 'Wilson', 'Anderson', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Lee', 'Thompson', 'White', 'Harris', 'Clark', 'Lewis'
]

customer_rows = []
for i in range(1, 101):
    seg  = random.choice(segments)
    reg  = random.choice(regions)
    city = random.choice(cities_by_region[reg])
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    joined = date(2021, 1, 1) + timedelta(days=random.randint(0, 900))
    customer_rows.append((i, name, seg, reg, city, joined.isoformat()))

cust_schema = StructType([
    StructField("customer_id",   IntegerType()),
    StructField("customer_name", StringType()),
    StructField("segment",       StringType()),
    StructField("region",        StringType()),
    StructField("city",          StringType()),
    StructField("join_date",     StringType()),
])

spark.sql("DROP TABLE IF EXISTS customers")
df_cust = spark.createDataFrame(customer_rows, schema=cust_schema)
df_cust = df_cust.withColumn("join_date", F.to_date("join_date"))
df_cust.write.saveAsTable("customers")

print(f"customers: {df_cust.count()} rows created")

# COMMAND ----------

# DBTITLE 1,Create sales_orders table
# =============================================================
# TABLE 2: SALES_ORDERS (1000 rows)
# =============================================================
# The main fact table — one row per order line.
# Good for questions about revenue, profit, channels, products, and regions.
# customer_id links to the customers table.

random.seed(42)

categories = {
    'Electronics':   ['Laptop Pro', 'Tablet Air', 'Wireless Earbuds', 'Smart Watch'],
    'Clothing':      ['Denim Jacket', 'Running Shoes', 'Winter Coat', 'Casual T-Shirt'],
    'Home & Garden': ['Standing Desk', 'LED Lamp', 'Garden Hose', 'Air Purifier'],
    'Sports':        ['Yoga Mat', 'Dumbbell Set', 'Tennis Racket', 'Cycling Helmet'],
}
channels = ['Online', 'In-Store', 'Mobile', 'Wholesale']

order_rows = []
for i in range(1, 1001):
    cat     = random.choice(list(categories.keys()))
    product = random.choice(categories[cat])
    cust_id = random.randint(1, 100)
    region  = customer_rows[cust_id - 1][3]   # inherit region from customer
    channel = random.choice(channels)
    odate   = date(2024, 1, 1) + timedelta(days=random.randint(0, 364))
    qty     = random.randint(1, 5)
    uprice  = round(random.uniform(15, 600), 2)
    disc    = round(random.choice([0.0, 0.0, 0.05, 0.10, 0.15, 0.20]), 2)
    net_rev = round(qty * uprice * (1 - disc), 2)
    cost    = round(net_rev * random.uniform(0.40, 0.65), 2)
    order_rows.append((
        i, odate.isoformat(), cust_id, region,
        cat, product, channel,
        qty, uprice, disc, net_rev, cost
    ))

ord_schema = StructType([
    StructField("order_id",         IntegerType()),
    StructField("order_date",       StringType()),
    StructField("customer_id",      IntegerType()),
    StructField("region",           StringType()),
    StructField("product_category", StringType()),
    StructField("product_name",     StringType()),
    StructField("channel",          StringType()),
    StructField("quantity",         IntegerType()),
    StructField("unit_price",       DoubleType()),
    StructField("discount_pct",     DoubleType()),
    StructField("net_revenue",      DoubleType()),
    StructField("cost",             DoubleType()),
])

spark.sql("DROP TABLE IF EXISTS sales_orders")
df_orders = spark.createDataFrame(order_rows, schema=ord_schema)
df_orders = df_orders.withColumn("order_date", F.to_date("order_date"))
df_orders.write.saveAsTable("sales_orders")

print(f"sales_orders: {df_orders.count()} rows created")

# COMMAND ----------

# DBTITLE 1,Create sales_targets table
# =============================================================
# TABLE 3: SALES_TARGETS (20 rows)
# =============================================================
# Regional quarterly revenue and order-count targets for 2024.
# Demonstrates join relationships in Genie Space configuration (Demo 2).
# Joins to sales_orders on: region  AND  derived quarter from order_date.
#
# Targets are set to create a realistic mix of hits and misses
# so Genie's performance-vs-target queries produce interesting results.

targets_data = [
    # (region,      year,  quarter, target_revenue, target_orders)
    ('Northeast', 2024, 'Q1', 16000.0, 45),
    ('Northeast', 2024, 'Q2', 17000.0, 48),
    ('Northeast', 2024, 'Q3', 18000.0, 50),
    ('Northeast', 2024, 'Q4', 19000.0, 52),
    ('Southeast', 2024, 'Q1', 12000.0, 38),
    ('Southeast', 2024, 'Q2', 13000.0, 40),
    ('Southeast', 2024, 'Q3', 14000.0, 42),
    ('Southeast', 2024, 'Q4', 14500.0, 44),
    ('Midwest',   2024, 'Q1', 10000.0, 32),
    ('Midwest',   2024, 'Q2', 11000.0, 35),
    ('Midwest',   2024, 'Q3', 12000.0, 38),
    ('Midwest',   2024, 'Q4', 12500.0, 40),
    ('West',      2024, 'Q1', 15000.0, 42),
    ('West',      2024, 'Q2', 16000.0, 45),
    ('West',      2024, 'Q3', 17000.0, 48),
    ('West',      2024, 'Q4', 18000.0, 50),
    ('Northwest', 2024, 'Q1',  8000.0, 28),
    ('Northwest', 2024, 'Q2',  9000.0, 30),
    ('Northwest', 2024, 'Q3',  9500.0, 32),
    ('Northwest', 2024, 'Q4', 10000.0, 34),
]

tgt_schema = StructType([
    StructField("region",         StringType()),
    StructField("year",           IntegerType()),
    StructField("quarter",        StringType()),
    StructField("target_revenue", DoubleType()),
    StructField("target_orders",  IntegerType()),
])

spark.sql("DROP TABLE IF EXISTS sales_targets")
df_targets = spark.createDataFrame(targets_data, schema=tgt_schema)
df_targets.write.saveAsTable("sales_targets")

print(f"sales_targets: {df_targets.count()} rows created")

# COMMAND ----------

# DBTITLE 1,Create fn_profit_margin SQL function
# MAGIC %sql
# MAGIC -- =============================================================
# MAGIC -- SQL FUNCTION: fn_profit_margin
# MAGIC -- =============================================================
# MAGIC -- A Unity Catalog scalar function that calculates gross profit margin
# MAGIC -- as a percentage. Registered as a trusted asset in the Genie Space
# MAGIC -- (Demo 2) so Genie uses verified logic when users ask about margin.
# MAGIC --
# MAGIC -- Sample questions this function is designed to answer:
# MAGIC --   "What is the profit margin for each product category?"
# MAGIC --   "Show me our margin across regions."
# MAGIC --   "Which channel has the best gross margin?"
# MAGIC
# MAGIC CREATE OR REPLACE FUNCTION fn_profit_margin(revenue DOUBLE, cost DOUBLE)
# MAGIC RETURNS DOUBLE
# MAGIC COMMENT 'Calculates gross profit margin as a percentage: (revenue - cost) / revenue * 100. Returns NULL when revenue is zero or NULL. Round result as needed before display.'
# MAGIC RETURN
# MAGIC   CASE
# MAGIC     WHEN revenue IS NULL OR revenue = 0 THEN NULL
# MAGIC     ELSE ROUND((revenue - cost) / revenue * 100, 2)
# MAGIC   END;

# COMMAND ----------

# DBTITLE 1,Create vw_monthly_sales view
# MAGIC %sql
# MAGIC -- =============================================================
# MAGIC -- VIEW: VW_MONTHLY_SALES
# MAGIC -- =============================================================
# MAGIC -- Pre-aggregated monthly summary, grouped by region and product category.
# MAGIC -- Useful for time-based questions like:
# MAGIC --   "What was total revenue per month?" or "Which region grew fastest?"
# MAGIC
# MAGIC CREATE OR REPLACE VIEW vw_monthly_sales AS
# MAGIC SELECT
# MAGIC   DATE_TRUNC('MONTH', order_date)         AS order_month,
# MAGIC   region,
# MAGIC   product_category,
# MAGIC   COUNT(order_id)                         AS order_count,
# MAGIC   ROUND(SUM(net_revenue), 2)              AS total_revenue,
# MAGIC   ROUND(SUM(cost), 2)                     AS total_cost,
# MAGIC   ROUND(SUM(net_revenue - cost), 2)       AS total_profit,
# MAGIC   ROUND(AVG(net_revenue), 2)              AS avg_order_value
# MAGIC FROM sales_orders
# MAGIC GROUP BY ALL;

# COMMAND ----------

# DBTITLE 1,Verify setup complete
# --- Verification: confirm all assets exist and print schema reference ---
verify_sql = f"""
  SELECT table_name, table_type
  FROM   `{catalog}`.information_schema.tables
  WHERE  table_schema = '{schema}'
  ORDER BY table_name
"""
results = spark.sql(verify_sql).collect()

print("")
print("SETUP COMPLETE")
print("")
print(f"Catalog : {catalog}")
print(f"Schema  : {schema}")
print("")
print("Assets created:")
for row in results:
    label = "TABLE" if row.table_type == "BASE TABLE" else "VIEW "
    print(f"  {label}  →  {row.table_name}")
print("")
print(f"Use this fully-qualified path in the Genie Space UI:")
print(f"  {catalog}.{schema}.<table_name>")

# --- Confirm SQL function exists ---
try:
    fn_check = spark.sql(f"SELECT `{catalog}`.`{schema}`.fn_profit_margin(1000.0, 400.0) AS margin").collect()
    print(f"")
    print(f"SQL function fn_profit_margin: OK (test result: {fn_check[0].margin}%)")
except Exception as e:
    print(f"\nWarning: fn_profit_margin not found or failed: {e}")
