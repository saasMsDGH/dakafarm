# AMAS FARM MANAGEMENT SYSTEM

## Agent Initialization & Engineering Rules

You are working on the **AMAS FARM Management System**.

This is not a demo or a simple CRUD application. The goal is to build a **production-ready farm management platform** that can grow over time and eventually become the central operational and management system for AMAS FARM.

---

# 1. PROJECT PURPOSE

AMAS FARM will contain multiple interconnected subsystems.

Each subsystem manages a specific area of the business, while a central/general system will eventually combine information from all subsystems to provide management-level visibility.

The system should support:

* Daily operations
* Record keeping
* Operational monitoring
* Financial management
* Farm production monitoring
* Inventory management
* Staff management
* Business management
* Centralized reporting
* Management analysis

The final system should be capable of producing:

* Daily reports
* Weekly reports
* Monthly reports
* Yearly reports

The long-term goal is to allow management to understand what is happening across the farm without manually combining information from different records.

---

# 2. PROJECT DEVELOPMENT STRATEGY

We are building the system **subsystem by subsystem**.

The development process will follow phases.

Example:

```text
Phase 1
Farm Module
    ├── Backend
    ├── Frontend
    ├── Integration
    └── Testing

Phase 2
Sales / Business Module
    ├── Backend
    ├── Frontend
    ├── Integration
    └── Testing

Phase 3
Inventory Module
    ├── Backend
    ├── Frontend
    ├── Integration
    └── Testing

...
```

Do NOT implement future modules unless explicitly instructed.

Do NOT introduce features simply because they may be useful later.

Build the current phase properly, while keeping the architecture extensible.

---

# 3. CURRENT PHASE

The current phase is:

> **FARM MODULE**

The immediate objective is to complete the Farm module's:

* Database models
* Schemas
* Repositories
* Services
* API routes
* Backend tests
* Frontend pages/components
* Frontend-backend integration
* Validation
* Error handling
* Final module testing

The Farm module will become the **reference implementation** for the architecture of future modules.

Therefore, do not rush this module.

The patterns, naming conventions, error handling, repository design, service design, API conventions, testing approach, and frontend/backend communication established here should be reusable for future modules.

---

# 4. EXISTING PROJECT FOUNDATION

The project already has important infrastructure.

The following already exist:

* Database
* PostgreSQL
* Docker
* Authentication
* Folder structure
* Alembic
* RBAC
* Existing project configuration

You are allowed to:

* Inspect existing implementation
* Reuse existing infrastructure
* Modify existing implementation when necessary
* Refactor incorrect implementation
* Fix architectural problems
* Improve existing code when required for correctness

Do NOT assume existing code is perfect.

Before implementing something new, inspect the existing project and understand how it currently works.

Do not unnecessarily replace working infrastructure.

---

# 5. BACKEND ARCHITECTURE

The backend uses a **modular monolith architecture**.

Each subsystem must be independently organized.

Current structure:

```text
farm/
├── models/
├── schemas/
├── repository/
├── service/
└── router/
```

Future modules should follow the same architectural pattern.

Example:

```text
sales/
├── models/
├── schemas/
├── repository/
├── service/
└── router/
```

```text
inventory/
├── models/
├── schemas/
├── repository/
├── service/
└── router/
```

Do not create unnecessary architectural layers.

---

# 6. RESPONSIBILITY OF EACH LAYER

## Models

Responsible for:

* SQLAlchemy models
* Database relationships
* Database constraints
* Database-level structure

Models must not contain:

* API logic
* HTTP logic
* Business workflows

---

## Schemas

Responsible for:

* Request validation
* Response schemas
* Input/output contracts
* Pagination/filter schemas where appropriate

Schemas must not contain database queries.

---

## Repository

Responsible for:

* Database queries
* Selecting records
* Creating records
* Updating records
* Deleting records
* Filtering
* Searching
* Sorting
* Pagination queries
* Database-specific operations

The repository is the database access layer.

Do not put business decisions inside repositories.

---

## Service

Responsible for:

* Business logic
* Business rules
* Validation that depends on business rules
* Coordinating repositories
* Coordinating multiple operations
* Transaction-level workflows

Example:

```text
Create Sale
    ↓
Check customer
    ↓
Check stock
    ↓
Create sale
    ↓
Update inventory
    ↓
Record financial transaction
```

This workflow belongs to the service layer.

---

## Router

Responsible for:

* HTTP endpoints
* Request parameters
* Dependencies
* Authentication/authorization dependencies
* Calling services
* Returning responses

Routers should remain thin.

Do not put complex SQL queries or business workflows inside routers.

---

# 7. API VERSIONING

The API must be versioned.

Current API:

```text
/api/v1/
```

Examples:

```text
/api/v1/farm/houses
/api/v1/farm/flocks
/api/v1/farm/production
```

Do not create unversioned business endpoints such as:

```text
/farm/houses
```

unless there is a deliberate infrastructure reason.

Future breaking API changes may introduce:

```text
/api/v2/
```

Do not create v2 unless required.

---

# 8. ROUTER ORGANIZATION

The project should maintain a clear router hierarchy.

Conceptually:

```text
main.py
   ↓
api/router.py
   ↓
api/v1/router.py
   ↓
module/router.py
```

Example:

```text
/api/v1/farm/...
```

The purpose is to make future API versions possible without destroying existing clients.

---

# 9. DATABASE PRINCIPLES

Use the existing PostgreSQL + SQLAlchemy + Alembic architecture.

All database changes must be handled through **Alembic migrations**.

Do not manually modify database structure as a replacement for migrations.

Before creating a new table:

1. Check existing models.
2. Check existing relationships.
3. Check whether the information already exists elsewhere.
4. Avoid duplicated data.
5. Define appropriate constraints.
6. Consider indexes where they materially improve common queries.

The database should be normalized enough to maintain data integrity, but do not over-engineer it.

---

# 10. TRANSACTION RULES

Be especially careful with operations that modify multiple tables.

For example:

```text
Sale
 ├── Sale Items
 ├── Inventory
 ├── Customer Balance
 └── Financial Transaction
```

These operations may need to succeed or fail together.

The service layer should control the business transaction workflow.

Do not randomly commit from multiple layers.

Establish one consistent transaction pattern and reuse it.

---

# 11. PAGINATION, SEARCH, FILTERING AND SORTING

List endpoints should be designed for real-world data volumes.

Where appropriate, support:

* Pagination
* Searching
* Filtering
* Sorting
* Date ranges

Example:

```text
GET /api/v1/farm/flocks
    ?page=1
    &limit=20
    &search=FLK-001
    &status=active
    &sort_by=arrival_date
    &order=desc
```

Use reusable pagination patterns rather than rewriting the same logic differently in every module.

Module-specific filters should remain specific to that module.

Do not create unnecessary generic abstractions before there is a real need.

---

# 12. ERROR HANDLING

Errors must be predictable and useful.

Handle common situations such as:

* Resource not found
* Duplicate records
* Invalid input
* Unauthorized access
* Forbidden operation
* Invalid relationships
* Database integrity errors
* Insufficient stock
* Invalid business operations

Do not expose raw database errors to users.

Example:

Instead of exposing:

```text
sqlalchemy.exc.IntegrityError: ...
```

return an appropriate API-level error.

However, do not hide useful debugging information from logs.

---

# 13. AUTHENTICATION AND RBAC

Authentication and RBAC already exist.

Reuse them.

Do not create a second authentication system inside individual modules.

Each module should use the existing authentication/authorization architecture.

When an endpoint requires permissions, enforce them consistently.

Do not assume that hiding a frontend button is sufficient authorization.

Authorization must be enforced by the backend.

---

# 14. TESTING RULE

Testing is mandatory.

Do not assume that code works because it looks correct.

For important functionality:

1. Implement
2. Run
3. Test
4. Inspect errors
5. Fix
6. Run again
7. Test related functionality
8. Test edge cases

Test multiple scenarios.

For example, if implementing a flock endpoint, do not test only:

```text
Valid flock → success
```

Also test:

```text
Duplicate flock code
Invalid house
Invalid quantity
Missing required data
Unauthorized user
Nonexistent flock
Update existing flock
Delete existing flock
Pagination
Search
Filtering
Sorting
```

The objective is not merely:

> "The endpoint runs."

The objective is:

> "The feature behaves correctly under realistic conditions."

---

# 15. DEBUGGING RULE

When something fails, do not immediately rewrite the entire feature.

First identify:

```text
What failed?
        ↓
Where did it fail?
        ↓
Why did it fail?
        ↓
What is the smallest correct fix?
        ↓
Does the fix affect another part of the system?
        ↓
Run tests again
```

When debugging:

* Read the traceback carefully.
* Inspect the relevant code.
* Inspect database relationships.
* Inspect schemas.
* Inspect the request/response.
* Verify assumptions.
* Fix the root cause.

Do not repeatedly patch symptoms without understanding the underlying problem.

---

# 16. DATABASE PROBLEM-SOLVING

You are expected to be capable of diagnosing database problems yourself.

When a database issue appears, investigate:

* Model definitions
* Foreign keys
* Relationships
* Constraints
* Query construction
* Async/sync usage
* Session handling
* Transactions
* Migrations
* Existing database state

Do not immediately ask the developer to solve problems that can be diagnosed from the project.

If the database design is genuinely wrong, explain the problem and propose the smallest appropriate correction.

---

# 17. API PROBLEM-SOLVING

You are also expected to diagnose route/API problems yourself.

Check:

* Router registration
* API version prefix
* Endpoint path
* HTTP method
* Dependencies
* Authentication
* RBAC
* Request schema
* Response schema
* Service function
* Repository query
* Database state

For example, if:

```text
POST /api/v1/farm/flocks
```

returns 404, do not assume the service is broken.

First trace:

```text
main.py
 ↓
api/router.py
 ↓
v1/router.py
 ↓
farm/router.py
 ↓
endpoint
```

---

# 18. PATTERN MEMORY / ARCHITECTURAL CONSISTENCY

This is extremely important.

Once a correct pattern has been established and approved in the Farm module, **remember it and reuse it**.

Do not implement each module using a completely different style.

For example, if Farm establishes:

```text
Router
 ↓
Service
 ↓
Repository
 ↓
Database
```

then Sales, Inventory, Finance, HR, Assets, etc. should follow the same pattern unless there is a legitimate architectural reason not to.

Before creating a new pattern, ask:

> "Do we already have an established project pattern for this?"

Prefer consistency over novelty.

Do not introduce a new abstraction merely because another architecture exists.

---

# 19. DO NOT OVER-ENGINEER

This is a core project rule.

We want:

> **Production quality without unnecessary complexity.**

Do NOT introduce:

* Microservices without a real requirement
* Event-driven architecture without a real requirement
* Unnecessary design patterns
* Excessive abstraction
* Dozens of helper classes for simple operations
* Generic systems that solve problems we do not have
* Extra dependencies without justification
* Premature optimization

Before introducing complexity, ask:

> "Does this solve a real problem in AMAS FARM?"

If not, keep the simpler implementation.

---

# 20. CODE QUALITY

Write code that another developer can understand.

Prefer:

* Clear naming
* Small focused functions
* Consistent structure
* Type hints
* Proper async handling
* Reusable patterns
* Meaningful error messages
* Clear separation of responsibilities

Avoid clever code when simple code is easier to understand.

---

# 21. FRONTEND

The frontend should consume the backend through the versioned API.

Do not duplicate backend business rules unnecessarily in the frontend.

Frontend should handle:

* User interface
* Form interaction
* Client-side validation where useful
* API communication
* Loading states
* Error states
* Success states
* Tables
* Search/filter/sort controls
* Pagination
* Responsive design

Backend remains responsible for authoritative validation and business rules.

---

# 22. DEVELOPMENT WORKFLOW

For every feature:

```text
UNDERSTAND
    ↓
PLAN
    ↓
IMPLEMENT
    ↓
TEST
    ↓
DEBUG
    ↓
INTEGRATE
    ↓
TEST AGAIN
```

Do not start coding immediately when a requirement is ambiguous.

First inspect the existing project and understand how the feature fits into the architecture.

---

# 23. BEFORE MODIFYING EXISTING CODE

Before changing existing code:

1. Read the relevant files.
2. Understand their relationships.
3. Identify what currently works.
4. Identify the actual problem.
5. Make the smallest safe change.
6. Run tests.

Do not destroy working functionality just to make implementation easier.

---

# 24. WHEN REQUIREMENTS ARE UNCLEAR

Do not silently invent important business rules.

If the missing information affects:

* Database design
* Financial calculations
* Permissions
* Business rules
* Data relationships
* User workflows

pause and clearly explain the ambiguity.

If the decision is minor and a reasonable default is obvious, use the simplest sensible default and document it.

---

# 25. SECURITY

Treat the system as a real production application.

Pay attention to:

* Authentication
* Authorization
* Password handling
* Input validation
* SQL injection prevention
* Sensitive information
* File uploads
* Access control
* Environment variables
* Secrets
* Error information leakage

Never hard-code secrets.

Never commit `.env` credentials.

---

# 26. OBSERVABILITY AND LOGGING

When useful, provide enough logging to diagnose failures in production.

Logs should help answer:

```text
What happened?
When did it happen?
Which operation failed?
Why did it fail?
```

Do not log passwords, tokens, or other sensitive credentials.

---

# 27. AGENT AUTONOMY

You are expected to solve ordinary implementation and debugging problems independently.

You may:

* Inspect files
* Search the codebase
* Trace dependencies
* Run tests
* Run migrations
* Fix implementation errors
* Refactor incorrect code
* Verify API behavior
* Verify database behavior
* Fix frontend/backend integration issues

Do not stop at the first error.

Investigate the root cause.

However, do not make major architectural or business decisions silently.

For major decisions, explain:

```text
Problem
Options
Recommended solution
Reason
```

Then proceed according to the project's established rules.

---

# 28. DEFINITION OF DONE

A feature is NOT complete simply because code has been written.

A feature is complete when:

```text
Code implemented
       ↓
Database correct
       ↓
Migration created
       ↓
API registered
       ↓
Authentication/RBAC checked
       ↓
Validation checked
       ↓
Business logic tested
       ↓
Database queries tested
       ↓
Edge cases tested
       ↓
Frontend integrated
       ↓
Frontend behavior tested
       ↓
Errors handled
       ↓
Existing functionality verified
```

Only then should the feature be considered complete.

---

# 29. CURRENT FARM MODULE STRUCTURE

Start from:

```text
farm/
├── models/
├── schemas/
├── repository/
├── service/
└── router/
```

The Farm module will eventually cover the farm-related records defined in the project database design, including:

```text
Houses
Flocks
Production
Feed
Medication
Vaccination
Mortality
```

Respect the existing database design unless development reveals a legitimate reason to modify it.

If changes are necessary, update:

```text
Model
↓
Alembic migration
↓
Schema
↓
Repository
↓
Service
↓
Router
↓
Tests
```

Do not modify only one layer and leave the rest inconsistent.

---

# 30. IMPORTANT PROJECT MINDSET

This project will grow.

Do not write code only for today's endpoint.

But also do not build imaginary systems for problems that do not exist yet.

The target is:

> **Simple enough to develop quickly. Structured enough to grow. Reliable enough for production.**

Every implementation should balance these three goals.

---

# 31. FINAL RULE

Before implementing any feature, understand:

```text
What are we building?
Why are we building it?
Where does it belong?
What existing pattern should it follow?
What data does it depend on?
What other modules does it affect?
How will we test it?
```

Then implement it.

The **Farm module is the reference module**.

Future modules should learn from its established patterns rather than inventing new architecture.

Do not forget established project conventions between tasks.

When in doubt, prioritize:

1. Correctness
2. Data integrity
3. Security
4. Maintainability
5. Simplicity
6. Performance

Build carefully. Verify your work. Fix root causes. Keep the architecture consistent.
