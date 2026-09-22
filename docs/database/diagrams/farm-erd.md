# Farm ERD

```mermaid
erDiagram
    HOUSES ||--o{ FLOCKS : houses
    FLOCKS ||--o{ FEED_RECORDS : consumes
    FLOCKS ||--o{ MEDICATION_RECORDS : receives
    FLOCKS ||--o{ VACCINATION_RECORDS : receives
    FLOCKS ||--o{ MORTALITY_RECORDS : tracks
    FLOCKS ||--o{ PRODUCTION_RECORDS : produces
```
