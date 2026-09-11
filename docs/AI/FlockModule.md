# Flock Module

**Location:** `app/api/v1/farm/`

## Overview
The `Flock` module is the core entity linking everything together on the farm. A Flock represents a batch of birds living in a specific `House`. Other modules (Feed, Medication, Production) will reference the `flock_id`.

## Schema & Attributes
- **id**: Internal DB primary key.
- **flock_code**: A unique string identifying the flock. **(Auto-generated)**
- **house_id**: Links to `House.id`.
- **breed**: Breed of the birds.
- **initial_quantity**: Number of birds on arrival.
- **arrival_date**: When the flock arrived at the farm.
- **status**: A free-form string managed by the user (e.g., "Active", "Completed").

## Flock Code Generation Strategy
To simplify operations for the farm staff, the backend **automatically generates the `flock_code`**. 
The generation rule uses the House name and Arrival Date:
`[HouseName(Sanitized)]-[YYYYMMDD]`

*Example:* If a flock arrives in "North Block" on September 9th, 2026, the code generated is `NORTHBLOCK-20260909`.
If a collision occurs (two flocks arriving at the same house on the same day), the system appends a sequential number: `NORTHBLOCK-20260909-1`.

This code logic is handled exclusively in `FlockService._generate_flock_code()`.

## API Endpoints
All endpoints enforce Role-Based Access Control (RBAC):

| Method | Endpoint | Description | Role Required |
| --- | --- | --- | --- |
| `POST` | `/api/v1/farm/flocks/` | Create a new flock | Admin, Farm Manager |
| `GET`  | `/api/v1/farm/flocks/` | List flocks (paginated, searchable) | All Authenticated |
| `GET`  | `/api/v1/farm/flocks/{id}` | Get a single flock | All Authenticated |
| `PUT`  | `/api/v1/farm/flocks/{id}` | Update flock fields | Admin, Farm Manager |
| `DELETE`| `/api/v1/farm/flocks/{id}` | Permanently delete flock | Admin |

## Search and Pagination
The `GET /` list endpoint reuses the common `PaginationParams` class.
Users can search flocks by passing the `?search=` parameter, which will look for matches in:
- `flock_code`
- `breed`
- `status`

## Developer Notes
- Ensure a valid `house_id` is supplied during creation/update, or a `404 Not Found` will be returned.
- If deleting a house, the relationship `cascade="all, delete-orphan"` will automatically wipe out associated flocks. Ensure UI warnings are in place before deleting a house.
