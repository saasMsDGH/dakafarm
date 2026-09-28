# Stock Movements Module

## Overview
The Stock Movements module is the final and most critical piece of the Inventory subsystem. It manages the flow of products in and out of the farm. 

This module enforces **immutability**. To guarantee a flawless audit trail, users cannot manually update a product's stock, nor can they edit or delete an existing stock movement. All stock changes must be explicitly logged as new movements.

## Movement Types & Math
There are three types of movements, and each handles math automatically behind the scenes:

1. **`IN`**: Used when new stock arrives (e.g., purchases).
   - *Requirement*: `quantity` must be greater than 0.
   - *Result*: Automatically adds the quantity to the product's `current_stock`.

2. **`OUT`**: Used when stock is consumed or sold (e.g., fed to a flock).
   - *Requirement*: `quantity` must be greater than 0.
   - *Validation*: If the requested quantity is greater than the product's available `current_stock`, the API returns a `400 Bad Request`.
   - *Result*: Automatically subtracts the quantity from the product's `current_stock`.

3. **`ADJUSTMENT`**: Used to correct discrepancies (e.g., damaged stock, miscounts).
   - *Requirement*: `quantity` can be positive (found extra stock) or negative (lost/damaged stock).
   - *Result*: Adds the quantity directly to the product's `current_stock`.

## Polymorphic Associations (Soft Foreign Keys)
Since stock can move for many reasons across many different tables, we use `reference_type` and `reference_id` to link the movement to its source.
- **`reference_type`**: A string indicating the source module (e.g., "FeedRecord", "Purchase", "Sale").
- **`reference_id`**: The integer ID of that record in its respective table.

These fields are optional (`nullable`), allowing you to make simple manual adjustments without needing a parent record.

## API Endpoints
All endpoints require `manage_inventory` permissions (Roles: `admin` or `inventory_admin`).
- `POST /api/v1/inventory/movements/`: Record a new movement.
- `GET /api/v1/inventory/movements/`: List movements. Supports filtering by `product_id` and `movement_type`.
- `GET /api/v1/inventory/movements/{id}`: Get details of a single movement.
