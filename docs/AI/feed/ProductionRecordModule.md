# ProductionRecord Module

**Location:** `app/api/v1/farm/`

## Overview
The `ProductionRecord` module tracks daily egg production for specific flocks. This module is fully automated to minimize manual user input and prevent mathematical errors during data entry.

## Schema & Attributes
- **id**: Internal DB primary key.
- **flock_id**: Foreign Key linking to `Flock.id`.
- **record_date**: The date the eggs were collected.
- **total_birds**: The number of active birds in the flock on this day.
- **total_eggs**: Total eggs collected.
- **damaged_eggs**: Number of broken or unusable eggs.
- **good_eggs**: Number of sellable eggs **(Auto-calculated)**.
- **laying_percentage**: The percentage of birds that laid an egg **(Auto-calculated)**.
- **recorded_by**: Foreign Key linking to `Users.id` (tracks who logged the production).

*Timestamps strictly use the timezone-aware syntax:*
`created_at = Column(DateTime(timezone=True), server_default=func.now())`
`updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())`

## Full Automation (Service Layer)
- **Calculations**: To prevent discrepancies, `good_eggs` and `laying_percentage` have been completely removed from the request schema (meaning the frontend does not send them).
- The `ProductionRecordService` computes them automatically:
  - `good_eggs = max(0, total_eggs - damaged_eggs)`
  - `laying_percentage = (total_eggs / total_birds) * 100` (Includes safety checks to prevent division by zero).
- **Validation**: The service also throws a `400 Bad Request` if a user accidentally logs more `damaged_eggs` than `total_eggs`.

## API Endpoints & RBAC
Because logging daily production is a routine farm task, **Farm Workers** are allowed to create records. However, only Managers and Admins can update or delete them to correct mistakes.

| Method | Endpoint | Description | Role Required |
| --- | --- | --- | --- |
| `POST` | `/api/v1/farm/production-records/` | Create a production record | Admin, Farm Manager, Farm Worker |
| `GET`  | `/api/v1/farm/production-records/` | List all records (paginated) | All Authenticated |
| `GET`  | `/api/v1/farm/production-records/{id}` | Get a single record | All Authenticated |
| `PUT`  | `/api/v1/farm/production-records/{id}` | Update record fields | Admin, Farm Manager |
| `DELETE`| `/api/v1/farm/production-records/{id}` | Permanently delete record | Admin |

## Search and Pagination
The `GET /` list endpoint reuses the common `PaginationParams` class.
Search functionality defaults to ordering by `record_date`.
