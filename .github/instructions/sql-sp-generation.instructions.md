---
description: 'Guidelines for generating SQL statements and stored procedures'
applyTo: '**/*.sql'
---
# SQL Development

## Database schema generation
- all table names should be in singular form
- all column names should be in singular form
- all tables should have a primary key column named `id`
- all tables should have a column named `created_at` and `updated_at`

## SQL Coding Style
- use uppercase for SQL keywords (SELECT, FROM, WHERE, etc.)
- use consistent indentation for nested queries
- break long queries into multiple lines for readability
- organize clauses in a consistent order: SELECT, FROM, JOIN, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT

## SQL Query Structure
- use explicit column names instead of SELECT *
- qualify column names with table name or alias when joining multiple tables
- include LIMIT clauses to restrict result sets where appropriate
- avoid using functions on indexed columns in WHERE clauses (prevents index use)

## SQL Security Best Practices
- parameterize all queries to prevent SQL injection attacks
- use prepared statements for any dynamic SQL
- avoid embedding credentials, connection strings, or secrets in SQL scripts
- implement proper error handling that doesn't expose system details or schema information
- avoid dynamic SQL construction within stored procedures when possible

## Transaction Management
- explicitly begin and commit/rollback transactions
- use appropriate isolation levels for the use case (READ COMMITTED as default)
- avoid long-running transactions that lock tables unnecessarily
- use batch processing for large data operations (INSERT/UPDATE/DELETE)

## Stored Procedure Guidelines
- stored procedures should have a single, well-defined responsibility
- use input parameter validation at the start of each stored procedure
- use output parameters or return values to communicate results
- document parameters, return values, and behavior with comments
- prefix stored procedure names consistently (e.g., `usp_` or `sp_`)

## Indexing
- create indexes on columns frequently used in WHERE clauses
- create indexes on foreign key columns
- use composite indexes for queries filtering on multiple columns
- avoid over-indexing (slows writes, increases storage)
- consider covering indexes for high-frequency queries

## Performance
- avoid SELECT * in production queries
- use EXISTS instead of COUNT when checking for row existence
- prefer JOINs over subqueries where equivalent
- use EXPLAIN / EXPLAIN ANALYZE to verify query plans
- avoid OFFSET for large paginated queries; prefer keyset pagination
