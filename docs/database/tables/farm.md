# Farm Operations Tables

## `houses`
**Purpose**: Physical poultry houses/structures on the farm.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| name | String | No | | Unique | | |
| capacity | Integer | No | | | | |
| status | Boolean | Yes | True | | | |
| created_by | Integer | Yes | | FK | users.id | |

## `flocks`
**Purpose**: Batches of birds. Linked to a house.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| name | String | No | | Unique | | |
| house_id | Integer | No | | FK | houses.id | |
| start_date | Date | No | | | | |
| initial_quantity | Integer | No | | | | |
| current_quantity | Integer | No | | | | |

## `medication_records`
**Purpose**: Logs treatments and medications given to a flock.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| flock_id | Integer | No | | FK | flocks.id | |
| product_id | Integer | No | | FK | products.id | |
| record_date | Date | No | | | | |
| total_cost | Numeric | No | | | | |

## `vaccination_records`
**Purpose**: Logs vaccination schedules and completions for a flock.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| flock_id | Integer | No | | FK | flocks.id | |
| product_id | Integer | No | | FK | products.id | |
| record_date | Date | No | | | | |
| total_cost | Numeric | No | | | | |

## `production_records`
**Purpose**: Tracks daily egg production.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| flock_id | Integer | No | | FK | flocks.id | |
| total_eggs | Integer | No | | | | |
| good_eggs | Integer | No | | | | |

## `mortality_records`
**Purpose**: Tracks bird deaths.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| flock_id | Integer | No | | FK | flocks.id | |
| quantity | Integer | No | | | | |

## `feed_records`
**Purpose**: Logs daily feed consumption.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| flock_id | Integer | No | | FK | flocks.id | |
| product_id | Integer | No | | FK | products.id | |
