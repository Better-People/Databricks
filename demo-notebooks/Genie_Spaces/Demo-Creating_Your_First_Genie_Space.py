# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Demo Introduction
# MAGIC %md
# MAGIC # DEMO: Create Your First Genie Space
# MAGIC
# MAGIC This demo is for learners who are brand new to Genie Spaces in Databricks.
# MAGIC
# MAGIC Your goal in this notebook is to:
# MAGIC * navigate to the Genie Spaces area in the Databricks workspace
# MAGIC * create a new Genie Space and select its initial data objects from Unity Catalog
# MAGIC * rename the space and add a description via the Settings panel
# MAGIC * verify which tables are attached to the space
# MAGIC * explore the chat interface layout
# MAGIC * ask natural language questions and review the results Genie returns
# MAGIC
# MAGIC We stay intentionally narrow in scope:
# MAGIC * no example SQL queries or custom instructions
# MAGIC * no verified answers or knowledge store configuration
# MAGIC * no sharing or permissions setup
# MAGIC * no advanced quality tuning
# MAGIC
# MAGIC Before you begin:
# MAGIC 1. Run the setup cell below so the demo tables and view exist in Unity Catalog.
# MAGIC 2. The setup cell will print your personal schema name — note it down because you will need it when browsing the Unity Catalog in the Genie Space creation dialog.
# MAGIC
# MAGIC You will add these data objects to your Genie Space:
# MAGIC * `sales_orders` — one row per order, with product, region, channel, revenue, and cost
# MAGIC * `customers` — customer dimension with segment, region, and city
# MAGIC * `vw_monthly_sales` — a pre-aggregated monthly summary view
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Run setup
# MAGIC %run ./Setup

# COMMAND ----------

# DBTITLE 1,Print schema reference for UI
# This cell re-derives your schema name so you can easily copy it
# into the Unity Catalog browser inside the Genie Space creation dialog.
print("")
print("Use this path when browsing for tables in the Genie Space UI:")
print(f"  Catalog : {catalog}")
print(f"  Schema  : {schema}")
print("")
print("Tables to add to your Genie Space:")
print("  - sales_orders")
print("  - customers")
print("  - vw_monthly_sales")

# COMMAND ----------

# DBTITLE 1,Concept - What Is a Genie Space?
# MAGIC %md
# MAGIC ## Concept: What Is a Genie Space?
# MAGIC
# MAGIC A **Genie Space** is a natural-language chat interface that sits on top of your Unity Catalog data.
# MAGIC
# MAGIC * Users type plain English questions such as *"What was total revenue last month?"*
# MAGIC * Genie generates SQL behind the scenes, runs it against your tables, and returns a results table and often an auto-generated chart.
# MAGIC * Each space is scoped to a set of Unity Catalog tables and views you choose — this keeps answers relevant and accurate.
# MAGIC * The SQL Genie writes is always visible, so analysts can inspect and learn from it.
# MAGIC
# MAGIC A Genie Space is different from an AI/BI dashboard:
# MAGIC
# MAGIC | | AI/BI Dashboard | Genie Space |
# MAGIC |---|---|---|
# MAGIC | Purpose | Pre-built visualizations for known questions | Ad-hoc answers to questions not anticipated in advance |
# MAGIC | Audience | Business consumers of fixed reports | Business users who need to explore freely |
# MAGIC | Author role | Analyst builds and publishes charts | Analyst configures data and lets Genie answer |
# MAGIC | Interaction | Read-only, filter-driven | Conversational, question-driven |
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 1 - Navigate to Genie Spaces
# MAGIC %md
# MAGIC ## Step 1: Navigate to Genie Spaces
# MAGIC
# MAGIC Genie Spaces live in a dedicated area of the Databricks workspace sidebar.
# MAGIC
# MAGIC 1. Look at the left-hand sidebar.
# MAGIC 2. Find and click **Genie Spaces** in the sidebar navigation. This opens the Genie Spaces listing page.
# MAGIC 3. The listing page shows all spaces you have access to — it may be empty or show spaces shared with you if this is your first visit.
# MAGIC 4. Each card on the listing page shows the space title, a description, and the owner.
# MAGIC 5. Take a moment to look at the layout before creating your own space.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 2 - Create a New Genie Space
# MAGIC %md
# MAGIC ## Step 2: Create a New Genie Space
# MAGIC
# MAGIC 1. On the Genie Spaces listing page, click **New** in the upper-right corner of the screen.
# MAGIC 2. A dialog opens with a **Unity Catalog browser** where you select the data sources to include in this space.
# MAGIC 3. In the catalog tree on the left of the dialog, expand the `workspace` catalog.
# MAGIC 4. Find and expand your personal schema. The schema name is printed in the setup output above — it starts with `demo_genie_`.
# MAGIC 5. Select `sales_orders`. A checkmark appears.
# MAGIC 6. Select `customers`.
# MAGIC 7. Select `vw_monthly_sales`.
# MAGIC 8. With all three objects checked, click **Create**.
# MAGIC 9. Databricks opens the new Genie Space immediately and lands you on the chat screen.
# MAGIC
# MAGIC > Note: you can always add or remove data objects later. Selecting them during creation is just a convenience starting point.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 3 - Set a Title and Description
# MAGIC %md
# MAGIC ## Step 3: Set a Title and Description
# MAGIC
# MAGIC When the new space opens, it has a placeholder title. Give it a meaningful name before sharing it with anyone.
# MAGIC
# MAGIC 1. Inside the Genie Space, look for the **Configure** button near the top of the space — it may appear as a gear icon or as a labelled button in the upper-right area.
# MAGIC 2. Click **Configure**, then select **About** from the menu that appears.
# MAGIC 3. In the **Name** field, replace the placeholder text with a clear name such as `Retail Sales Q&A`.
# MAGIC 4. In the **Description** field, type a short explanation such as:
# MAGIC    > Ask natural language questions about retail sales orders and customer data for 2024.
# MAGIC 5. Look at the **Default warehouse** field. This is the SQL warehouse Genie uses to run all generated queries.
# MAGIC    * If a warehouse is already selected, leave it as-is.
# MAGIC 7. Confirm the new title now appears in the space header and in your browser tab.
# MAGIC
# MAGIC > The title is also how the space appears on the Genie Spaces listing page, so choose something that describes the data domain clearly.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 4 - Verify Data Objects
# MAGIC %md
# MAGIC ## Step 4: Verify the Data Objects in Your Space
# MAGIC
# MAGIC Before asking questions, confirm that all three data objects are correctly attached to this space.
# MAGIC
# MAGIC 1. Click **Configure**, then select **Data**.
# MAGIC 2. The data panel lists all tables and views currently registered to this space.
# MAGIC 3. Confirm that all three objects are present:
# MAGIC    * `sales_orders`
# MAGIC    * `customers`
# MAGIC    * `vw_monthly_sales`
# MAGIC 4. Click on `sales_orders` to view its details.
# MAGIC 5. Two tabs appear:
# MAGIC    * **Overview** — shows column names and data types. These are the exact terms Genie uses when generating SQL.
# MAGIC    * **Sample data** — shows a preview of actual rows from the table.
# MAGIC 6. Review the column names in the Overview tab. Notice columns like `region`, `product_category`, `channel`, `net_revenue`, and `cost`. Genie maps your plain-English terms to these column names automatically.
# MAGIC 7. Click the back arrow to return to the full data list.
# MAGIC 8. If any object is missing, click the **Add** button to browse Unity Catalog and add it now.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 5 - Explore the Chat Interface Layout
# MAGIC %md
# MAGIC ## Step 5: Explore the Chat Interface Layout
# MAGIC
# MAGIC Before asking your first question, spend a minute identifying the main areas of the Genie Space chat interface.
# MAGIC
# MAGIC The interface has these key regions:
# MAGIC
# MAGIC * **Chat window** — the large centre panel where you type questions and read Genie’s responses. It opens by default when you access the space.
# MAGIC * **Chat history** — the left-hand panel that lists all your previous conversations, each organized as a separate thread. Genie remembers the context of earlier questions within the same thread, so you can ask follow-up questions without restating the topic.
# MAGIC * **Configure panel** — a collapsible panel (usually on the right) with three tabs:
# MAGIC   * **About** — shows the space title, description, owner, and common questions if any have been configured.
# MAGIC   * **Data** — lists the tables and views attached to this space. Expand any entry to see its columns and descriptions.
# MAGIC   * **Instructions** — shows any custom text instructions or SQL expressions a space author has added to guide Genie’s responses (empty in a brand-new space).
# MAGIC * **Share** — a button or link for sharing the space with other workspace members or generating a shareable link.
# MAGIC
# MAGIC Familiarise yourself with each area before asking questions.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 6 - Ask Your First Questions
# MAGIC %md
# MAGIC ## Step 6: Ask Your First Natural Language Questions
# MAGIC
# MAGIC Type each question below into the chat window and observe what Genie returns.
# MAGIC
# MAGIC **Question 1 — a broad aggregation:**
# MAGIC > What is the total revenue by region?
# MAGIC
# MAGIC After Genie responds:
# MAGIC 1. You should see a results table with one row per region and a `total_revenue` column.
# MAGIC 2. Genie may also auto-generate a visualization alongside the table.
# MAGIC 3. Look for a **Show code** link above the response. Click it to see the exact SQL query Genie wrote. Notice it uses the `net_revenue` column from `sales_orders` and groups by `region`.
# MAGIC
# MAGIC **Question 2 — a follow-up in the same thread:**
# MAGIC > Which of those regions had the highest average order value?
# MAGIC
# MAGIC 4. Type this as a follow-up in the same chat thread — do not start a new chat.
# MAGIC 5. Genie uses the context from the previous exchange. You do not need to restate the table name.
# MAGIC 6. Review the new result. Notice how the question is resolved against the same data without repeating yourself.
# MAGIC
# MAGIC **Question 3 — a different aggregation:**
# MAGIC > How many orders came through each sales channel?
# MAGIC
# MAGIC 7. This time Genie should use the `channel` column from `sales_orders`.
# MAGIC 8. Review the SQL it generates.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 7 - Questions Across Multiple Tables and the View
# MAGIC %md
# MAGIC ## Step 7: Ask Questions That Use Different Data Objects
# MAGIC
# MAGIC Now ask questions that draw on the `customers` table or the `vw_monthly_sales` view.
# MAGIC
# MAGIC **Question 4 — using the customers table:**
# MAGIC > How many customers do we have in each segment?
# MAGIC
# MAGIC Genie should use the `customers` table and the `segment` column. Review the result and the generated SQL.
# MAGIC
# MAGIC **Question 5 — a time-based trend question:**
# MAGIC > Show me total revenue by month across 2024.
# MAGIC
# MAGIC Genie may use `vw_monthly_sales` directly (which is already aggregated by month), or it may aggregate the `order_date` column from `sales_orders`. Either approach is correct.
# MAGIC * Check the SQL tab to see which data object Genie chose.
# MAGIC * If it used `sales_orders` directly, note how it applied `DATE_TRUNC` or similar date functions automatically.
# MAGIC
# MAGIC **Question 6 — a profitability question:**
# MAGIC > Which product category has the highest profit margin?
# MAGIC
# MAGIC Genie needs to calculate profit (net_revenue minus cost) and divide by revenue. Observe how it handles derived calculations.
# MAGIC
# MAGIC After each question, check whether Genie returned a table, a chart, or both. If a result looks unexpected or incomplete, type a clarifying follow-up in the same thread. That is the correct way to refine Genie’s understanding within a conversation.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Summary
# MAGIC %md
# MAGIC ---
# MAGIC
# MAGIC ## Summary
# MAGIC
# MAGIC By the end of this notebook, the learner should have:
# MAGIC
# MAGIC * navigated to the Genie Spaces listing page in the Databricks workspace sidebar
# MAGIC * created a new Genie Space by selecting three Unity Catalog objects from a personal schema
# MAGIC * set a meaningful title, description, and SQL warehouse via the Configure → Settings panel
# MAGIC * verified all attached data objects and reviewed column details via the Configure → Data panel
# MAGIC * identified the key areas of the chat interface: chat window, history, context panel, and share button
# MAGIC * asked natural language questions and reviewed the generated SQL behind each response
# MAGIC * asked follow-up questions within the same thread, using Genie’s conversational context
# MAGIC
# MAGIC More importantly, the learner should understand:
# MAGIC * a Genie Space is scoped to a set of Unity Catalog tables you choose — not all data in the workspace
# MAGIC * Genie always generates SQL — every response is backed by a query you can inspect
# MAGIC * questions in the same thread share context, enabling natural conversation without repeating yourself
# MAGIC
# MAGIC The next demo will cover how to improve Genie response quality by adding instructions, example SQL queries, and verified answers to the space.
