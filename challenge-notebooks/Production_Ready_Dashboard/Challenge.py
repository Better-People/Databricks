# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Challenge — Introduction
# MAGIC %md
# MAGIC # Challenge: Databricks Dashboards
# MAGIC
# MAGIC You've completed the three demos. Now it's time to apply those skills independently — from writing SQL datasets to building a polished, interactive dashboard.
# MAGIC
# MAGIC You'll practice:
# MAGIC - Writing custom SQL datasets and parameterized queries for dashboard widgets
# MAGIC - Querying a Unity Catalog metric view using `MEASURE()` syntax
# MAGIC - Building a complete dashboard with counters, charts, and a table
# MAGIC - Adding filters and a parameterized visualization for interactivity
# MAGIC - Identifying the right dataset type and visualization for each scenario
# MAGIC
# MAGIC > **Instructions:** Run the setup cell below, then complete each task. Replace `<FILL_IN>` with the correct SQL or values.
# MAGIC > - Tasks 1–3 are SQL — paste them into the dashboard Data tab, or run them here first to verify.
# MAGIC > - Tasks 4–7 are dashboard UI tasks — read the requirements and build directly in your dashboard.
# MAGIC > - Tasks 8–9 are conceptual — fill in the answers inline in each table.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Run setup
# MAGIC %run ./Setup

# COMMAND ----------

# DBTITLE 1,Task 1 - Custom SQL Dataset
# MAGIC %md
# MAGIC ## Task 1: Write a Custom SQL Dataset
# MAGIC
# MAGIC Write a SQL query that will serve as a **custom SQL dataset** in your dashboard. It should summarize order data by region and channel to power comparison charts.
# MAGIC
# MAGIC Return: `region`, `channel`, `order_count`, `total_revenue`, `gross_profit`, `margin_pct`
# MAGIC
# MAGIC - `gross_profit` = gross_revenue minus cogs
# MAGIC - `margin_pct` = gross profit as a percentage of gross revenue, rounded to 1 decimal
# MAGIC
# MAGIC Sort by `total_revenue` descending.
# MAGIC
# MAGIC > Once you're satisfied the query runs correctly, you'll paste it into the dashboard **Data** tab as a new SQL dataset named `region_channel_summary`.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Task 1 - SQL
# MAGIC %sql
# MAGIC -- Task 1: Custom SQL dataset — region and channel revenue summary
# MAGIC -- Paste this into the dashboard Data tab as a new SQL dataset.
# MAGIC
# MAGIC SELECT
# MAGIC   <FILL_IN>                                                          AS region,
# MAGIC   <FILL_IN>                                                          AS channel,
# MAGIC   COUNT(<FILL_IN>)                                                   AS order_count,
# MAGIC   ROUND(SUM(<FILL_IN>), 2)                                          AS total_revenue,
# MAGIC   ROUND(SUM(<FILL_IN> - <FILL_IN>), 2)                             AS gross_profit,
# MAGIC   ROUND(SUM(<FILL_IN> - <FILL_IN>) / SUM(<FILL_IN>) * 100, 1)     AS margin_pct
# MAGIC FROM retail_orders
# MAGIC GROUP BY <FILL_IN>, <FILL_IN>
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# DBTITLE 1,Task 2 - Parameterized Dataset
# MAGIC %md
# MAGIC ## Task 2: Write a Parameterized SQL Dataset
# MAGIC
# MAGIC Write a SQL query that uses a **dashboard parameter** named `selected_dept` to filter results by department at query time. The query should return all rows when the viewer selects `'All'`.
# MAGIC
# MAGIC Return: `department`, `channel`, `order_count`, `total_revenue`, `avg_order_value`
# MAGIC
# MAGIC > **Key concept:** Dashboard parameters use the `:param_name` syntax inside a SQL dataset. To handle "show everything", combine the filter with an `OR :param = 'All'` condition.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Task 2 - SQL
# MAGIC %sql
# MAGIC -- Task 2: Parameterized SQL dataset — filter by department at query time
# MAGIC -- The :selected_dept parameter will be bound to a filter widget in the dashboard.
# MAGIC
# MAGIC SELECT
# MAGIC   department,
# MAGIC   channel,
# MAGIC   COUNT(order_id)              AS order_count,
# MAGIC   ROUND(SUM(gross_revenue), 2) AS total_revenue,
# MAGIC   ROUND(AVG(gross_revenue), 2) AS avg_order_value
# MAGIC FROM retail_orders
# MAGIC WHERE department = <FILL_IN> OR <FILL_IN> = 'All'
# MAGIC GROUP BY department, channel
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# DBTITLE 1,Task 3 - Metric View Query
# MAGIC %md
# MAGIC ## Task 3: Query the Metric View Using MEASURE() Syntax
# MAGIC
# MAGIC Write a SQL query against `mv_retail_metrics` that returns **total revenue, gross profit, order count, and profit margin** grouped by Region and Channel.
# MAGIC
# MAGIC Key rules for metric view queries:
# MAGIC - Dimension names are capitalized identifiers — wrap them in backticks: `` `Region` ``
# MAGIC - All aggregated measures use `MEASURE(...)` syntax: `MEASURE(\`Total Revenue\`)`
# MAGIC - Use `GROUP BY ALL` instead of listing every column
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Task 3 - SQL
# MAGIC %sql
# MAGIC -- Task 3: Query the metric view using MEASURE() syntax
# MAGIC
# MAGIC SELECT
# MAGIC   `<FILL_IN>`,
# MAGIC   `<FILL_IN>`,
# MAGIC   MEASURE(<FILL_IN>)  AS total_revenue,
# MAGIC   MEASURE(<FILL_IN>)  AS gross_profit,
# MAGIC   MEASURE(<FILL_IN>)  AS order_count,
# MAGIC   MEASURE(<FILL_IN>)  AS profit_margin
# MAGIC FROM <FILL_IN>
# MAGIC GROUP BY ALL;

# COMMAND ----------

# DBTITLE 1,Task 4 - Create Dashboard and Add Datasets
# MAGIC %md
# MAGIC ## Task 4: Create the Dashboard and Add All Datasets
# MAGIC
# MAGIC Create a new Databricks dashboard and give it a clear, descriptive name such as **Retail Performance Dashboard**.
# MAGIC
# MAGIC Add the following six datasets to the dashboard. Use the method that fits the source type for each — not every dataset needs to be entered as custom SQL.
# MAGIC
# MAGIC | Dataset Name | Source | Type |
# MAGIC | --- | --- | --- |
# MAGIC | `region_channel_summary` | SQL query from Task 1 | Custom SQL |
# MAGIC | `retail_orders` | UC table | Unity Catalog object |
# MAGIC | `retail_customers` | UC table | Unity Catalog object |
# MAGIC | `vw_monthly_trend` | UC view | Unity Catalog object |
# MAGIC | `vw_region_scorecard` | UC view | Unity Catalog object |
# MAGIC | `mv_retail_metrics` | Metric view | Unity Catalog object |
# MAGIC
# MAGIC When you're done, the **Data** tab should list all six datasets and each should return rows before you proceed.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Task 5 - KPI Counters and Comparison Charts
# MAGIC %md
# MAGIC ## Task 5: Build KPI Counters and Comparison Charts
# MAGIC
# MAGIC On the first page of your dashboard canvas, add the following:
# MAGIC
# MAGIC 1. A **text widget** with the dashboard title and a brief description of what it shows.
# MAGIC 2. At least **two counter visualizations** from `mv_retail_metrics` surfacing headline KPIs — choose metrics that make business sense as single-number callouts.
# MAGIC 3. A **bar chart** comparing total revenue across the five regions using a region-level dataset.
# MAGIC 4. A **pie chart** showing each channel's share of total revenue.
# MAGIC
# MAGIC Give every widget a clear, descriptive title. Arrange these into a logical visual order before moving on.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Task 6 - Trend Chart and Detail Table
# MAGIC %md
# MAGIC ## Task 6: Build a Trend Chart and a Detail Table
# MAGIC
# MAGIC Still on the same page, add:
# MAGIC
# MAGIC 1. A **line chart** showing how total revenue has changed month-over-month, with a separate line for each channel. Use the `vw_monthly_trend` dataset.
# MAGIC 2. A **table visualization** showing customers ranked by total amount spent from the `retail_customers` dataset. Include at minimum: name, tier, region, and total spent — sorted so the highest spenders appear first.
# MAGIC
# MAGIC After adding these widgets, resize and arrange **all widgets from Tasks 5 and 6** so the page has a clear visual hierarchy: KPIs at the top, comparison charts in the middle, trend and detail near the bottom.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Task 7 - Add Interactivity
# MAGIC %md
# MAGIC ## Task 7: Add Interactivity
# MAGIC
# MAGIC Add two layers of interactivity to the dashboard:
# MAGIC
# MAGIC **A. Page-level filter by region**
# MAGIC
# MAGIC Add an interactive filter widget that lets viewers slice the dashboard by `region`. Connect it to at least two datasets that have a region dimension. Verify that selecting a region value updates the linked visualizations.
# MAGIC
# MAGIC **B. Parameterized visualization for department**
# MAGIC
# MAGIC Add a new SQL dataset to the dashboard using your parameterized query from Task 2 and name it `dept_by_channel`. Build a bar chart from it showing revenue by channel. Add a filter widget that controls the `:selected_dept` parameter so viewers can switch between departments interactively.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Spacer
# MAGIC %md
# MAGIC ---
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC # STOP HERE — Solutions Below
# MAGIC
# MAGIC Only scroll down after you've attempted all 9 tasks!
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC &nbsp;
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Solutions Header
# MAGIC %md
# MAGIC # Solutions
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Solution - Task 1
# MAGIC %sql
# MAGIC -- Solution: Task 1 — Custom SQL dataset (region & channel summary)
# MAGIC SELECT
# MAGIC   region,
# MAGIC   channel,
# MAGIC   COUNT(order_id)                                                   AS order_count,
# MAGIC   ROUND(SUM(gross_revenue), 2)                                      AS total_revenue,
# MAGIC   ROUND(SUM(gross_revenue - cogs), 2)                               AS gross_profit,
# MAGIC   ROUND(SUM(gross_revenue - cogs) / SUM(gross_revenue) * 100, 1)   AS margin_pct
# MAGIC FROM retail_orders
# MAGIC GROUP BY region, channel
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# DBTITLE 1,Solution - Task 2
# MAGIC %sql
# MAGIC -- Solution: Task 2 — Parameterized query filtering by department
# MAGIC SELECT
# MAGIC   department,
# MAGIC   channel,
# MAGIC   COUNT(order_id)              AS order_count,
# MAGIC   ROUND(SUM(gross_revenue), 2) AS total_revenue,
# MAGIC   ROUND(AVG(gross_revenue), 2) AS avg_order_value
# MAGIC FROM retail_orders
# MAGIC WHERE department = :selected_dept OR :selected_dept = 'All'
# MAGIC GROUP BY department, channel
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# DBTITLE 1,Solution - Task 3
# MAGIC %sql
# MAGIC -- Solution: Task 3 — Metric view query using MEASURE() syntax
# MAGIC SELECT
# MAGIC   `Region`,
# MAGIC   `Channel`,
# MAGIC   MEASURE(`Total Revenue`)   AS total_revenue,
# MAGIC   MEASURE(`Gross Profit`)    AS gross_profit,
# MAGIC   MEASURE(`Order Count`)     AS order_count,
# MAGIC   MEASURE(`Profit Margin`)   AS profit_margin
# MAGIC FROM mv_retail_metrics
# MAGIC GROUP BY ALL;

# COMMAND ----------

# DBTITLE 1,Solution - Task 4
# MAGIC %md
# MAGIC ### Solution: Task 4 — Creating the Dashboard and Adding Datasets
# MAGIC
# MAGIC 1. In the sidebar click **+ New → Dashboard**. A draft opens with a default name.
# MAGIC 2. Click the dashboard title at the top and rename it to **Retail Performance Dashboard**.
# MAGIC 3. Click the **Data** tab.
# MAGIC 4. Click **Add SQL dataset**, paste in your Task 1 query, click **Run** to confirm rows return, and rename the dataset to `region_channel_summary`.
# MAGIC 5. Click **Add data → Unity Catalog object**, browse to the schema created by Setup, and select the `retail_orders` table. Rename the dataset to `retail_orders`.
# MAGIC 6. Repeat step 5 for `retail_customers`.
# MAGIC 7. Repeat step 5 for each view: `vw_monthly_trend`, `vw_region_scorecard`.
# MAGIC 8. Repeat step 5 for the metric view `mv_retail_metrics` — it appears alongside tables and views in the Unity Catalog browser.
# MAGIC
# MAGIC The **Data** tab sidebar should now show all six datasets.

# COMMAND ----------

# DBTITLE 1,Solution - Task 5
# MAGIC %md
# MAGIC ### Solution: Task 5 — KPI Counters and Comparison Charts
# MAGIC
# MAGIC **Text widget**
# MAGIC 1. On the **Canvas**, click **Add a text box** and place it at the top of the page.
# MAGIC 2. Type the title **Retail Performance Dashboard** and add a brief description.
# MAGIC
# MAGIC **Counter — Total Revenue**
# MAGIC 1. Click **Add a visualization**, place it below the text widget.
# MAGIC 2. Select `mv_retail_metrics`, choose **Counter**, set the value field to `MEASURE(Total Revenue)`.
# MAGIC 3. Title it **Total Revenue**.
# MAGIC
# MAGIC **Counter — Order Count**
# MAGIC 1. Add another visualization, select `mv_retail_metrics`, choose **Counter**, set the value to `MEASURE(Order Count)`.
# MAGIC 2. Title it **Total Orders**.
# MAGIC
# MAGIC **Bar chart — Revenue by Region**
# MAGIC 1. Add a visualization, select `vw_region_scorecard`, choose **Bar**.
# MAGIC 2. Set X-axis to `region`, Y-axis to `total_revenue`. Title it **Revenue by Region**.
# MAGIC
# MAGIC **Pie chart — Revenue Share by Channel**
# MAGIC 1. Add a visualization, select `region_channel_summary`, choose **Pie**.
# MAGIC 2. Set Color to `channel`, Angle to `total_revenue`. Title it **Revenue Share by Channel**.

# COMMAND ----------

# DBTITLE 1,Solution - Task 6
# MAGIC %md
# MAGIC ### Solution: Task 6 — Trend Chart and Detail Table
# MAGIC
# MAGIC **Line chart — Monthly Revenue by Channel**
# MAGIC 1. Add a visualization, select `vw_monthly_trend`, choose **Line**.
# MAGIC 2. Set X-axis to `order_month`, Y-axis to `total_revenue`.
# MAGIC 3. Set the Color/Series field to `channel` so each channel gets its own line.
# MAGIC 4. Title it **Monthly Revenue Trend by Channel**.
# MAGIC
# MAGIC **Table — Top Customers by Spend**
# MAGIC 1. Add a visualization, select `retail_customers`, choose **Table**.
# MAGIC 2. Include columns: `full_name`, `tier`, `home_region`, `total_orders`, `total_spent`.
# MAGIC 3. Sort by `total_spent` descending. Title it **Top Customers by Spend**.
# MAGIC
# MAGIC **Layout**
# MAGIC 1. Place the text widget and counters in the top row.
# MAGIC 2. Put the bar and pie charts side-by-side in the next row.
# MAGIC 3. Place the line chart across a wide band below.
# MAGIC 4. Put the customer table at the bottom spanning the full width.
# MAGIC 5. Resize until the page reads cleanly from top to bottom.

# COMMAND ----------

# DBTITLE 1,Solution - Task 7
# MAGIC %md
# MAGIC ### Solution: Task 7 — Adding Interactivity
# MAGIC
# MAGIC **A. Page-level filter by region**
# MAGIC 1. On the canvas, click **Add a filter (field/parameter)** and place the widget on the page.
# MAGIC 2. In the configuration panel, set filter type to **Field** and choose `region`.
# MAGIC 3. Connect the filter to both `retail_orders` and `vw_region_scorecard`.
# MAGIC 4. Label it **Filter by Region**.
# MAGIC 5. Switch to preview mode and confirm that selecting a region updates the linked charts.
# MAGIC
# MAGIC **B. Parameterized visualization for department**
# MAGIC 1. Open the **Data** tab, click **Add SQL dataset**, paste in the Task 2 parameterized query, and name it `dept_by_channel`.
# MAGIC 2. Databricks detects `:selected_dept` and creates a parameter entry — configure it as a dropdown or combobox with the five department names as choices, plus `All`.
# MAGIC 3. Return to the **Canvas**, add a visualization from `dept_by_channel`, choose **Bar**, set X-axis to `channel` and Y-axis to `total_revenue`.
# MAGIC 4. Title it **Revenue by Channel — Selected Department**.
# MAGIC 5. Add a filter widget, set it to **Parameter**, choose `:selected_dept`, and label it **Select Department**.
# MAGIC 6. Test by switching departments and confirming the bar chart updates.
