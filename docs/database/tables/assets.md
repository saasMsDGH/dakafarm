# Assets Tables

## `assets`
**Purpose**: Tracks fixed/moving farm assets (machinery, vehicles).

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |

## `asset_distributions`
**Purpose**: Tracks where an asset is assigned.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| asset_id | Integer | No | | FK | assets.id | |
