# MedicationRecord Module

**Location:** `app/api/v1/farm/`

## Overview
The `MedicationRecord` module is responsible for tracking health interventions for specific flocks. This includes logging the suspected disease, the medication administered, the cost of the treatment, and any required withdrawal period before the farm's products (eggs/meat) are safe for human consumption.

## Schema & Attributes
- **id**: Internal DB primary key.
- **flock_id**: Foreign Key linking to `Flock.id`.
- **product_id**: A loose integer reference for the medication product used. This is kept loose (no strict FK constraint) until the Business module is fully built.
- **record_date**: The date the medication was administered.
- **disease_suspected**: An optional string describing the suspected illness.
- **quantity_used**: The amount of medication administered.
- **cost_per_unit**: The cost of a single unit of the medication.
- **total_cost**: The total calculated cost of the treatment (`quantity_used * cost_per_unit`).
- **withdrawal_period_days**: The number of days after treatment during which products from this flock cannot be sold.
- **recorded_by**: Foreign Key linking to `Users.id`.

## Automation Details
- **Total Cost Auto-Calculation**: Like `FeedRecord`, `total_cost` is entirely removed from the input schemas (`MedicationRecordCreate` and `MedicationRecordUpdate`). When a user inputs `quantity_used` and `cost_per_unit`, the backend automatically calculates and stores `total_cost`.
  - When an update (`PUT`) changes either the quantity or the unit cost, the `total_cost` is instantly recalculated.

## API Endpoints & RBAC
**Farm Workers** can log daily medications. However, they are restricted from altering past medical records to prevent data tampering.

| Method | Endpoint | Description | Role Required |
| --- | --- | --- | --- |
| `POST` | `/api/v1/farm/medication-records/` | Create a medication record | Admin, Farm Manager, Farm Worker |
| `GET`  | `/api/v1/farm/medication-records/` | List all records (paginated) | All Authenticated |
| `GET`  | `/api/v1/farm/medication-records/{id}` | Get a single record | All Authenticated |
| `PUT`  | `/api/v1/farm/medication-records/{id}` | Update record fields | Admin, Farm Manager |
| `DELETE`| `/api/v1/farm/medication-records/{id}` | Permanently delete record | Admin |
