# Inventory (Stock Status) Module

## Overview
The Inventory module provides a real-time view of the current stock positions for all products. 

Rather than duplicating data into a separate 1-to-1 database table, this module smartly reads directly from the `Product` table (which tracks `current_stock` and `reorder_level`). It aggregates this data and automatically calculates a human-readable `status` string on the fly, preventing over-engineering and avoiding data synchronization bugs.

## Example Output Format
```json
{
  "product_id": 1,
  "product_name": "Layer Mash",
  "unit_of_measure": "bags",
  "quantity": 35.0,
  "reorder_level": 10.0,
  "status": "In Stock",
  "updated_at": "2026-09-11T12:00:00Z"
}
```

## API Endpoints

All endpoints are protected under the `manage_inventory` RoleChecker (Requires `admin` or `inventory_admin` roles).

- `GET /api/v1/inventory/stock/`
  - **Purpose**: Lists all stock positions.
  - **Filters**: 
    - `category_id`: Filter stock positions by a specific product category.
    - `status_filter`: Filter by calculated stock status (e.g., `?status_filter=Low Stock`).
- `GET /api/v1/inventory/stock/{product_id}`
  - **Purpose**: Retrieves the real-time stock position for a specific product.

## Status Calculation Logic
The `status` field is not stored in the database but is derived dynamically on every request based on the following rules:
- **Out of Stock**: `quantity <= 0`
- **Low Stock**: `quantity > 0` AND `quantity <= reorder_level`
- **In Stock**: `quantity > reorder_level`
