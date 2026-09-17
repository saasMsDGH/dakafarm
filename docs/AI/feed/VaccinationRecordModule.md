# VaccinationRecord Module

**Location:** `app/api/v1/farm/`

## Overview
The `VaccinationRecord` module tracks preventative healthcare measures for flocks. This module logs the vaccines administered to the flock, the targeted disease, the method of administration (e.g., water, spray, injection), and crucially, the date when the next booster or dose is due.

## Schema & Attributes
- **id**: Internal DB primary key.
- **flock_id**: Foreign Key linking to `Flock.id`.
- **product_id**: A loose integer reference for the vaccine product used. Kept loose pending the Business/Inventory module.
- **record_date**: The date the vaccination was administered.
- **disease_targeted**: An optional string describing the target disease (e.g., "Gumboro", "Newcastle").
- **administration_method**: An optional string for the method (e.g., "Water", "Spray", "Eye-drop", "Injection").
- **quantity_used**: The amount of vaccine administered.
- **cost_per_unit**: The cost of a single unit of the vaccine.
- **total_cost**: The total calculated cost of the vaccine (`quantity_used * cost_per_unit`).
- **next_due_date**: The date when the next dose or booster is required.
- **recorded_by**: Foreign Key linking to `Users.id`.

## Automation Details
- **Total Cost Auto-Calculation**: Like the `MedicationRecord` and `FeedRecord`, the `total_cost` field is entirely removed from the user input schema. When a user inputs `quantity_used` and `cost_per_unit`, the backend automatically calculates and stores `total_cost`.
  - When an update (`PUT`) alters the quantity or the unit cost, the `total_cost` mathematically self-corrects.

## API Endpoints & RBAC
**Farm Workers** can log new vaccinations. However, they are restricted from altering past vaccination records to prevent data tampering.

| Method | Endpoint | Description | Role Required |
| --- | --- | --- | --- |
| `POST` | `/api/v1/farm/vaccination-records/` | Create a vaccination record | Admin, Farm Manager, Farm Worker |
| `GET`  | `/api/v1/farm/vaccination-records/` | List all records (paginated) | All Authenticated |
| `GET`  | `/api/v1/farm/vaccination-records/{id}` | Get a single record | All Authenticated |
| `PUT`  | `/api/v1/farm/vaccination-records/{id}` | Update record fields | Admin, Farm Manager |
| `DELETE`| `/api/v1/farm/vaccination-records/{id}` | Permanently delete record | Admin |
