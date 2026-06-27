# Databricks notebook source
# DBTITLE 1,Setup — Schema and imports
# Dashboard Challenge — Setup
# Creates tables, views, and a metric view used across all challenge tasks.

import re
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType
from datetime import date, timedelta
import random

# --- Schema setup ---
username      = spark.sql("SELECT current_user()").collect()[0][0]
clean_username = re.sub(r'[^a-zA-Z0-9]', '_', username.split('@')[0])
catalog = "workspace"
schema  = f"challenge_dashboards_{clean_username}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")
spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA  `{schema}`")

# COMMAND ----------

# DBTITLE 1,Create retail_orders table
# --- retail_orders: 2 000 rows ---
random.seed(55)
spark.sql("DROP TABLE IF EXISTS retail_orders")

regions     = ['Northeast', 'Southeast', 'Midwest', 'West', 'Northwest']
departments = ['Electronics', 'Apparel', 'Home & Garden', 'Sports & Outdoors', 'Grocery']
channels    = ['Web', 'Mobile', 'In-Store', 'Marketplace']
segments    = ['Premium', 'Standard', 'Budget']
products    = [
    'Noise-Cancelling Headphones', 'Mechanical Keyboard', 'Webcam HD', '4K Monitor',
    'Fleece Hoodie', 'Waterproof Jacket', 'Cargo Pants', 'Athletic Socks',
    'Ceramic Planter', 'Blackout Curtains', 'Air Purifier', 'Smart Thermostat',
    'Resistance Bands', 'Hiking Boots', 'Foam Roller', 'Jump Rope',
    'Organic Coffee', 'Protein Granola', 'Trail Mix', 'Sparkling Water',
]

schema_def = StructType([
    StructField("order_id",      IntegerType(), False),
    StructField("order_date",    DateType(),    False),
    StructField("region",        StringType(),  False),
    StructField("product_name",  StringType(),  False),
    StructField("department",    StringType(),  False),
    StructField("channel",       StringType(),  False),
    StructField("segment",       StringType(),  False),
    StructField("quantity",      IntegerType(), False),
    StructField("gross_revenue", DoubleType(),  False),
    StructField("cogs",          DoubleType(),  False),
])

rows = []
for i in range(1, 2001):
    order_date = date(2024, 1, 1) + timedelta(days=random.randint(0, 364))
    unit_price = round(random.uniform(10, 400), 2)
    qty        = random.randint(1, 5)
    discount   = random.choice([0.0, 0.0, 0.0, 0.05, 0.10, 0.15])
    gross_rev  = round(qty * unit_price * (1 - discount), 2)
    cogs_val   = round(gross_rev * random.uniform(0.35, 0.65), 2)
    rows.append((
        i, order_date, random.choice(regions),  random.choice(products),
        random.choice(departments), random.choice(channels),
        random.choice(segments), qty, gross_rev, cogs_val
    ))

df = spark.createDataFrame(rows, schema=schema_def)
df.write.saveAsTable("retail_orders")

# COMMAND ----------

# DBTITLE 1,Create retail_customers table
# --- retail_customers: 150 rows ---
random.seed(88)
spark.sql("DROP TABLE IF EXISTS retail_customers")

first_names = ['Alice', 'Bob', 'Carlos', 'Diana', 'Ethan',
               'Fiona', 'George', 'Hannah', 'Ivan', 'Julia']
last_names  = ['Anderson', 'Baker', 'Chen', 'Davis', 'Evans',
               'Foster', 'Green', 'Hill', 'Ingram', 'Jones']

cust_schema = StructType([
    StructField("customer_id",      IntegerType(), False),
    StructField("full_name",        StringType(),  False),
    StructField("tier",             StringType(),  False),
    StructField("home_region",      StringType(),  False),
    StructField("first_order_date", DateType(),    False),
    StructField("total_orders",     IntegerType(), False),
    StructField("total_spent",      DoubleType(),  False),
])

cust_rows = []
for i in range(1, 151):
    cust_rows.append((
        i,
        f"{random.choice(first_names)} {random.choice(last_names)}",
        random.choice(['Gold', 'Silver', 'Bronze']),
        random.choice(regions),
        date(2021, 1, 1) + timedelta(days=random.randint(0, 1460)),
        random.randint(1, 50),
        round(random.uniform(50, 20000), 2),
    ))

df_cust = spark.createDataFrame(cust_rows, schema=cust_schema)
df_cust.write.saveAsTable("retail_customers")

# COMMAND ----------

# DBTITLE 1,Create SQL views
# MAGIC %sql
# MAGIC -- View 1: monthly revenue trend (time-series ready)
# MAGIC CREATE OR REPLACE VIEW vw_monthly_trend AS
# MAGIC SELECT
# MAGIC   DATE_TRUNC('MONTH', order_date)           AS order_month,
# MAGIC   channel,
# MAGIC   department,
# MAGIC   COUNT(order_id)                           AS order_count,
# MAGIC   ROUND(SUM(gross_revenue), 2)              AS total_revenue,
# MAGIC   ROUND(SUM(gross_revenue - cogs), 2)       AS gross_profit,
# MAGIC   ROUND(AVG(gross_revenue), 2)              AS avg_order_value
# MAGIC FROM retail_orders
# MAGIC GROUP BY ALL;
# MAGIC
# MAGIC -- View 2: region performance scorecard
# MAGIC CREATE OR REPLACE VIEW vw_region_scorecard AS
# MAGIC SELECT
# MAGIC   region,
# MAGIC   COUNT(order_id)                                                       AS total_orders,
# MAGIC   ROUND(SUM(gross_revenue), 2)                                          AS total_revenue,
# MAGIC   ROUND(AVG(gross_revenue), 2)                                          AS avg_order_value,
# MAGIC   ROUND(SUM(gross_revenue - cogs) / SUM(gross_revenue) * 100, 1)        AS margin_pct
# MAGIC FROM retail_orders
# MAGIC GROUP BY region;
# MAGIC
# MAGIC -- View 3: department revenue breakdown by channel
# MAGIC CREATE OR REPLACE VIEW vw_dept_summary AS
# MAGIC SELECT
# MAGIC   department,
# MAGIC   channel,
# MAGIC   COUNT(order_id)              AS order_count,
# MAGIC   ROUND(SUM(gross_revenue), 2) AS total_revenue,
# MAGIC   ROUND(SUM(gross_revenue - cogs), 2) AS gross_profit
# MAGIC FROM retail_orders
# MAGIC GROUP BY department, channel;
# MAGIC
# MAGIC SHOW TABLES;

# COMMAND ----------

# DBTITLE 1,Create metric view
# --- Metric view: mv_retail_metrics ---
spark.sql(f"""
CREATE OR REPLACE VIEW mv_retail_metrics
WITH METRICS
LANGUAGE YAML
AS $$
  version: 1.1
  source: {catalog}.{schema}.retail_orders
  dimensions:
    - name: Region
      expr: region
    - name: Channel
      expr: channel
    - name: Department
      expr: department
    - name: Segment
      expr: segment
  measures:
    - name: Total Revenue
      expr: SUM(gross_revenue)
    - name: Gross Profit
      expr: SUM(gross_revenue - cogs)
    - name: Order Count
      expr: COUNT(order_id)
    - name: Avg Order Value
      expr: AVG(gross_revenue)
    - name: Profit Margin
      expr: SUM(gross_revenue - cogs) / SUM(gross_revenue) * 100
$$""")

# COMMAND ----------

# DBTITLE 1,Print summary
# --- Summary ---
print("CHALLENGE SETUP COMPLETE")
print("")
print(f"Catalog : {catalog}")
print(f"Schema  : {schema}")
print()
print("Tables:")
print("  retail_orders     — 2 000 rows")
print("    columns: order_id, order_date, region, product_name,")
print("             department, channel, segment, quantity,")
print("             gross_revenue, cogs")
print("  retail_customers  — 150 rows")
print("    columns: customer_id, full_name, tier, home_region,")
print("             first_order_date, total_orders, total_spent")
print()
print("Views:")
print("  vw_monthly_trend     — monthly totals by channel & department")
print("  vw_region_scorecard  — region KPIs: revenue, orders, margin")
print("  vw_dept_summary      — department revenue by channel")
print()
print("Metric View:")
print("  mv_retail_metrics")
print("    dimensions : Region, Channel, Department, Segment")
print("    measures   : Total Revenue, Gross Profit, Order Count,")
print("                 Avg Order Value, Profit Margin")
