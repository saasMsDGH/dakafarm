# Inventory Products Module

## Overview
The Products module is part of the Inventory subsystem and handles all inventory items (products) across the farm (e.g., Medicine, Feed, Equipment). It tracks standard catalog data alongside stock management settings like `current_stock` and `reorder_level`. 

## Data Model (`Product`)
- `id` (int, primary key)
- `category_id` (int, foreign key -> `product_categories.id`)
- `name` (string 100, unique)
- `unit_of_measure` (string 50, e.g., 'kg', 'vials', 'bags')
- `current_stock` (numeric, default 0) - *Managed automatically by future stock transactions*
- `reorder_level` (numeric, default 0) - *Threshold for low-stock alerts*
- `description` (string 255, optional)
- `is_active` (boolean, default True)
- `created_by` (int, foreign key -> `users.id`)
- `created_at` (datetime)
- `updated_at` (datetime)

## API Endpoints

All endpoints are protected under the `manage_inventory` RoleChecker (Requires `admin` or `inventory_admin` roles).

- `POST /api/v1/inventory/products/`
  - **Purpose**: Creates a new product. 
  - **Validation**: Verifies that the provided `category_id` exists before creation.
- `GET /api/v1/inventory/products/`
  - **Purpose**: Lists products with pagination support.
  - **Filters**: Can filter by `category_id` and `search` (checks name/description).
- `GET /api/v1/inventory/products/{product_id}`
  - **Purpose**: Retrieves a single product by its ID.
- `PUT /api/v1/inventory/products/{product_id}`
  - **Purpose**: Updates an existing product. 
  - **Validation**: Checks if a new `category_id` exists before updating.
- `DELETE /api/v1/inventory/products/{product_id}`
  - **Purpose**: Deletes a product.
  - **Note**: This will fail with a 400 Bad Request if the product is actively referenced by foreign keys (e.g., existing stock transactions) using SQLAlchemy's `IntegrityError`.
