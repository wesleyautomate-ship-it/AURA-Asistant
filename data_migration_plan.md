# Data Migration Plan

This document outlines the plan to migrate the data from the old database tables to the new "enhanced" tables. This is a critical step in completing the migration to the new, clean architecture.

## 1. Table and Column Mapping

The following table maps the old tables and columns to the new tables and columns.

| Old Table | Old Column | New Table | New Column |
|---|---|---|---|
| `ai_requests` | `id` | `ai_requests_new` | `id` (UUID) |
| `ai_requests` | `agent_id` | `ai_requests_new` | `user_id` |
| `ai_requests` | `brokerage_id` | `ai_requests_new` | `brokerage_id` |
| `ai_requests` | `request_type` | `ai_requests_new` | `team` |
| `ai_requests` | `request_content` | `ai_requests_new` | `content` |
| `ai_requests` | `status` | `ai_requests_new` | `status` |
| `ai_requests` | `priority` | `ai_requests_new` | `priority` |
| `ai_requests` | `created_at` | `ai_requests_new` | `created_at` |
| `ai_requests` | `updated_at` | `ai_requests_new` | `updated_at` |
| `properties` | `id` | `enhanced_properties` | `id` |
| `properties` | `title` | `enhanced_properties` | `title` |
| `properties` | `description` | `enhanced_properties` | `description` |
| `properties` | `price` | `enhanced_properties` | `price_aed` |
| `clients` | `id` | `enhanced_clients` | `id` |
| `clients` | `name` | `enhanced_clients` | `name` |
| `clients` | `email` | `enhanced_clients` | `email` |
| `clients` | `phone` | `enhanced_clients` | `phone` |
| `transactions` | `id` | `transactions` | `id` |
| `transactions` | `property_id` | `transactions` | `property_id` |
| `transactions` | `buyer_id` | `transactions` | `buyer_id` |
| `transactions` | `seller_id` | `transactions` | `seller_id` |
| `transactions` | `agent_id` | `transactions` | `agent_id` |

## 2. Migration Order

The tables should be migrated in the following order to handle dependencies:

1.  `users` (No changes, but needed for foreign keys)
2.  `brokerages` (No changes, but needed for foreign keys)
3.  `enhanced_properties` (from `properties`)
4.  `enhanced_leads` (from `leads`)
5.  `enhanced_clients` (from `clients`)
6.  `transactions` (from `transactions`)
7.  `ai_requests_new` (from `ai_requests`)

## 3. Migration Scripts (Alembic)

Alembic should be used to create the migration scripts. The following steps should be followed:

1.  **Generate a new revision:**
    ```bash
    alembic revision -m "Migrate data from old tables to new tables"
    ```
2.  **Edit the revision file:**
    *   In the `upgrade()` function, write the SQL statements to migrate the data from the old tables to the new tables. Use `op.execute()` to run raw SQL.
    *   In the `downgrade()` function, write the SQL statements to revert the changes. This would involve deleting the data from the new tables.

**Example SQL for migrating `properties` to `enhanced_properties`:**

```sql
INSERT INTO enhanced_properties (id, title, description, price_aed, ...)
SELECT id, title, description, price, ...
FROM properties;
```

## 4. Execution

The migration should be executed in the following steps:

1.  **Backup the database:** Before starting the migration, create a full backup of the database.
2.  **Run the migration:**
    ```bash
    alembic upgrade head
    ```
3.  **Verify the data:** After the migration is complete, verify that the data has been migrated correctly.
4.  **Update the application:** Update the application to use the new tables.
5.  **Delete the old tables:** Once the application is stable, the old tables can be deleted.
