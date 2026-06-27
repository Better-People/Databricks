# Databricks notebook source
# DBTITLE 1,Demo Introduction
# MAGIC %md
# MAGIC # DEMO: Tune Your Genie Space for Better Responses
# MAGIC
# MAGIC This demo continues directly from Demo 1. You already created a `Retail Sales Q&A` Genie Space with three data objects and asked your first natural language questions. Most of them worked — but five specific questions produced wrong, empty, or unreliable results.
# MAGIC
# MAGIC This demo is about diagnosing those five failures and applying every tuning tool Genie provides to fix them. Rather than presenting the tools in isolation, each step solves a real problem that came out of live use.
# MAGIC
# MAGIC Your goal in this notebook is to:
# MAGIC * add plain-text instructions for default behaviour rules
# MAGIC * define SQL expressions for business metrics (profit, AOV, profit margin)
# MAGIC * define filter and field expressions for business terminology and segmentation
# MAGIC * add join relationships so Genie correctly links `sales_orders` to `customers` and `sales_targets`
# MAGIC * add example queries for complex and anticipated questions
# MAGIC * build parameterized example queries as verified trusted assets
# MAGIC * register a Unity Catalog SQL function as a trusted asset
# MAGIC * add column metadata, descriptions, and synonyms to the knowledge store
# MAGIC * configure prompt matching for value recognition and spelling correction
# MAGIC * understand when metric views and Unity Catalog metadata are the right long-term answer
# MAGIC
# MAGIC We stay intentionally narrow:
# MAGIC * no benchmarks
# MAGIC * no sharing or permissions configuration
# MAGIC * no agent mode
# MAGIC
# MAGIC Before you begin:
# MAGIC 1. Run the setup cell below — it adds a `sales_targets` table and a SQL function `fn_profit_margin` to your schema.
# MAGIC 2. **Add `sales_targets` to your existing Genie Space**: in your `Retail Sales Q&A` space, click **Configure > Data > Add**, browse to your schema, and select `sales_targets`.
# MAGIC 3. Open the Genie Space alongside this notebook — you will switch between the two throughout.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Run setup
# MAGIC %run ./Setup

# COMMAND ----------

# DBTITLE 1,Print schema reference for UI
# Print schema context and the new assets added by this demo's setup.
print(f"Catalog : {catalog}")
print(f"Schema  : {schema}")
print("")
print("New assets added by setup (Demo 2):")
print(f"  TABLE     →  sales_targets")
print(f"  FUNCTION  →  fn_profit_margin")
print("")
print("Action required: add sales_targets to your Genie Space")
print("  Configure > Data > Add → browse to your schema → select sales_targets")

# COMMAND ----------

# DBTITLE 1,The 5 Failing Questions
# MAGIC %md
# MAGIC ## The 5 Questions That Got It Wrong
# MAGIC
# MAGIC After Demo 1, your class kept exploring. Within a few minutes, five questions produced wrong, empty, or unreliable results. Each one reveals a different gap in the space configuration.
# MAGIC
# MAGIC | # | Question asked | What happened | Root cause | Fix we’ll apply |
# MAGIC |---|---|---|---|---|
# MAGIC | 1 | *What is our profit?* | Genie returned `net_revenue` as profit, ignoring cost entirely | No definition of “profit” in the space — Genie guessed | SQL Expression (Measure) |
# MAGIC | 2 | *Show me B2B sales* | Empty result — zero rows returned | `segment` stores `'Corporate'`, not `'B2B'`; Genie couldn’t match the term | Column synonym + entity matching |
# MAGIC | 3 | *What’s our AOV trend by quarter?* | Genie generated a wrong or inconsistent formula each time | `AOV` is not a column name; Genie guessed the formula differently on each attempt | SQL Expression (Measure) with synonym |
# MAGIC | 4 | *Are we hitting our regional targets?* | “I don’t have information about sales targets” | `sales_targets` has no defined relationship to `sales_orders`; join not obvious | Join relationship + example query |
# MAGIC | 5 | *Show me profit margin by category* | Different result on each attempt — Genie wrote a different formula every time | No verified formula; no trusted asset | SQL function (Trusted Asset) |
# MAGIC
# MAGIC Every step in this demo fixes one or more of these failures. By the end, you will re-test all five and confirm the space responds correctly.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Concept - The Genie Tuning Toolkit
# MAGIC %md
# MAGIC ## Concept: The Genie Tuning Toolkit
# MAGIC
# MAGIC Genie provides multiple layers of tuning, each solving a different class of problem. Databricks recommends applying them in priority order: SQL first, text instructions only as a last resort.
# MAGIC
# MAGIC | Tool | Best for | Where in the UI |
# MAGIC |---|---|---|
# MAGIC | **SQL Expression — Measure** | KPI definitions: profit, AOV, margin, conversion rate | Configure > Instructions > SQL Expressions |
# MAGIC | **SQL Expression — Filter** | Named business conditions: B2B, high-value orders | Configure > Instructions > SQL Expressions |
# MAGIC | **SQL Expression — Field** | Derived grouping attributes: quarter label, order size tier | Configure > Instructions > SQL Expressions |
# MAGIC | **Join relationships** | Correctly linking two tables without guessing the join key | Configure > Instructions > SQL Expressions |
# MAGIC | **Example queries** | Complex, multi-step, or frequently anticipated questions | Configure > Instructions > SQL Queries |
# MAGIC | **Parameterized queries** | Trusted, user-adjustable answers (verified logic) | Configure > Instructions > SQL Queries |
# MAGIC | **SQL functions** | Verified calculations from Unity Catalog (run as-is, no guessing) | Configure > Instructions > SQL Queries |
# MAGIC | **Column metadata & synonyms** | Teaching Genie business terms at the column level | Configure > Data > [table] > pencil icon |
# MAGIC | **Prompt matching** | Abbreviation recognition, spelling correction, value mapping | Configure > Data > [table] > column Advanced settings |
# MAGIC | **Text instructions** | Behavioural rules that cannot be expressed as SQL | Configure > Instructions > Text |
# MAGIC
# MAGIC **Limits to keep in mind:**
# MAGIC * Instructions: 100 per space (each query, each function, and the full text block each count as 1)
# MAGIC * Knowledge store snippets: 200 per space (table descriptions, join relationships, and SQL expressions share this limit)
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 1 - Text Instructions
# MAGIC %md
# MAGIC ## Step 1: Add Text Instructions
# MAGIC
# MAGIC **Fixes:** default date range behaviour and terminology ambiguity across the whole space.
# MAGIC
# MAGIC Text instructions are plain English guidance. Use them sparingly — only for rules that cannot be expressed as SQL.
# MAGIC
# MAGIC 1. In your Genie Space, click **Configure** in the upper-right area.
# MAGIC 2. Click **Instructions** from the menu that appears.
# MAGIC 3. Click the **Text** tab.
# MAGIC 4. In the **General instructions** text area, enter the following:
# MAGIC
# MAGIC    > When a user does not specify a date range, assume they mean the full year 2024.
# MAGIC    >
# MAGIC    > When users refer to “direct” sales or orders, they mean the Online channel.
# MAGIC    >
# MAGIC    > When a user asks for “top” results without specifying a number, return the top 5.
# MAGIC    >
# MAGIC    > Always round monetary values to 2 decimal places in results.
# MAGIC
# MAGIC 5. Click **Save**.
# MAGIC
# MAGIC > Keep text instructions short, specific, and non-overlapping. Conflicting or vague instructions reduce Genie’s accuracy. If a rule can be expressed as a SQL expression, use that instead.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 2 - SQL Expressions: Measures
# MAGIC %md
# MAGIC ## Step 2: Define SQL Expressions — Measures
# MAGIC
# MAGIC **Fixes:** Failing Questions 1 (profit) and 3 (AOV).
# MAGIC
# MAGIC Measures define KPIs and aggregations. Genie applies them exactly as written, eliminating guessing.
# MAGIC
# MAGIC 1. Click **Configure > Instructions**.
# MAGIC 2. Click the **SQL Expressions** tab.
# MAGIC 3. Click **Add** and select **Measure**.
# MAGIC
# MAGIC **Measure 1 — Profit**
# MAGIC * Name: `Profit`
# MAGIC * Code: `SUM(net_revenue - cost)`
# MAGIC * Synonyms: `gross profit, net profit, earnings, margin dollars`
# MAGIC * Instructions: `Use when users ask about profit, earnings, or how much money was made after costs. Do not confuse with net_revenue alone.`
# MAGIC * Click **Save**.
# MAGIC
# MAGIC 4. Click **Add > Measure** again.
# MAGIC
# MAGIC **Measure 2 — Profit Margin**
# MAGIC * Name: `Profit Margin`
# MAGIC * Code: `ROUND(SUM(net_revenue - cost) / NULLIF(SUM(net_revenue), 0) * 100, 2)`
# MAGIC * Synonyms: `margin, gross margin, margin %, profitability, margin percentage`
# MAGIC * Instructions: `Returns profit as a percentage of revenue. Results are already multiplied by 100 — display as a percentage. Use NULLIF to avoid division by zero.`
# MAGIC * Click **Save**.
# MAGIC
# MAGIC 5. Click **Add > Measure** again.
# MAGIC
# MAGIC **Measure 3 — Average Order Value (AOV)**
# MAGIC * Name: `Average Order Value`
# MAGIC * Code: `ROUND(SUM(net_revenue) / NULLIF(COUNT(DISTINCT order_id), 0), 2)`
# MAGIC * Synonyms: `AOV, average basket, average transaction value, average spend per order`
# MAGIC * Instructions: `Use when users ask about AOV, average order value, or average basket size. Count distinct order_id to avoid inflating the average.`
# MAGIC * Click **Save**.
# MAGIC
# MAGIC > Each SQL expression counts as one knowledge store snippet toward the 200-snippet limit.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 3 - SQL Expressions: Filter and Field
# MAGIC %md
# MAGIC ## Step 3: Define SQL Expressions — Filter and Field
# MAGIC
# MAGIC **Fixes:** Failing Question 2 (B2B) and adds a useful segmentation field for future questions.
# MAGIC
# MAGIC **Filter — B2B Orders**
# MAGIC
# MAGIC 1. Click **Configure > Instructions > SQL Expressions**.
# MAGIC 2. Click **Add** and select **Filter**.
# MAGIC 3. Enter:
# MAGIC    * Name: `B2B Orders`
# MAGIC    * Code: `customers.segment = 'Corporate'`
# MAGIC    * Synonyms: `B2B, business customers, corporate accounts, enterprise customers, business-to-business`
# MAGIC    * Instructions: `Apply when users ask about B2B, corporate, or business-to-business activity. This filter requires joining sales_orders to customers on customer_id.`
# MAGIC 4. Click **Save**.
# MAGIC
# MAGIC > The filter references the `customers` table. Genie will apply the join defined in Step 4 to resolve it.
# MAGIC
# MAGIC **Field — Order Size Tier**
# MAGIC
# MAGIC 5. Click **Add** and select **Field**.
# MAGIC 6. Enter:
# MAGIC    * Name: `Order Size Tier`
# MAGIC    * Code: `CASE WHEN net_revenue < 100 THEN 'Small' WHEN net_revenue < 500 THEN 'Medium' ELSE 'Large' END`
# MAGIC    * Synonyms: `order tier, deal size, order bucket, size band`
# MAGIC    * Instructions: `Groups individual orders into Small (under $100), Medium ($100–$499), or Large ($500+) based on net_revenue. Use when users ask to break down results by order size.`
# MAGIC 7. Click **Save**.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 4 - Define Join Relationships
# MAGIC %md
# MAGIC ## Step 4: Define Join Relationships
# MAGIC
# MAGIC **Fixes:** Failing Question 4 (targets). Also makes the B2B filter in Step 3 reliably resolvable.
# MAGIC
# MAGIC Without explicit join definitions, Genie must guess how to relate tables. For non-obvious relationships — especially when the join involves a derived value like a quarter string — guessing fails.
# MAGIC
# MAGIC > Tip: If your Unity Catalog tables have formal foreign key constraints defined, Genie reads them automatically and may suggest joins via knowledge mining. Our demo tables don’t have foreign keys, so we define the relationships manually.
# MAGIC
# MAGIC **Join 1 — sales_orders → customers**
# MAGIC
# MAGIC 1. Click **Configure > Instructions**.
# MAGIC 2. Click the **SQL Expressions** tab.
# MAGIC 3. Scroll to the **Joins** section and click **Add join**.
# MAGIC 4. In the join editor, enter:
# MAGIC    * Left table: `sales_orders`
# MAGIC    * Right table: `customers`
# MAGIC    * Join condition: `sales_orders.customer_id = customers.customer_id`
# MAGIC    * Description: `Links each order to the purchasing customer's profile, including their segment, region, and city. Use this join for any question that asks about customer segment, B2B sales, or city-level breakdowns.`
# MAGIC 5. Click **Save**.
# MAGIC
# MAGIC **Join 2 — sales_orders → sales_targets**
# MAGIC
# MAGIC 6. Click **Add join** again.
# MAGIC 7. Enter:
# MAGIC    * Left table: `sales_orders`
# MAGIC    * Right table: `sales_targets`
# MAGIC    * Join condition: `sales_orders.region = sales_targets.region AND CONCAT('Q', QUARTER(sales_orders.order_date)) = sales_targets.quarter AND YEAR(sales_orders.order_date) = sales_targets.year`
# MAGIC    * Description: `Links each order to its regional quarterly target. The quarter is derived from order_date using QUARTER() and prefixed with Q to match the sales_targets.quarter format (Q1, Q2, Q3, Q4). Use for any question about targets, goals, or performance vs plan.`
# MAGIC 8. Click **Save**.
# MAGIC
# MAGIC > Each join relationship counts as one knowledge store snippet toward the 200 limit.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 5 - Add Example Queries
# MAGIC %md
# MAGIC ## Step 5: Add Example Queries
# MAGIC
# MAGIC **Fixes:** Failing Question 4 (targets) — provides the exact multi-table join logic for the most common targets question.
# MAGIC
# MAGIC Example queries show Genie how to handle complex, multi-step patterns. Write the sample question the way a real user would ask it — the phrasing matters as much as the SQL.
# MAGIC
# MAGIC **Example Query 1 — Performance vs Target**
# MAGIC
# MAGIC 1. Click **Configure > Instructions**.
# MAGIC 2. Click the **SQL Queries** tab.
# MAGIC 3. Click **Add SQL query**.
# MAGIC 4. In the question title field at the top, enter:
# MAGIC    > How is each region tracking against target this quarter?
# MAGIC 5. In the SQL editor below, paste the query from the code cell below this one.
# MAGIC 6. Click **Usage guidance** near the bottom of the editor.
# MAGIC 7. Enter: `Use when users ask about target attainment, performance vs plan, or whether regions are hitting their goals. Requires the sales_targets table.`
# MAGIC 8. Click **Save**.
# MAGIC
# MAGIC **Example Query 2 — Segment and Channel Breakdown**
# MAGIC
# MAGIC 9. Click **Add SQL query** again.
# MAGIC 10. Enter question title:
# MAGIC     > Show a breakdown of performance by segment and channel
# MAGIC 11. In the SQL editor, paste the second query from the code cell below.
# MAGIC 12. Add usage guidance: `Use when users ask for a performance breakdown without specifying exact columns. This is the canonical breakdown view combining customer segment and order channel.`
# MAGIC 13. Click **Save**.
# MAGIC
# MAGIC > Non-parameterized example queries are not trusted assets — Genie uses them as guidance and may adapt the SQL for similar questions. Only parameterized queries produce verified trusted responses.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Reference SQL: Example queries to paste
# MAGIC %sql
# MAGIC -- =============================================================
# MAGIC -- EXAMPLE QUERY 1: Region vs Target
# MAGIC -- Question title: "How is each region tracking against target this quarter?"
# MAGIC -- Paste this SQL into the Genie Space example query editor (Step 5).
# MAGIC -- =============================================================
# MAGIC
# MAGIC SELECT
# MAGIC   t.region,
# MAGIC   t.quarter,
# MAGIC   t.target_revenue,
# MAGIC   ROUND(SUM(s.net_revenue), 2)                                AS actual_revenue,
# MAGIC   ROUND(SUM(s.net_revenue) / t.target_revenue * 100, 2)      AS pct_of_target,
# MAGIC   CASE
# MAGIC     WHEN SUM(s.net_revenue) >= t.target_revenue THEN 'On Track'
# MAGIC     ELSE 'Below Target'
# MAGIC   END                                                         AS status
# MAGIC FROM sales_orders s
# MAGIC JOIN sales_targets t
# MAGIC   ON  s.region = t.region
# MAGIC   AND CONCAT('Q', QUARTER(s.order_date)) = t.quarter
# MAGIC   AND YEAR(s.order_date) = t.year
# MAGIC GROUP BY t.region, t.quarter, t.target_revenue
# MAGIC ORDER BY t.region, t.quarter;
# MAGIC
# MAGIC -- =============================================================
# MAGIC -- EXAMPLE QUERY 2: Segment and Channel Breakdown
# MAGIC -- Question title: "Show a breakdown of performance by segment and channel"
# MAGIC -- Paste this SQL into the Genie Space example query editor (Step 5).
# MAGIC -- =============================================================
# MAGIC
# MAGIC SELECT
# MAGIC   c.segment,
# MAGIC   s.channel,
# MAGIC   COUNT(s.order_id)                                                       AS order_count,
# MAGIC   ROUND(SUM(s.net_revenue), 2)                                            AS total_revenue,
# MAGIC   ROUND(SUM(s.net_revenue - s.cost), 2)                                   AS total_profit,
# MAGIC   ROUND(SUM(s.net_revenue - s.cost) / NULLIF(SUM(s.net_revenue),0)*100,2) AS profit_margin_pct
# MAGIC FROM sales_orders s
# MAGIC JOIN customers c ON s.customer_id = c.customer_id
# MAGIC GROUP BY c.segment, s.channel
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# DBTITLE 1,Step 6 - Parameterized Queries (Trusted Assets)
# MAGIC %md
# MAGIC ## Step 6: Add Parameterized Example Queries — Trusted Assets
# MAGIC
# MAGIC **Produces:** a verified trusted answer for any region-scoped order question.
# MAGIC
# MAGIC A parameterized query is an example query that contains a runtime placeholder (`:parameter_name`). When Genie uses it to answer a question, it fills in the parameter value and runs the exact query as written. The response is labelled **Trusted** because the SQL logic has been verified by a space author.
# MAGIC
# MAGIC 1. Click **Configure > Instructions > SQL Queries**.
# MAGIC 2. Click **Add SQL query**.
# MAGIC 3. In the question title field, enter:
# MAGIC    > Show me all orders for a specific region
# MAGIC 4. In the SQL editor, paste the query from the code cell below this one.
# MAGIC 5. Add the parameter:
# MAGIC    * Place your cursor on the `:region` token in the query, or type `:region` directly in the SQL.
# MAGIC    * Click the **pencil icon** next to the `region` parameter name in the parameter list.
# MAGIC    * Set **Data type** to `String`.
# MAGIC    * Set **Comment** to: `The region name. Valid values: Northeast, Southeast, Midwest, West, Northwest`
# MAGIC    * Click **Save** to close the parameter dialog.
# MAGIC 6. Add usage guidance: `Use when a user asks to see orders, revenue, or activity for a named region. The user’s region name is passed as the parameter value.`
# MAGIC 7. Click **Save** to save the example query.
# MAGIC
# MAGIC **How to verify it worked:**
# MAGIC
# MAGIC Go to the chat window and ask: *Show me all orders for the West region.*
# MAGIC Genie should return results labelled **Trusted** and show a parameter value of `West`. You can change the parameter value in the response to re-run for a different region without asking a new question.
# MAGIC
# MAGIC > Trusted assets are the highest-confidence Genie responses. They run verified SQL with user-supplied values rather than generating SQL from scratch.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Reference SQL: Parameterized query
# MAGIC %sql
# MAGIC -- =============================================================
# MAGIC -- PARAMETERIZED QUERY: Orders for a specific region
# MAGIC -- Question title: "Show me all orders for a specific region"
# MAGIC -- Paste this into the Genie Space parameterized example query editor.
# MAGIC -- The :region token becomes the trusted parameter.
# MAGIC -- =============================================================
# MAGIC
# MAGIC SELECT
# MAGIC   s.order_id,
# MAGIC   s.order_date,
# MAGIC   c.customer_name,
# MAGIC   c.segment,
# MAGIC   s.product_name,
# MAGIC   s.product_category,
# MAGIC   s.channel,
# MAGIC   s.quantity,
# MAGIC   s.net_revenue,
# MAGIC   ROUND(s.net_revenue - s.cost, 2) AS profit
# MAGIC FROM sales_orders s
# MAGIC JOIN customers c ON s.customer_id = c.customer_id
# MAGIC WHERE s.region = :region
# MAGIC ORDER BY s.order_date DESC;

# COMMAND ----------

# DBTITLE 1,Step 7 - Register SQL Function as Trusted Asset
# MAGIC %md
# MAGIC ## Step 7: Register a SQL Function as a Trusted Asset
# MAGIC
# MAGIC **Fixes:** Failing Question 5 (profit margin inconsistency).
# MAGIC
# MAGIC A SQL function registered in Unity Catalog can be added to a Genie Space as a trusted asset. When Genie uses it to answer a question, the result is labelled **Trusted** — the exact function logic runs every time, with no variation between attempts.
# MAGIC
# MAGIC The setup notebook created `fn_profit_margin(revenue DOUBLE, cost DOUBLE)` in your schema. Its function comment already explains when to use it — Genie reads that comment as context.
# MAGIC
# MAGIC 1. Click **Configure > Instructions**.
# MAGIC 2. Click the **SQL Queries** tab.
# MAGIC 3. Click **Add SQL function** (this is a separate button from **Add SQL query**).
# MAGIC 4. In the function browser, navigate to your schema and select `fn_profit_margin`.
# MAGIC 5. Click **Add** to register it in the space.
# MAGIC 6. Click **Save**.
# MAGIC
# MAGIC **How to verify it worked:**
# MAGIC
# MAGIC In the chat, ask: *What is the profit margin for each product category?*
# MAGIC Genie should call `fn_profit_margin(net_revenue, cost)` and return consistent results labelled **Trusted**. Click **Show more** in the response to confirm the function name and the comment explaining what it does.
# MAGIC
# MAGIC > Users of the space must have `EXECUTE` permission on the function in Unity Catalog. For this demo, you own the function, so no grant is needed. In production, grant `EXECUTE ON FUNCTION` to the appropriate group.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 8 - Column Metadata and Synonyms
# MAGIC %md
# MAGIC ## Step 8: Add Column Metadata and Synonyms
# MAGIC
# MAGIC **Fixes:** Failing Question 2 (B2B) at the column level. Also improves general question accuracy for any column with ambiguous naming.
# MAGIC
# MAGIC Column metadata and synonyms live in the knowledge store scoped to this space. They do not change Unity Catalog. Each edit teaches Genie how users talk about a column in the real world.
# MAGIC
# MAGIC **For `sales_orders.net_revenue`:**
# MAGIC
# MAGIC 1. Click **Configure > Data**.
# MAGIC 2. Click `sales_orders`.
# MAGIC 3. Find the `net_revenue` column and click the **pencil icon** next to it.
# MAGIC 4. Set **Description** to: `Total revenue collected for this order after applying the discount. Calculated as quantity × unit_price × (1 − discount_pct). This is the primary revenue measure for the space.`
# MAGIC 5. Set **Synonyms** to: `revenue, sales, turnover, income, top line`
# MAGIC 6. Click **Save**.
# MAGIC
# MAGIC **For `sales_orders.discount_pct`:**
# MAGIC
# MAGIC 7. Click the **pencil icon** next to `discount_pct`.
# MAGIC 8. Set **Description** to: `Discount rate applied to this order, expressed as a decimal where 0.10 means 10% off.`
# MAGIC 9. Set **Synonyms** to: `discount, promo rate, markdown, offer rate`
# MAGIC 10. Click **Save**.
# MAGIC
# MAGIC **For `customers.segment`:**
# MAGIC
# MAGIC 11. Click the back arrow to return to the data list, then click `customers`.
# MAGIC 12. Click the **pencil icon** next to `segment`.
# MAGIC 13. Set **Description** to: `Customer classification. Values: Consumer (individual shoppers), Corporate (business buyers also known as B2B), Home Office (small home-based businesses).`
# MAGIC 14. Set **Synonyms** to: `customer type, account type, tier, B2B, B2C`
# MAGIC 15. Click **Save**.
# MAGIC
# MAGIC > The description is the most impactful field — Genie reads it as context when generating SQL. Synonyms help match conversational language to column names.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 9 - Configure Prompt Matching
# MAGIC %md
# MAGIC ## Step 9: Configure Prompt Matching
# MAGIC
# MAGIC **Fixes:** Failing Question 2 (B2B) at the value level. Also improves accuracy for any question referencing specific values like region names, category names, or channel names.
# MAGIC
# MAGIC Prompt matching has two components:
# MAGIC
# MAGIC * **Format assistance** — samples representative values from the column and adds them to Genie’s context, so it understands data types and formatting patterns (e.g., dates stored as `YYYY-MM-DD`, decimals stored as `0.10` not `10%`).
# MAGIC * **Entity matching** — builds a curated list of distinct values for a column so Genie can match user language to actual stored values (e.g., `FL` → `Florida`, `B2B` → `Corporate`, `clothes` → `Clothing`).
# MAGIC
# MAGIC **Enable entity matching on `customers.segment`:**
# MAGIC
# MAGIC 1. In `customers`, click the **pencil icon** next to `segment`.
# MAGIC 2. Click **Advanced settings**.
# MAGIC 3. Toggle **Entity matching** on.
# MAGIC 4. Click **Save**.
# MAGIC
# MAGIC Genie now loads the distinct segment values (`Consumer`, `Corporate`, `Home Office`) as context. When a user asks about *B2B customers*, Genie maps `B2B` to `Corporate` and generates the correct filter.
# MAGIC
# MAGIC **Enable entity matching on `sales_orders.region`:**
# MAGIC
# MAGIC 5. Navigate to `sales_orders`, then click the pencil icon next to `region`.
# MAGIC 6. Click **Advanced settings** and toggle **Entity matching** on.
# MAGIC 7. Click **Save**.
# MAGIC
# MAGIC **Enable entity matching on `sales_orders.product_category`:**
# MAGIC
# MAGIC 8. Repeat for `product_category` on `sales_orders`.
# MAGIC
# MAGIC **Enable format assistance on `sales_orders.order_date`:**
# MAGIC
# MAGIC 9. Click the pencil icon next to `order_date`.
# MAGIC 10. Click **Advanced settings**.
# MAGIC 11. Confirm **Format assistance** is toggled on (it is usually on by default for date columns).
# MAGIC 12. Click **Save**.
# MAGIC
# MAGIC > Entity matching data is generated using the space author’s data permissions and stored in your workspace’s storage bucket. Tables with row filters or column masks are excluded from prompt matching.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Concept - Metric Views and UC Metadata
# MAGIC %md
# MAGIC ## Concept: Where Metric Views and Unity Catalog Metadata Fit
# MAGIC
# MAGIC Everything configured so far is **scoped to this Genie Space only**. It does not change Unity Catalog. That scope is intentional when tuning is audience-specific — but for widely-shared business logic it creates a maintenance problem: the same measures and synonyms need to be duplicated across every space, dashboard, and team that uses the same data.
# MAGIC
# MAGIC Two Unity Catalog features solve this at a higher level:
# MAGIC
# MAGIC **1. Unity Catalog table and column comments**
# MAGIC
# MAGIC When you set a `COMMENT` on a table or column in Unity Catalog (via SQL, Catalog Explorer, or `ALTER TABLE ... ALTER COLUMN`), Genie reads that comment automatically as context for every space that includes that table. Space-level descriptions (Configure > Data) override UC comments locally for just this space, without touching UC.
# MAGIC
# MAGIC | Scope | Set via | Effect |
# MAGIC |---|---|---|
# MAGIC | Space-level description | Configure > Data > pencil icon | Overrides UC comment for this space only |
# MAGIC | UC COMMENT | `ALTER TABLE ... ALTER COLUMN ... COMMENT '...'` | Used by all Genie Spaces, dashboards, and SQL editors workspace-wide |
# MAGIC
# MAGIC **2. Unity Catalog Metric Views**
# MAGIC
# MAGIC A metric view is a Unity Catalog object that encodes your measures, fields, filters, and synonyms as YAML — once, at the catalog level. When you add a metric view to a Genie Space, all its pre-defined measures, fields, and synonyms are available immediately. There is nothing to re-enter in the space.
# MAGIC
# MAGIC | Space-level tuning | Metric view (UC-level) |
# MAGIC |---|---|
# MAGIC | Only this space benefits | All Genie Spaces, dashboards, and notebooks benefit |
# MAGIC | Authors must re-enter definitions per space | Define once, reuse everywhere |
# MAGIC | Synonyms must be manually added | Synonyms from the metric view are automatically imported into Genie |
# MAGIC | Good for audience-specific logic | Good for shared, organisation-wide business logic |
# MAGIC
# MAGIC **When to use which approach:**
# MAGIC * Use space-level tuning when the definition is specific to this audience and unlikely to be shared.
# MAGIC * Use UC metric views when the measure or join is a company-standard definition that needs to be consistent across multiple Genie Spaces, dashboards, and the SQL editor.
# MAGIC * Use UC column comments as a baseline for all teams — they cost nothing to add and improve every downstream tool automatically.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 10 - Re-test the 5 Failing Questions
# MAGIC %md
# MAGIC ## Step 10: Re-test the 5 Failing Questions
# MAGIC
# MAGIC Go back to the `Retail Sales Q&A` Genie Space and ask each failing question again. Start a fresh chat thread so there is no context carried over from earlier sessions.
# MAGIC
# MAGIC | # | Question to ask | What to look for |
# MAGIC |---|---|---|
# MAGIC | 1 | *What is our profit?* | Genie uses the `Profit` SQL expression: `SUM(net_revenue - cost)`. Result should differ from `SUM(net_revenue)`. |
# MAGIC | 2 | *Show me B2B sales* | Non-zero results. Check the SQL — it should filter `customers.segment = 'Corporate'` via the join. |
# MAGIC | 3 | *What’s our AOV trend by quarter?* | Consistent formula: `SUM(net_revenue) / COUNT(DISTINCT order_id)` grouped by quarter. |
# MAGIC | 4 | *Are we hitting our regional targets?* | Uses `sales_targets` in the join, returns actual vs target with a status column. |
# MAGIC | 5 | *Show me profit margin by category* | Response is labelled **Trusted**. SQL calls `fn_profit_margin(net_revenue, cost)`. Click **Show more** to confirm the function name. |
# MAGIC
# MAGIC **For each response:**
# MAGIC * Click **Show code** to confirm the generated SQL matches the fix you applied.
# MAGIC * If a result still looks wrong, review the SQL expression, join condition, or column synonym and adjust.
# MAGIC
# MAGIC > Genie is non-deterministic. If a question fails once but works on a retry, re-phrase the question closer to the example title you used in the example query. The phrasing of example query titles has a large effect on matching.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Summary
# MAGIC %md
# MAGIC ---
# MAGIC
# MAGIC ## Summary
# MAGIC
# MAGIC By the end of this notebook, the learner should have applied every tuning layer Genie provides and resolved all five original failures:
# MAGIC
# MAGIC | Tool applied | Failure fixed |
# MAGIC |---|---|
# MAGIC | SQL Expression (Measure: Profit, Profit Margin, AOV) | Questions 1 and 3 |
# MAGIC | SQL Expression (Filter: B2B Orders) + column synonym | Question 2 |
# MAGIC | Join relationship (sales_orders → sales_targets) + example query | Question 4 |
# MAGIC | SQL function (fn_profit_margin) as trusted asset | Question 5 |
# MAGIC
# MAGIC Beyond the five fixes, the learner should now understand:
# MAGIC
# MAGIC * **SQL expressions beat text instructions** for anything that can be expressed as a formula, filter, or field definition — Genie applies SQL exactly, while text instructions are interpreted.
# MAGIC * **Trusted assets** (parameterized queries and SQL functions) are the highest-confidence responses — the SQL runs verbatim and results are labelled Trusted.
# MAGIC * **Prompt matching** solves value-level mismatches (abbreviations, synonyms, spelling) that SQL expressions alone cannot fix.
# MAGIC * **Space-level tuning is scoped** — it only benefits this space. Use Unity Catalog column comments as a free baseline for all tools, and use metric views when measures need to be consistent across multiple spaces, dashboards, and teams.
# MAGIC * **Knowledge mining** can suggest join relationships and SQL expressions automatically when Genie learns from author interactions — this reduces manual curation over time.
# MAGIC
# MAGIC The next demo will cover benchmarks, knowledge mining, and sharing the space with other users.
