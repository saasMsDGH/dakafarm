over all project stucture
```
app/
│
├── main.py
│
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── exceptions.py
│
├── api/
│   ├── router.py
│   │
│   └── v1/
│       ├── router.py
│       │
│       ├── auth/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       ├── users/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       ├── farm/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       ├── sales/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       ├── purchases/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       ├── inventory/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       ├── finance/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       ├── hr/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       ├── assets/
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── router.py
│       │
│       └── reports/
│           ├── schemas.py
│           ├── service.py
│           ├── repository.py
│           └── router.py
│
├── shared/
│   ├── enums.py
│   ├── pagination.py
│   ├── responses.py
│   └── dependencies.py
│
└── tests/
    ├── auth/
    ├── farm/
    ├── sales/
    ├── purchases/
    ├── inventory/
    ├── finance/
    ├── hr/
    ├── assets/
    └── reports/
```
What each file does

For every module:
```
farm/
├── models.py        → Database tables
├── schemas.py       → Pydantic request/response schemas
├── service.py       → Business logic
├── repository.py    → Database queries
└── router.py        → API endpoints
```
For example, Farm:
```
farm/
│
├── models.py
│   ├── House
│   ├── Flock
│   ├── ProductionRecord
│   ├── FeedRecord
│   ├── MedicationRecord
│   ├── VaccinationRecord
│   └── MortalityRecord
│
├── schemas.py
│   ├── HouseCreate
│   ├── HouseResponse
│   ├── FlockCreate
│   ├── ProductionCreate
│   └── ...
│
├── service.py
│   ├── create_flock()
│   ├── record_production()
│   ├── record_mortality()
│   ├── record_feed_usage()
│   └── ...
│
├── repository.py
│   ├── create()
│   ├── get_by_id()
│   ├── get_all()
│   ├── update()
│   └── delete()
│
└── router.py
    ├── POST /flocks
    ├── GET /flocks
    ├── POST /production
    ├── POST /mortality
    └── ...
```
The request flow stays consistent:
```
Frontend
   ↓
router.py
   ↓
schemas.py
   ↓
service.py
   ↓
repository.py
   ↓
models.py
   ↓
PostgreSQL
```

And when a business operation affects another subsystem:
```
Sales
  │
  └── service.py
        │
        ├── Inventory Service
        ├── Finance Service
        └── Customer Service
````
        