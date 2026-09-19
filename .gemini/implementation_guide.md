# AMAS FARM — AI Implementation Guide
## How to Implement a Backend Module Without Errors

**Author:** Derived from live implementation of Finance Phase 1 & Phase 2.
**Purpose:** A complete teaching reference for any AI model assigned a new implementation task in this project. Read this **before writing a single line of code.**

---

## PART 1 — BEFORE YOU TOUCH THE KEYBOARD

### Rule 0: Inspect First. Always.

The most common cause of bugs, wasted time, and architectural drift is starting to write code without fully understanding the existing system.

When you receive a task, do this before anything else:

1. Read the **existing module that is most similar** to what you are about to build.
2. Read the **shared utilities** (`app/shared/`, `app/core/`, `app/auth/`).
3. Read the **existing models registry** (`app/db/__init__.py`).
4. Read the **main router** (`app/api/v1/router.py`).
5. Read the **Alembic configuration** and the latest migration file.

Do not rely on memory. Read the actual files every time.

**Why this matters:** This codebase has specific patterns that are not universal FastAPI conventions. If you guess instead of reading, you will break things that were working.

---

### Rule 1: Understand the Stack Deeply

This project uses:

```
FastAPI + SQLAlchemy (async) + PostgreSQL + Alembic + Pydantic v2
```

The async SQLAlchemy session is the single biggest source of runtime bugs. Understand these traps before writing any DB code:

#### Trap 1: Lazy Loading Crashes the App

```python
# WRONG — accessing a relationship after commit without eager loading
user = await db.execute(select(User).where(User.id == 1))
user = result.scalar_one_or_none()
print(user.role.name)  # CRASH: MissingGreenlet
```

**Rule:** Never access a relationship attribute unless you either:
- Used `selectinload(Model.relationship)` in your query, OR
- Called `await db.refresh(object)` after the commit

```python
# CORRECT
from sqlalchemy.orm import selectinload
result = await db.execute(
    select(User).options(selectinload(User.role)).where(User.id == 1)
)
```

#### Trap 2: Accessing `.id` After Commit

```python
# WRONG
db.add(new_record)
await db.commit()
print(new_record.id)  # CRASH: triggers lazy load on expired object
```

**Rule:** Always call `await db.refresh(object)` before accessing scalar fields after a commit.

```python
# CORRECT
db.add(new_record)
await db.commit()
await db.refresh(new_record)
print(new_record.id)  # Works
```

#### Trap 3: Overwriting an Unloaded Collection

```python
# WRONG — triggers lazy load if collection was never loaded
record.items = []  # CRASH: MissingGreenlet
```

**Rule:** Never assign to a relationship collection unless you loaded it first with `selectinload`.

---

## PART 2 — THE EXACT PROJECT PATTERNS

These are not opinions. These are the exact patterns used throughout this codebase. Deviate from them and you will cause hard-to-debug inconsistencies.

### Pattern A: Directory Structure for a Module

Every module follows this structure exactly:

```
app/api/v1/<module_name>/
    models/
        <entity>.py
    schemas/
        <Entity>Schema.py
    repository/
        <Entity>Repo.py
    service/
        <Entity>Service.py
    Router/
        <entity>_router.py
```

Note: `Router/` is capitalized. This is how it is everywhere in this project. Match it.

---

### Pattern B: The SQLAlchemy Model

Look at any existing model (`account.py`, `asset.py`, `payroll.py`) — they all share this exact structure:

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class YourModel(Base):
    __tablename__ = "your_table_name_plural"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Business columns
    name = Column(String(150), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text, nullable=True)

    # Foreign keys: always include ondelete=
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Audit timestamps: always both, always timezone=True
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships: always use back_populates, never backref
    user = relationship("Users")
```

**Critical rules for models:**

- `ondelete="RESTRICT"` — when deleting the parent must be prevented (e.g. deleting a FinancialAccount that has transactions).
- `ondelete="SET NULL"` — when the referenced user might be deleted (created_by fields).
- `ondelete="CASCADE"` — when child records should be deleted with the parent.
- **Status and Type columns are plain `String`** in this codebase, NOT SQLAlchemy `Enum` columns. Validation happens in the Pydantic schema layer, not the database layer.
- Always `index=True` on ForeignKey columns, type/status columns, and date columns used for filtering.

---

### Pattern C: The Pydantic Schema

Schemas have a specific structure — see `AccountSchema.py`, `ExpenseSchema.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Enums live HERE in schemas, NOT in models
class SomeType(str, Enum):
    OPTION_A = "OPTION_A"
    OPTION_B = "OPTION_B"

# Create schema — all required fields
class YourModelCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    some_type: SomeType
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None

# Update schema — ALL fields optional
class YourModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    is_active: Optional[bool] = None

# Response schema — must have from_attributes
class YourModelResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # REQUIRED — enables ORM mode

# List response — always this exact shape
class YourModelListResponse(BaseModel):
    items: List[YourModelResponse]
    total: int
    page: int
    limit: int
    pages: int
```

**Why enums in schemas instead of models?**
Because the DB stores a plain `String`. The schema validates the value before it reaches the DB. This is simpler, migration-safe, and consistent with how `AccountType`, `TransactionType`, and `Direction` are all handled in this project.

---

### Pattern D: The Repository

The repository is responsible for database access **only**. No business logic lives here.

```python
from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.<module>.models.<entity> import YourModel
from app.shared.pagination import PaginationParams

class YourRepo:

    @staticmethod
    async def create(db: AsyncSession, obj: YourModel) -> YourModel:
        try:
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A record with this data already exists."
            )
        return obj

    @staticmethod
    async def get_by_id(db: AsyncSession, obj_id: int) -> Optional[YourModel]:
        result = await db.execute(
            select(YourModel).where(YourModel.id == obj_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        params: PaginationParams,
        filter_field: Optional[str] = None
    ) -> Tuple[List[YourModel], int]:
        query = select(YourModel)

        # Apply filters
        if filter_field:
            query = query.where(YourModel.some_column == filter_field)

        # Apply search (always use ilike for case-insensitive)
        if params.search:
            term = f"%{params.search}%"
            query = query.where(
                or_(
                    YourModel.name.ilike(term),
                    YourModel.description.ilike(term),
                )
            )

        # Count BEFORE applying pagination (after filters/search)
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Sorting with safe fallback
        sort_column = getattr(YourModel, params.sort_by, YourModel.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Pagination
        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def update(db: AsyncSession, obj: YourModel, data: dict) -> YourModel:
        for field, value in data.items():
            if value is not None:
                setattr(obj, field, value)
        try:
            await db.commit()
            await db.refresh(obj)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error during update."
            )
        return obj
```

**Key repository rules:**
- The repository **owns the commit**. The service does not commit again.
- `count()` is called on the filtered query **before** `.offset().limit()` — if you do it after, you count the paginated result, not the total.
- `getattr(Model, params.sort_by, Model.created_at)` — this is the safe sort pattern. If the client passes an invalid column name, it falls back to `created_at` instead of crashing.
- Return `scalar_one_or_none()` from get queries, never `fetchall()` for single items.

---

### Pattern E: The Service

```python
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.<module>.models.<entity> import YourModel
from app.api.v1.<module>.repository.YourRepo import YourRepo
from app.api.v1.<module>.schemas.YourSchema import YourCreate, YourUpdate, YourListResponse
from app.shared.pagination import PaginationParams, compute_pages

class YourService:

    @staticmethod
    async def create(db: AsyncSession, request: YourCreate, current_user_id: int) -> YourModel:
        # Business validation goes HERE, not in the repo
        # Example: check uniqueness, check related records, etc.

        new_obj = YourModel(
            name=request.name,
            amount=request.amount,
            created_by=current_user_id,
        )
        return await YourRepo.create(db, new_obj)

    @staticmethod
    async def get_one(db: AsyncSession, obj_id: int) -> YourModel:
        obj = await YourRepo.get_by_id(db, obj_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record {obj_id} not found."
            )
        return obj

    @staticmethod
    async def list_all(db: AsyncSession, params: PaginationParams) -> YourListResponse:
        items, total = await YourRepo.list(db, params)
        return YourListResponse(
            items=items,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, obj_id: int, request: YourUpdate) -> YourModel:
        obj = await YourRepo.get_by_id(db, obj_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
        update_data = request.model_dump(exclude_unset=True)
        return await YourRepo.update(db, obj, update_data)
```

**Key service rules:**
- Business rules (validate FK existence, check active status, enforce constraints) go in the service.
- Database queries for validation (e.g. "does this account exist?") use `db.execute(select(...))` directly in the service — the service is allowed to read the DB.
- **Never** call `db.commit()` in the service unless the repo does not commit. In this project, repos commit — so services do not.
- Use `request.model_dump(exclude_unset=True)` for updates — this ensures only fields that the client actually sent get updated.

---

### Pattern F: The Router

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.<module>.schemas.YourSchema import (
    YourCreate, YourListResponse, YourResponse, YourUpdate
)
from app.api.v1.<module>.service.YourService import YourService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

# RBAC checkers defined at MODULE LEVEL, not inside route functions
some_role_checker = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/your-resource",
    tags=["Your Resource"],
    redirect_slashes=False,  # Always include this
)

@router.post(
    "/",
    response_model=YourResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new record"
)
async def create_record(
    request: YourCreate,
    current_user: Users = Depends(some_role_checker),
    db: AsyncSession = Depends(get_db),
) -> YourResponse:
    return await YourService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=YourListResponse,
    summary="List records"
)
async def list_records(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=500),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(some_role_checker),
    db: AsyncSession = Depends(get_db),
) -> YourListResponse:
    params = PaginationParams(page=page, limit=limit, search=search, sort_by=sort_by, order=order)
    return await YourService.list_all(db, params)

@router.get("/{record_id}", response_model=YourResponse, summary="Get by ID")
async def get_record(
    record_id: int,
    current_user: Users = Depends(some_role_checker),
    db: AsyncSession = Depends(get_db),
) -> YourResponse:
    return await YourService.get_one(db, record_id)

@router.put("/{record_id}", response_model=YourResponse, summary="Update a record")
async def update_record(
    record_id: int,
    request: YourUpdate,
    current_user: Users = Depends(some_role_checker),
    db: AsyncSession = Depends(get_db),
) -> YourResponse:
    return await YourService.update(db, record_id, request)
```

**Key router rules:**
- Routers are **thin** — no business logic, no DB queries.
- `redirect_slashes=False` — always include this to avoid unexpected 307 redirects.
- `current_user.id` — pass the user ID to the service for audit trails.
- Pagination parameters are **explicitly** declared in the router, not injected as a Depends. This makes the Swagger docs self-documenting.

---

### Pattern G: Registering in db/\__init__.py

Every new SQLAlchemy model **must** be imported here:

```python
# At end of app/db/__init__.py
from app.api.v1.finance.models.transaction import FinancialTransaction
```

And added to `__all__`:

```python
__all__ = [..., "FinancialTransaction"]
```

**Why this matters:** Alembic's `autogenerate` discovers tables from SQLAlchemy's `Base.metadata`. If the model is not imported somewhere in the import chain that Alembic loads, `autogenerate` will not see it and will generate an empty migration.

---

### Pattern H: Registering the Router in v1/router.py

```python
from app.api.v1.finance.Router import transaction_router

# Add to the APIRouter includes:
router.include_router(transaction_router.router, prefix="/finance")
```

The URL will become: `/api/v1/finance/transactions/` — because:
- `/api` — main app prefix
- `/v1` — versioned router prefix
- `/finance` — module prefix (added in `include_router`)
- `/transactions` — resource prefix (defined in the router itself)

---

## PART 3 — THE ALEMBIC MIGRATION WORKFLOW

**Never skip these steps. Ever.**

### Step 1: Make sure the model is imported in `db/__init__.py`

Alembic only sees models that have been imported.

### Step 2: Generate the migration

```bash
docker exec ms_farms alembic revision --autogenerate -m "Add <table_name> table"
```

### Step 3: READ the generated migration file before applying it

Check for:
- Is the table name correct?
- Are all columns present?
- Are the foreign key constraints correct? (`RESTRICT` vs `SET NULL` vs `CASCADE`)
- Are the indexes created?
- Is `down_revision` pointing to the correct previous migration?
- Is there anything unexpected (Alembic sometimes picks up unrelated changes)?

### Step 4: Apply the migration

```bash
docker exec ms_farms alembic upgrade head
```

### Step 5: Verify

```bash
docker logs ms_farms --tail 5
```

Look for: `Running upgrade <old> -> <new>, <description>`. No errors.

---

## PART 4 — THE TESTING STRATEGY

### Why tests matter here

This is a financial management system. Untested code can corrupt farm data, financial records, and HR payroll. Testing is not optional.

### The test file pattern

All existing tests (`test_pos_customers.py`, `test_pos_sales.py`, `test_finance_accounts.py`) follow this pattern:

```python
import requests
import uuid

BASE_URL = "http://localhost:8000"
RUN_ID = uuid.uuid4().hex[:8]  # Unique suffix for this test run
ADMIN_EMAIL = f"admin_test_{RUN_ID}@amas.com"  # Unique per run

def req(method, path, json=None, token=None, params=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.request(method, BASE_URL + path, json=json, headers=headers, params=params)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text

def form_req(path, data):
    r = requests.post(BASE_URL + path, data=data,
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
    return r.status_code, r.json()

PASS_COUNT = 0
FAIL_COUNT = 0

def check(name, status_code, body, expected_status):
    global PASS_COUNT, FAIL_COUNT
    if status_code == expected_status:
        print(f"  PASS  {name}")
        PASS_COUNT += 1
    else:
        print(f"  FAIL  {name}")
        print(f"        got={status_code}  expected={expected_status}  body={body}")
        FAIL_COUNT += 1
```

**Important note about Unicode in test files:** Do not use Unicode emoji characters (✅ ❌) in Python strings produced by PowerShell `@'...'@` heredocs — they cause `SyntaxError: unterminated f-string literal`. Use plain ASCII text (`PASS`, `FAIL`) inside the string literal.

### What to test for every module

For every new backend module, test at minimum:

1. **Create — valid** — works, returns 201, fields are correct
2. **Create — validation** — zero/negative amounts rejected, invalid enum rejected, missing fields rejected (422)
3. **Create — FK validation** — nonexistent related record returns 404, inactive record returns 422
4. **Get by ID — valid** — 200, returns correct data
5. **Get by ID — not found** — 404
6. **List — empty** — 200, `total=0`, `items=[]`
7. **List — with data** — 200, correct count
8. **Filters** — one test per filter parameter
9. **Search** — matches expected fields
10. **Pagination** — page 1 with limit 2, page 2, multiple pages
11. **Sorting** — ASC, DESC, invalid field (should not crash)
12. **Auth** — no token → 401 on all endpoints
13. **RBAC** — wrong role → 403
14. **Immutability** (if applicable) — PUT/DELETE → 405

### Running tests

```bash
docker exec ms_farms python test_<module_name>.py
```

Tests run inside the Docker container because `requests` calls `localhost:8000` from inside the network.

---

## PART 5 — THE IMPLEMENTATION WORKFLOW

Follow this exact sequence every time. Do not skip steps.

```
STEP 1 — Read existing similar modules
STEP 2 — Read shared utilities and auth
STEP 3 — Write a plan and explain key design decisions
         (If uncertain about a decision, STOP and ask the developer before proceeding)
STEP 4 — Write the model
STEP 5 — Register model in db/__init__.py
STEP 6 — Add relationships to related models if needed
STEP 7 — Generate Alembic migration
STEP 8 — Read the generated migration — inspect it
STEP 9 — Apply migration
STEP 10 — Write schemas
STEP 11 — Write repository
STEP 12 — Write service
STEP 13 — Write router
STEP 14 — Register router in v1/router.py
STEP 15 — Restart the backend
STEP 16 — Check logs — must say "Application startup complete" with no errors
STEP 17 — Write test file
STEP 18 — Run tests
STEP 19 — Fix ALL failures — do not move on with failing tests
STEP 20 — Run tests again to confirm fixes did not break other tests
STEP 21 — Verify backend logs are clean after the test run
STEP 22 — Report completion
```

---

## PART 6 — COMMON BUGS AND HOW TO FIX THEM

### Bug: 500 reported as CORS error

**Symptom:** Browser says "No Access-Control-Allow-Origin header". Backend logs show a real 500 error.

**Cause:** Unhandled Python exceptions in FastAPI bypass CORS middleware.

**Fix:** Always check `docker logs ms_farms` first — the real error is there, not in the browser.

---

### Bug: 422 Unprocessable Entity from FastAPI

**Symptom:** API returns 422.

**Cause:** Pydantic validation failed. The body is a JSON array of error objects: `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`.

**Fix:** Read `response.json()["detail"]` — it tells you exactly which field failed and why.

**Frontend trap:** Never pass `response.data.detail` (an array) directly to SweetAlert2 — it expects a string. Always map it: `data.detail.map(e => e.msg).join(", ")`.

---

### Bug: IntegrityError — null value violates not-null constraint

**Symptom:** SQLAlchemy `IntegrityError` with `NotNullViolationError`.

**Cause:** A required column was not assigned when constructing the model object.

**Fix:** Compare every `nullable=False` column in the model to the constructor call in the service. Find the missing assignment.

---

### Bug: MissingGreenlet

**Symptom:** `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.`

**Cause:** SQLAlchemy tried to lazy-load a relationship inside async context.

**Fix:** Use `selectinload(Model.relationship)` in your query, or restructure to avoid relationship access after commit.

---

### Bug: Text-replacement scripts break unrelated code

**Symptom:** A regex or string replace script accidentally modifies code it wasn't meant to touch.

**Real example from this project:** A script meant to remove `location` from the `Asset` model also stripped `location` from `AssetDistribution`, causing null constraint violations.

**Fix:**
- Never use broad regex (`re.sub`) to modify multiple-model files.
- Use exact `code.replace(exact_old_block, exact_new_block)` — if the string is not found, the replace is a no-op and does not corrupt anything.
- After any automated code modification, read the modified file to verify the change.

---

## PART 7 — FINANCIAL DATA SPECIAL RULES

This project is a financial management system. These rules are stricter than a normal CRUD app.

### Amounts are always positive — direction carries the sign

```
WRONG: direction=IN, amount=-500000
RIGHT: direction=IN, amount=500000
RIGHT: direction=OUT, amount=500000
```

### Financial transactions may be immutable

Depending on the business context, some records should not allow `PUT` or `DELETE` after creation. For financial transactions, the correct approach is a future **Reversal** mechanism, not editing the original row.

When implementing a module that records money movements, always ask:
> "Should this be editable, or should corrections go through a reversal?"

### Inactive accounts cannot receive transactions

When a financial account is deactivated, existing transaction history must be preserved (never deleted). New transactions against the account must be blocked. Always check `is_active` in the service before creating a transaction.

### Opening balances are separate from transaction rows

Never create a transaction row to represent an opening balance. The opening balance is a property of the `FinancialAccount`. Future balance formulas will be:

```
current_balance = opening_balance
               + SUM(transactions WHERE direction='IN')
               - SUM(transactions WHERE direction='OUT')
```

---

## PART 8 — CLEANUP RULES

After completing any implementation task:

1. Delete all temporary Python scripts (`fix_something.py`, `create_data.py`, etc.) that were used during development. Do not leave them in the repo.
2. Do not leave debug `print()` statements in production code.
3. Do not commit `.env` files.
4. Verify `docker logs ms_farms` is clean after your changes.

---

## SUMMARY — THE ONE-PAGE CHECKLIST

Before marking any task complete:

- [ ] Read existing similar module — did not guess patterns
- [ ] Model: `nullable=False` on required fields, correct `ondelete=`, both timestamps
- [ ] Model registered in `db/__init__.py` and `__all__`
- [ ] Migration generated → inspected → applied → verified
- [ ] Schema: enums in schema layer, not model; `model_config = {"from_attributes": True}` on response
- [ ] Repository: count before pagination; safe sort fallback; no business logic
- [ ] Service: validates FK existence and active status; does not commit if repo commits
- [ ] Router: `redirect_slashes=False`; RBAC at module level; thin
- [ ] Router registered in `v1/router.py`
- [ ] Backend restarted and logs show `Application startup complete` with no errors
- [ ] Test suite written covering: valid creates, validation rejections, get by ID, list, filters, search, pagination, sort, auth/RBAC
- [ ] All tests pass
- [ ] Temporary scripts deleted
- [ ] Backend logs clean after test run
