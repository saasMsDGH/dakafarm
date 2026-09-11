# FeedRecord Module

**Location:** `app/api/v1/farm/`

## Overview
The `FeedRecord` module tracks daily feed consumption for flocks. It serves as an operational module where farm workers log the quantity of feed given to birds.

## Schema & Attributes
- **id**: Internal DB primary key.
- **flock_id**: Foreign Key linking to `Flock.id`.
- **product_id**: An integer representing the feed product. *Note: Currently loose (no strict FK constraint) until the Business/Products module is built.*
- **record_date**: The date the feed was administered.
- **opening_quantity**: Starting amount of feed (Numeric).
- **quantity_used**: Amount given to the flock (Numeric).
- **closing_quantity**: Remaining feed amount (Numeric).
- **cost_per_unit**: Cost for one unit of the feed (Numeric).
- **total_cost**: Total cost of the feed used (Numeric).
- **recorded_by**: Foreign Key linking to `Users.id` (tracks who logged the feed).

*Timestamps strictly use the timezone-aware syntax:*
`created_at = Column(DateTime(timezone=True), server_default=func.now())`
`updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())`

## Business Logic (Service Layer)
- **Validation**: Ensures that the `flock_id` provided actually exists.
- **Auto-Calculation**: If `quantity_used` and `cost_per_unit` are provided (but `total_cost` is omitted), the system automatically calculates `total_cost = quantity_used * cost_per_unit`. This applies to both `POST` (create) and `PUT` (update) requests.

## API Endpoints & RBAC
Because feed logging is a daily operational task, **Farm Workers** are allowed to create records. However, only Managers and Admins can update or delete them (to correct mistakes).

| Method | Endpoint | Description | Role Required |
| --- | --- | --- | --- |
| `POST` | `/api/v1/farm/feed-records/` | Create a feed record | Admin, Farm Manager, Farm Worker |
| `GET`  | `/api/v1/farm/feed-records/` | List all records (paginated) | All Authenticated |
| `GET`  | `/api/v1/farm/feed-records/{id}` | Get a single record | All Authenticated |
| `PUT`  | `/api/v1/farm/feed-records/{id}` | Update record fields | Admin, Farm Manager |
| `DELETE`| `/api/v1/farm/feed-records/{id}` | Permanently delete record | Admin |

## Search and Pagination
The `GET /` list endpoint reuses the common `PaginationParams` class.
Search functionality is currently limited since fields are mostly numeric, but pagination and sorting by `record_date` are fully supported.
