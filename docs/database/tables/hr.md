# Human Resources Tables

## `employees`
**Purpose**: Staff profiles and salary details.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |

## `payrolls`
**Purpose**: Generated wage records.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| employee_id | Integer | No | | FK | employees.id | |
