# Authentication Tables

## `users`
**Purpose**: Stores user authentication credentials, names, and status.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| first_name | String | No | | | | |
| last_name | String | No | | | | |
| email | String | No | | Unique | | |
| phone | String | Yes | | | | |
| password_hash | String | Yes | | | | |
| is_active | Boolean | Yes | True | | | |
| created_at | DateTime | Yes | func.now() | | | |
| updated_at | DateTime | Yes | func.now() | | | |

## `roles`
**Purpose**: Defines system roles.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| name | String | Yes | | | | |

## `userrole`
**Purpose**: Junction table linking users to roles.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| user_id | Integer | Yes | | FK | users.id (CASCADE) | |
| role_id | Integer | Yes | | FK | roles.id (CASCADE) | |
