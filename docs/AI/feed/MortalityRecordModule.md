# MortalityRecord Module

**Location:** `app/api/v1/farm/`

## Overview
The `MortalityRecord` module tracks bird deaths within specific flocks. Crucially, this module is directly integrated with the `Flock` module to create a fully automated bird tracking system.

## Schema & Attributes
- **id**: Internal DB primary key.
- **flock_id**: Foreign Key linking to `Flock.id`.
- **record_date**: The date the mortality occurred.
- **quantity**: The number of dead birds.
- **cause**: An optional string describing the cause (e.g., "Disease", "Predator").
- **recorded_by**: Foreign Key linking to `Users.id`.
- Standard timezone-aware timestamps.

## Full Automation (Service Layer)
- **Automatic Flock Deduction**: When a worker successfully logs a `MortalityRecord` (`POST`), the `MortalityRecordService` automatically subtracts the dead birds from the flock's `current_quantity`.
- **Safety Locks**: The service rejects any attempt to log more dead birds than are currently alive in the flock (`400 Bad Request`).
- **Correction Handling**: 
  - If a manager updates (`PUT`) a mortality record (e.g., changes the quantity from 10 to 5), the flock's `current_quantity` mathematically self-corrects.
  - If a manager deletes (`DELETE`) a mortality record, the birds are immediately restored to the flock's `current_quantity`.
- **Cross-Module Impact**: Because `ProductionRecord` automatically fetches `Flock.current_quantity`, logging a mortality instantly cascades and corrects the laying percentage for future daily egg logs without any manual intervention.

## API Endpoints & RBAC
**Farm Workers** log daily mortalities. Only Managers and Admins can update or delete them.

| Method | Endpoint | Description | Role Required |
| --- | --- | --- | --- |
| `POST` | `/api/v1/farm/mortality-records/` | Create a mortality record | Admin, Farm Manager, Farm Worker |
| `GET`  | `/api/v1/farm/mortality-records/` | List all records (paginated) | All Authenticated |
| `GET`  | `/api/v1/farm/mortality-records/{id}` | Get a single record | All Authenticated |
| `PUT`  | `/api/v1/farm/mortality-records/{id}` | Update record fields | Admin, Farm Manager |
| `DELETE`| `/api/v1/farm/mortality-records/{id}` | Permanently delete record | Admin |
