# Authentication ERD

```mermaid
erDiagram
    USERS ||--o{ USERROLE : has
    ROLES ||--o{ USERROLE : assigned_to
```
