---
name: sql-optimization
description: 'Analyze and optimize SQL queries for better performance. Covers indexing strategies, query rewriting, execution plan analysis, and database-specific optimization techniques.'
---

# SQL Query Optimization

## Goal

Analyze the provided SQL queries and database schema to identify performance bottlenecks and provide optimized alternatives with explanations.

## Process

### 1. Analyze the Current Query

Before optimizing, understand:
- What data is being retrieved and how it will be used
- The approximate size of tables involved
- Existing indexes on the tables
- The database engine in use (MySQL, PostgreSQL, SQLite, SQL Server, Oracle)

### 2. Identify Performance Issues

Common problems to check:

**Query Structure**
- `SELECT *` — retrieves unnecessary columns
- Missing `LIMIT` on large result sets
- Correlated subqueries that execute once per row
- Functions applied to indexed columns in `WHERE` clauses (prevents index use)
- `OR` conditions that prevent index usage

**Join Issues**
- Missing indexes on join columns
- Cartesian products (missing JOIN condition)
- Joining on columns with incompatible types (implicit casting)

**Aggregation**
- `HAVING` used instead of `WHERE` for pre-aggregation filtering
- Aggregating more rows than needed

**N+1 Patterns**
- Queries inside loops — replace with a single JOIN or IN clause

### 3. Optimization Techniques

**Indexing**
```sql
-- Single column index
CREATE INDEX idx_table_column ON table(column);

-- Composite index (order matters: put equality filters first, range last)
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Covering index (includes all columns needed by the query)
CREATE INDEX idx_covering ON orders(user_id, created_at, status);
```

**Query Rewriting**
```sql
-- Instead of SELECT *
SELECT id, name, email FROM users WHERE active = 1;

-- Instead of correlated subquery
-- SLOW:
SELECT * FROM orders o WHERE amount > (SELECT AVG(amount) FROM orders WHERE user_id = o.user_id);
-- FAST:
SELECT o.* FROM orders o
JOIN (SELECT user_id, AVG(amount) AS avg_amount FROM orders GROUP BY user_id) avg_o
  ON o.user_id = avg_o.user_id AND o.amount > avg_o.avg_amount;

-- Keyset pagination instead of OFFSET
-- SLOW for large offsets:
SELECT * FROM posts ORDER BY id LIMIT 20 OFFSET 10000;
-- FAST:
SELECT * FROM posts WHERE id > :last_seen_id ORDER BY id LIMIT 20;
```

**EXISTS vs COUNT**
```sql
-- Use EXISTS to check for row presence (stops at first match)
SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders WHERE user_id = u.id);
```

### 4. Use EXPLAIN / EXPLAIN ANALYZE

```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT ...;

-- MySQL
EXPLAIN SELECT ...;

-- SQLite
EXPLAIN QUERY PLAN SELECT ...;
```

Look for:
- **Seq Scan** (PostgreSQL) / **ALL** (MySQL) on large tables → missing index
- **Nested Loop** on large sets → consider HASH JOIN
- High **rows** estimates → check statistics with `ANALYZE`

### 5. Batch Operations

```sql
-- Insert in batches, not one row at a time
INSERT INTO table (col1, col2) VALUES
  (val1a, val1b),
  (val2a, val2b),
  (val3a, val3b);

-- Update in batches
UPDATE orders SET status = 'archived'
WHERE created_at < '2023-01-01'
LIMIT 1000;  -- repeat until 0 rows affected
```

## Output Format

For each optimization, provide:

1. **Issue identified** — what is slow and why
2. **Optimized query** — the rewritten SQL
3. **Explanation** — why this is faster
4. **Index recommendation** — if a new index is needed
5. **Expected improvement** — qualitative or quantitative estimate
