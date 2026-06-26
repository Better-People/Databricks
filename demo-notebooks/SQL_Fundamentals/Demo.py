# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Title and Introduction
# MAGIC %md
# MAGIC # DEMO: SQL Fundamentals in Databricks
# MAGIC
# MAGIC In this demo you will write SQL queries against a live dataset — no imports, no setup required. All queries run against Databricks' built-in sample data (`samples.tpch`).
# MAGIC
# MAGIC You will learn:
# MAGIC 1. **The anatomy of a SQL query** — SELECT, FROM, WHERE, ORDER BY, LIMIT
# MAGIC 2. **Aggregation** — collapsing many rows into summary figures with GROUP BY
# MAGIC 3. **Joins** — combining multiple tables using a shared key
# MAGIC 4. **NULLs** — why absent values behave differently to zero or empty strings
# MAGIC 5. **Data type gotchas** — integer division, string case sensitivity, dates
# MAGIC 6. **CTEs** — organising complex queries into readable, named steps
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 1 — Your First Query
# MAGIC %md
# MAGIC ## Step 1: Your First Query
# MAGIC
# MAGIC The fundamental SQL pattern is:
# MAGIC
# MAGIC ```sql
# MAGIC SELECT  <columns>
# MAGIC FROM    <table>
# MAGIC WHERE   <condition>
# MAGIC ORDER BY <column>
# MAGIC LIMIT   <n>
# MAGIC ```
# MAGIC
# MAGIC Run the cell below to list customers sorted by account balance.

# COMMAND ----------

# DBTITLE 1,SELECT basics
# MAGIC %sql
# MAGIC -- Retrieve 10 customers sorted by account balance (highest first)
# MAGIC -- AS renames columns in the output — it does not change the underlying data
# MAGIC SELECT
# MAGIC     c_custkey     AS customer_id,
# MAGIC     c_name        AS customer_name,
# MAGIC     c_mktsegment  AS market_segment,
# MAGIC     c_acctbal     AS account_balance
# MAGIC FROM samples.tpch.customer
# MAGIC ORDER BY c_acctbal DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# DBTITLE 1,Gotcha — LIMIT and string case sensitivity
# MAGIC %md
# MAGIC > **Gotcha 1 — LIMIT without ORDER BY is non-deterministic**
# MAGIC >
# MAGIC > `LIMIT 10` alone returns *any* 10 rows — the database picks whichever it finds fastest. You may get different rows each run. Always pair `LIMIT` with `ORDER BY`.
# MAGIC
# MAGIC > **Gotcha 2 — String comparisons are case-sensitive**
# MAGIC >
# MAGIC > `WHERE c_mktsegment = 'BUILDING'` works; `'building'` returns zero rows. Use `LOWER(c_mktsegment) = 'building'` when your data has inconsistent casing.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 2 — Aggregation
# MAGIC %md
# MAGIC ## Step 2: Aggregation — Summarising Data
# MAGIC
# MAGIC Aggregation collapses many rows into summary figures. The database evaluates SQL clauses in this fixed order — regardless of how you write them:
# MAGIC
# MAGIC ```
# MAGIC FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
# MAGIC ```
# MAGIC
# MAGIC Key aggregate functions: `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`.

# COMMAND ----------

# DBTITLE 1,GROUP BY aggregation
# MAGIC %sql
# MAGIC -- Count customers and total account balance per market segment
# MAGIC SELECT
# MAGIC     c_mktsegment    AS market_segment,
# MAGIC     COUNT(*)        AS customer_count,
# MAGIC     SUM(c_acctbal)  AS total_balance,
# MAGIC     AVG(c_acctbal)  AS avg_balance
# MAGIC FROM samples.tpch.customer
# MAGIC GROUP BY c_mktsegment
# MAGIC ORDER BY customer_count DESC;

# COMMAND ----------

# DBTITLE 1,HAVING vs WHERE explanation
# MAGIC %md
# MAGIC `GROUP BY c_mktsegment` collapses all rows with the same segment into one, and the aggregate functions compute across each group.
# MAGIC
# MAGIC To filter on the *aggregated* result (e.g. only segments above a threshold), use `HAVING` — not `WHERE`:
# MAGIC
# MAGIC | Clause | Runs | Can filter on... |
# MAGIC |---|---|---|
# MAGIC | `WHERE` | Before aggregation | Raw column values |
# MAGIC | `HAVING` | After aggregation | Aggregate results like `COUNT(*)` |

# COMMAND ----------

# DBTITLE 1,HAVING and the column alias gotcha
# MAGIC %sql
# MAGIC -- HAVING filters on the aggregated result
# MAGIC -- You CANNOT write "HAVING customer_count > 30000" — the alias does not exist yet
# MAGIC -- at the point HAVING is evaluated. Repeat the full expression.
# MAGIC SELECT
# MAGIC     c_mktsegment    AS market_segment,
# MAGIC     COUNT(*)        AS customer_count,
# MAGIC     SUM(c_acctbal)  AS total_balance
# MAGIC FROM samples.tpch.customer
# MAGIC GROUP BY c_mktsegment
# MAGIC HAVING COUNT(*) > 30000            -- NOT: HAVING customer_count > 30000
# MAGIC ORDER BY customer_count DESC;      -- ORDER BY *can* use the alias (runs last)

# COMMAND ----------

# DBTITLE 1,Gotcha — Column aliases in WHERE and HAVING
# MAGIC %md
# MAGIC > **Gotcha — Column aliases cannot be used in WHERE or HAVING**
# MAGIC >
# MAGIC > The alias `customer_count` does not exist when `HAVING` is evaluated. You must repeat `COUNT(*)`. The same applies to `WHERE`. The only exception is `ORDER BY`, which runs last and can reference aliases.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 3 — Joining Tables
# MAGIC %md
# MAGIC ## Step 3: Joining Tables
# MAGIC
# MAGIC Real data lives across multiple tables linked by shared keys. Databricks SQL supports all standard SQL joins plus two powerful filter-style joins most graphical tools don't expose.
# MAGIC
# MAGIC | Join type | Returns | Row count effect |
# MAGIC |---|---|---|
# MAGIC | `[INNER] JOIN` | Only rows matching in *both* tables | Can reduce rows |
# MAGIC | `LEFT [OUTER] JOIN` | All left rows + matched right (NULL if no match) | Preserves left row count |
# MAGIC | `RIGHT [OUTER] JOIN` | Matched left + all right rows (NULL if no match) | Preserves right row count |
# MAGIC | `FULL [OUTER] JOIN` | All rows from both tables (NULL where no match) | Can increase rows |
# MAGIC | `CROSS JOIN` | Every left row × every right row — no ON clause needed | Multiplies rows — use with care |
# MAGIC | `[LEFT] SEMI JOIN` | Left rows that *have* a match — no right columns returned | Never multiplies rows |
# MAGIC | `[LEFT] ANTI JOIN` | Left rows that *have no* match — the "NOT IN" equivalent | Never multiplies rows |
# MAGIC
# MAGIC In the sample data, `orders.o_custkey` links to `customer.c_custkey`.

# COMMAND ----------

# DBTITLE 1,INNER JOIN orders to customers
# MAGIC %sql
# MAGIC -- Join orders to customers to show each order alongside customer details
# MAGIC -- Table aliases (o, c) are required when two tables share a column name
# MAGIC SELECT
# MAGIC     o.o_orderkey      AS order_id,
# MAGIC     o.o_orderdate     AS order_date,
# MAGIC     o.o_totalprice    AS total_price,
# MAGIC     c.c_name          AS customer_name,
# MAGIC     c.c_mktsegment    AS market_segment
# MAGIC FROM   samples.tpch.orders   o
# MAGIC JOIN   samples.tpch.customer c ON o.o_custkey = c.c_custkey
# MAGIC WHERE  o.o_orderdate >= DATE '1995-01-01'
# MAGIC ORDER BY o.o_totalprice DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# DBTITLE 1,Join gotcha and LEFT JOIN intro
# MAGIC %md
# MAGIC `DATE '1995-01-01'` is a date literal — always use the `DATE` keyword rather than a plain string.
# MAGIC
# MAGIC > **Gotcha — Joins can multiply rows**
# MAGIC >
# MAGIC > If one customer has 100 orders, the INNER JOIN result contains 100 rows for that customer — one per order. This is correct. When you want one summary row per customer, add a `GROUP BY` after the join.
# MAGIC
# MAGIC Now use a LEFT JOIN to count customers per nation — including nations with *zero* customers:

# COMMAND ----------

# DBTITLE 1,LEFT JOIN with COUNT(*) vs COUNT(column)
# MAGIC %sql
# MAGIC -- LEFT JOIN keeps all nations, even those with no matching customers
# MAGIC -- COUNT(*) counts every row including NULLs
# MAGIC -- COUNT(column) silently skips NULLs — only counts rows with a real value
# MAGIC SELECT
# MAGIC     n.n_name            AS nation,
# MAGIC     COUNT(*)            AS total_rows,        -- includes NULL rows from the LEFT JOIN
# MAGIC     COUNT(c.c_custkey)  AS customer_count     -- NULLs skipped — nations with customers only
# MAGIC FROM   samples.tpch.nation   n
# MAGIC LEFT   JOIN samples.tpch.customer c ON n.n_nationkey = c.c_nationkey
# MAGIC GROUP BY n.n_name
# MAGIC ORDER BY customer_count DESC;

# COMMAND ----------

# DBTITLE 1,SEMI and ANTI JOIN intro
# MAGIC %md
# MAGIC SEMI and ANTI joins are **existence filters** — they never return columns from the right table and never multiply rows. These two are the most unique to SQL and the hardest to replicate in graphical tools.

# COMMAND ----------

# DBTITLE 1,LEFT SEMI JOIN — find rows with a match
# MAGIC %sql
# MAGIC -- LEFT SEMI JOIN: return customers who placed at least one order in 1997
# MAGIC -- Unlike INNER JOIN, right-side columns are NOT returned and rows are NEVER multiplied
# MAGIC -- A customer with 100 orders in 1997 still appears exactly once
# MAGIC SELECT
# MAGIC     c_custkey     AS customer_id,
# MAGIC     c_name        AS customer_name,
# MAGIC     c_mktsegment  AS market_segment
# MAGIC FROM   samples.tpch.customer c
# MAGIC LEFT SEMI JOIN samples.tpch.orders o
# MAGIC     ON  o.o_custkey       = c.c_custkey
# MAGIC     AND YEAR(o.o_orderdate) = 1997
# MAGIC LIMIT 10;

# COMMAND ----------

# DBTITLE 1,LEFT ANTI JOIN — find rows with no match
# MAGIC %sql
# MAGIC -- LEFT ANTI JOIN: return customers who placed NO orders in 1997
# MAGIC -- The SQL equivalent of "find unmatched records" — hard to express in most graphical tools
# MAGIC SELECT
# MAGIC     c_custkey  AS customer_id,
# MAGIC     c_name     AS customer_name
# MAGIC FROM   samples.tpch.customer c
# MAGIC LEFT ANTI JOIN samples.tpch.orders o
# MAGIC     ON  o.o_custkey       = c.c_custkey
# MAGIC     AND YEAR(o.o_orderdate) = 1997
# MAGIC LIMIT 10;

# COMMAND ----------

# DBTITLE 1,Gotcha — SEMI vs INNER JOIN row multiplication
# MAGIC %md
# MAGIC > **SEMI vs INNER JOIN — the row multiplication difference**
# MAGIC >
# MAGIC > `INNER JOIN` returns one row *per match* — a customer with 100 orders produces 100 rows. `LEFT SEMI JOIN` returns that customer *exactly once*, regardless of how many orders exist. Use SEMI when you only need to test *whether* a match exists, not retrieve any data from the right table.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 4 — NULLs
# MAGIC %md
# MAGIC Notice `total_rows` and `customer_count` differ for nations with no customers — those rows got `NULL` in the joined column, and `COUNT(c.c_custkey)` silently excluded them.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Step 4: NULLs — The Silent Troublemaker
# MAGIC
# MAGIC `NULL` means *unknown* or *absent*. It is not zero, not an empty string, and not `false`. Three rules that trip everyone up:

# COMMAND ----------

# DBTITLE 1,NULL comparison and COALESCE
# MAGIC %sql
# MAGIC -- Rule 1: NULL does not equal NULL — use IS NULL, not = NULL
# MAGIC -- Rule 2: NULL propagates through expressions — NULL + 1 = NULL, NULL || 'x' = NULL
# MAGIC -- Rule 3: COALESCE returns the first non-NULL argument — use it as a safe fallback
# MAGIC SELECT
# MAGIC     (NULL = NULL)            AS null_eq_null,       -- returns NULL, not TRUE
# MAGIC     (NULL IS NULL)           AS null_is_null,        -- returns TRUE — the correct check
# MAGIC     (NULL != 'hello')        AS null_neq_string,     -- returns NULL, not TRUE
# MAGIC     COALESCE(NULL, 0)        AS coalesce_fallback,   -- returns 0
# MAGIC     COALESCE(NULL, NULL, 42) AS coalesce_chain;      -- returns first non-NULL

# COMMAND ----------

# DBTITLE 1,Gotcha — NULL filtering with !=
# MAGIC %md
# MAGIC > **Gotcha — `WHERE column != 'value'` silently drops NULLs**
# MAGIC >
# MAGIC > `WHERE o_orderstatus != 'F'` also removes rows where `o_orderstatus` is `NULL` — because `NULL != 'F'` evaluates to `NULL`, which is treated as `FALSE`. To keep NULLs, write:
# MAGIC > `WHERE o_orderstatus != 'F' OR o_orderstatus IS NULL`
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 5 — Data Type Gotchas
# MAGIC %md
# MAGIC ## Step 5: Data Type Gotchas
# MAGIC
# MAGIC Databricks SQL enforces types strictly. Two areas cause silent, hard-to-spot errors.

# COMMAND ----------

# DBTITLE 1,Integer division gotcha
# MAGIC %sql
# MAGIC -- Gotcha: Integer ÷ Integer = Integer (the decimal part is truncated, not rounded)
# MAGIC -- COUNT(*) returns BIGINT, so dividing two COUNTs does integer division
# MAGIC SELECT
# MAGIC     COUNT(*)                                              AS total_orders,
# MAGIC     COUNT(DISTINCT o_custkey)                             AS unique_customers,
# MAGIC     COUNT(*) / COUNT(DISTINCT o_custkey)                  AS avg_orders_wrong,    -- truncated!
# MAGIC     COUNT(*) / CAST(COUNT(DISTINCT o_custkey) AS DOUBLE)  AS avg_orders_correct   -- correct
# MAGIC FROM samples.tpch.orders;

# COMMAND ----------

# DBTITLE 1,Date functions
# MAGIC %sql
# MAGIC -- Date arithmetic and formatting
# MAGIC -- Always use DATE '...' literals — plain strings can silently misbehave on date columns
# MAGIC SELECT
# MAGIC     o_orderdate                               AS order_date,
# MAGIC     YEAR(o_orderdate)                         AS order_year,
# MAGIC     DATE_FORMAT(o_orderdate, 'yyyy-MM')       AS order_month,
# MAGIC     DATEDIFF(DATE '1998-12-31', o_orderdate)  AS days_to_year_end,
# MAGIC     DATE_ADD(o_orderdate, 30)                 AS thirty_days_later
# MAGIC FROM samples.tpch.orders
# MAGIC WHERE o_orderdate >= DATE '1998-01-01'
# MAGIC LIMIT 5;

# COMMAND ----------

# DBTITLE 1,Gotcha — Dates stored as strings
# MAGIC %md
# MAGIC > **Gotcha — Dates stored as strings sort alphabetically, not chronologically**
# MAGIC >
# MAGIC > If a date column is a `STRING` (e.g. `'20230115'` or `'15/01/2023'`), a `>` comparison sorts character-by-character — which gives completely wrong results. Cast to a proper date first: `TO_DATE(column, 'yyyyMMdd')`.
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Step 6 — CTEs
# MAGIC %md
# MAGIC ## Step 6: CTEs — Organising Complex Queries
# MAGIC
# MAGIC A **Common Table Expression** (CTE) names an intermediate result so you can reference it later in the same query. This breaks a complex query into labelled, readable steps — instead of nesting subqueries inside subqueries.
# MAGIC
# MAGIC ```sql
# MAGIC WITH step_one AS (
# MAGIC     -- first query
# MAGIC ),
# MAGIC step_two AS (
# MAGIC     -- can reference step_one here
# MAGIC )
# MAGIC SELECT * FROM step_two;
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,CTE with window function
# MAGIC %sql
# MAGIC -- Find the top 3 market segments by total order revenue in 1997
# MAGIC -- Each WITH block is a named, reusable step
# MAGIC WITH order_with_segment AS (
# MAGIC     -- Step 1: bring the customer's market segment onto each order row
# MAGIC     SELECT
# MAGIC         o.o_totalprice,
# MAGIC         c.c_mktsegment AS market_segment
# MAGIC     FROM   samples.tpch.orders   o
# MAGIC     JOIN   samples.tpch.customer c ON o.o_custkey = c.c_custkey
# MAGIC     WHERE  YEAR(o.o_orderdate) = 1997
# MAGIC ),
# MAGIC segment_totals AS (
# MAGIC     -- Step 2: aggregate to one row per segment
# MAGIC     SELECT
# MAGIC         market_segment,
# MAGIC         COUNT(*)                    AS order_count,
# MAGIC         ROUND(SUM(o_totalprice), 2) AS total_revenue
# MAGIC     FROM   order_with_segment
# MAGIC     GROUP BY market_segment
# MAGIC )
# MAGIC -- Step 3: add a rank and return the top 3
# MAGIC SELECT
# MAGIC     market_segment,
# MAGIC     order_count,
# MAGIC     total_revenue,
# MAGIC     RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
# MAGIC FROM   segment_totals
# MAGIC ORDER BY revenue_rank
# MAGIC LIMIT 3;

# COMMAND ----------

# DBTITLE 1,Summary
# MAGIC %md
# MAGIC `RANK() OVER (ORDER BY ...)` is a **window function** — it adds a computed value to each row without collapsing rows the way `GROUP BY` does. Window functions are the go-to tool for running totals, rankings, and row-over-row comparisons.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Summary
# MAGIC
# MAGIC | Concept | What to remember |
# MAGIC |---|---|
# MAGIC | **LIMIT** | Always pair with `ORDER BY` for a meaningful result |
# MAGIC | **String case** | Comparisons are case-sensitive — use `LOWER()` or `UPPER()` for safety |
# MAGIC | **Clause order** | `WHERE` runs before grouping; `HAVING` runs after |
# MAGIC | **Column aliases** | Not available in `WHERE` or `HAVING`; safe in `ORDER BY` |
# MAGIC | **Joins** | `INNER JOIN` returns only matches; `LEFT JOIN` keeps all left-side rows |
# MAGIC | **NULLs** | Use `IS NULL` / `IS NOT NULL`; `= NULL` never evaluates to true |
# MAGIC | **NULL in aggregates** | `COUNT(*)` includes NULLs; `COUNT(column)` silently skips them |
# MAGIC | **Integer division** | `COUNT(*) / COUNT(x)` truncates — cast one side to `DOUBLE` |
# MAGIC | **Date literals** | Use `DATE '...'` not plain strings; cast string dates with `TO_DATE()` |
# MAGIC | **CTEs** | Break complex logic into named, readable steps with `WITH` |

# COMMAND ----------


