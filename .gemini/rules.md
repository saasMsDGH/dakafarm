# AlfredDev Coding Conventions — Persistent Memory
# Auto-loaded for all AI tasks in this workspace.

You MUST always follow the coding conventions defined for this developer.
Before writing any code, consult and respect ALL of the following rules derived
from analysis of all tajirdev GitHub repositories (signia_backend, AMAS-FARM-Management-System,
NOTEHUB, shop_management_system, backend-engineering-standards).

## Project Structure
- Use: pp/ root with core/, models/, schemas/, outes/, services/ sub-directories
- One file per entity in models, schemas, routes, services
- migrations/ at project root (Alembic)
- For new projects: consider pp/api/v1/<feature>/ structure with API versioning

## FastAPI App Factory (pp/main.py)
- Always: FastAPI(title="<PROJECT NAME> API")
- CORS from env: CORS_ORIGINS comma-separated, never hard-coded
- Routers registered via pp.include_router(Router.router) - imported from route modules
- Static files: os.makedirs("uploads", exist_ok=True) + pp.mount("/uploads", StaticFiles(...))

## Database
- Use pp/core/database.py with get_db() generator using try/finally
- Sync: create_engine + sessionmaker(autocommit=False, autoflush=False)
- Async (new projects only): create_async_engine + AsyncSession
- DATABASE_URL always from env variable, never hard-coded
- Use Base = declarative_base() from sqlalchemy.ext.declarative
- For new projects: use pydantic_settings.BaseSettings for config (see AMAS-FARM pattern)

## SQLAlchemy Models
- Table names: snake_case plural (blog_posts, users, events)
- Always include: id (PK Integer), created_at (DateTime timezone=True, server_default=func.now()), updated_at (same + onupdate=func.now())
- ForeignKey always has ondelete= ("CASCADE" or "SET NULL")
- Status/type columns: use Enum(PythonEnum) not bare String; enum class inherits str, enum.Enum
- All relationships use ack_populates= (never ackref)
- Owned children: cascade="all, delete", passive_deletes=True
- Index FKs, status fields, date lookup fields with index=True

## Pydantic Schemas
- Triple schema per entity: MyModelCreate, MyModelUpdate, MyModelResponse
- ALL response schemas MUST have: model_config = ConfigDict(from_attributes=True)
- EmailStr for email fields
- Optional[X] = None for nullable fields
- Use Field(min_length=, max_length=) for validation
- Generic pagination: PaginatedResponse(BaseModel, Generic[T]) with 	otal, 	otal_pages, items

## Authentication
- JWT: "sub" key = str(user.id) (never email/username)
- Token expiry: 60 minutes default
- Always verify user.is_active in token verification, 403 if inactive
- Login: OAuth2PasswordRequestForm with username field mapped to email
- Two auth dependencies: get_current_user (required) and get_optional_current_user (returns None)
- Password hashing: pwdlib[argon2] via PasswordHash.recommended()

## RBAC
- RoleChecker callable class with __init__(allowed_roles: list[str])
- super_admin always bypasses all role checks
- Role names: lowercase strings ("super_admin", "editor", "member", "user")
- Role checkers instantiated at MODULE LEVEL in route files, not inline
- Last super_admin can never be deleted or demoted (guard in service)

## Routes
- APIRouter(prefix="/resource-name", tags=["Resource Name"]) - always set both
- Service instantiated once at module level
- esponse_model= always specified for data-returning endpoints
- Pagination: page: int = Query(1, ge=1), limit: int = Query(10, ge=1)

## Services
- All services: class-based with def __init__(self): pass
- db: Session passed per-method (not injected in constructor)
- Persistence: db.add() then db.commit() then db.refresh()
- Wrap in 	ry/except IntegrityError then db.rollback() then HTTPException(400, "Conflict: Data already exists.")
- Updates: model_dump(exclude_unset=True) + setattr loop
- Delete: returns {"message": "..."} dict

## Pagination
- page starts at 1; offset = (page - 1) * limit
- Return: {"page", "limit", "total", "total_pages", "items"}
- Search: .ilike(f"%{search}%")

## Error Handling
- ONLY use astapi.HTTPException
- Use status.HTTP_* constants
- Auth errors: include headers={"WWW-Authenticate": "Bearer"}
- 404 not found; 400 bad request/conflict; 401 auth; 403 permission/inactive

## File Uploads
- File I/O abstracted in pp/services/storage/ - never inline in routes
- Media records stored in media table
- Always delete physical file before removing DB record

## Naming
- Files: prefer snake_case for new files
- Classes: PascalCase
- Table names: snake_case plural
- API prefixes: kebab-case plural
- Enum values: lowercase strings

## Environment Variables
- Required: DATABASE_URL, SECRET_KEY, ALGORITHM, CORS_ORIGINS
- Never commit .env - always commit .env.example

## Dependencies (standard stack)
- fastapi, uvicorn, sqlalchemy, pwdlib[argon2], pyjwt, python-multipart
- psycopg2-binary, python-dotenv, alembic, pydantic[email]

## Feature Checklist (always complete for new features)
1. pp/models/<feature>.py - with id, timestamps, status enum
2. pp/schemas/<feature>.py - Create, Update, Response + from_attributes=True
3. pp/services/<feature>_service.py - class-based
4. pp/routes/<feature>.py - APIRouter with prefix + tags
5. Register router in pp/main.py
6. Generate Alembic migration
7. Update .env.example if new env vars added
8. Write tests for all new endpoints
