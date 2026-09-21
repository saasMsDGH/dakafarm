import json
import os

openapi_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/openapi.json'
output_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/docs/api.md'

with open(openapi_path, 'r', encoding='utf-16') as f:
    spec = json.load(f)

paths = spec.get('paths', {})
components = spec.get('components', {}).get('schemas', {})

def resolve_ref(ref):
    if not ref: return None
    ref_name = ref.split('/')[-1]
    return components.get(ref_name)

def get_schema_example(schema, depth=0):
    if depth > 3: return "..."
    if not schema: return "{}"
    if '$ref' in schema:
        return get_schema_example(resolve_ref(schema['$ref']), depth+1)
    
    if schema.get('type') == 'object' or 'properties' in schema:
        props = schema.get('properties', {})
        obj = {}
        for k, v in props.items():
            if v.get('type') == 'string':
                obj[k] = "string"
            elif v.get('type') == 'integer':
                obj[k] = 0
            elif v.get('type') == 'number':
                obj[k] = 0.0
            elif v.get('type') == 'boolean':
                obj[k] = True
            elif v.get('type') == 'array':
                obj[k] = [get_schema_example(v.get('items', {}), depth+1)]
            elif '$ref' in v:
                obj[k] = get_schema_example(resolve_ref(v['$ref']), depth+1)
            else:
                obj[k] = "any"
        return obj
    elif schema.get('type') == 'array':
        return [get_schema_example(schema.get('items', {}), depth+1)]
    return "{}"

modules = {}

for path, methods in paths.items():
    for method, details in methods.items():
        if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']: continue
        
        tags = details.get('tags', ['Other'])
        tag = tags[0] if tags else 'Other'
        if tag not in modules:
            modules[tag] = []
            
        modules[tag].append({
            'path': path,
            'method': method.upper(),
            'details': details
        })

md = []
md.append("# AMAS FARM API Documentation\n")

md.append("## 1. API Overview")
md.append("The AMAS FARM API provides full programmatic access to farm operations, inventory, point of sale (business), human resources, assets, finance, and reporting. The backend is built on **FastAPI** leveraging async **SQLAlchemy** connected to **PostgreSQL**. The API uses RESTful principles and JSON bodies.\n")

md.append("## 2. API Architecture")
md.append("```text\nClient\n   ↓\nFastAPI (main.py)\n   ↓\nRouter (app/api/v1/router.py)\n   ↓\nService (Business Logic)\n   ↓\nRepository (CRUD)\n   ↓\nSQLAlchemy (ORM)\n   ↓\nPostgreSQL\n```\n")

md.append("## 3. Base URL & Versioning")
md.append("The API is versioned at the router level. All standard endpoints are prefixed with `/api/v1/`.\n")
md.append("**Local Development URL**: `http://localhost:8000/api/v1`\n")
md.append("**Production URL**: Configure according to deployment environment.\n")

md.append("## 4. Authentication")
md.append("Authentication is handled via **OAuth2 Password Bearer with JWT tokens**.")
md.append("### POST /login")
md.append("**Request Body (form-data)**")
md.append("```text\nusername: user@example.com\npassword: yourpassword\n```")
md.append("**Response**")
md.append("```json\n{\n  \"access_token\": \"eyJhb...\",\n  \"token_type\": \"bearer\"\n}\n```")
md.append("Include the token in subsequent requests using the header `Authorization: Bearer <token>`.\n")

md.append("## 5. Authorization & RBAC")
md.append("Role-Based Access Control (RBAC) is enforced at the router/endpoint level using the `RoleChecker` dependency class.")
md.append("Typical roles observed in the system:\n* `admin` - Global access\n* `farm_manager` - Farm operations\n* `inventory_admin` - Inventory management\n* `sell_manager` / `sell_officer` - POS and Sales\n* `hr_manager` / `hr_officer` - Payroll and Employees\n* `finance_manager` - Financial ledger and reporting")
md.append("\nFlow:\n```text\nRequest -> get_current_user -> RoleChecker([\"admin\", \"farm_manager\"]) -> Endpoint\n```\n")

md.append("## 6. Common API Conventions")
md.append("* **Content Type**: `application/json`\n* **Auth Header**: `Authorization: Bearer <token>`\n* **IDs**: Integer\n* **Money**: Decimal represented as numbers/strings\n* **Dates**: ISO-8601 strings (e.g. `2026-09-20T14:30:00Z`)\n")

md.append("## 7. Response Format")
md.append("Single objects return a flat JSON object. Paginated collections return:")
md.append("```json\n{\n  \"items\": [...],\n  \"total\": 100,\n  \"page\": 1,\n  \"limit\": 20,\n  \"pages\": 5\n}\n```\n")

md.append("## 8. Error Handling")
md.append("* `400 Bad Request` — Business logic error (e.g., insufficient stock).\n* `401 Unauthorized` — Invalid or missing JWT token.\n* `403 Forbidden` — Valid token, but insufficient role permissions.\n* `404 Not Found` — Resource does not exist.\n* `422 Validation Error` — Pydantic schema validation failure.\n")
md.append("Example Error Body:")
md.append("```json\n{\n  \"detail\": \"Not enough stock available.\"\n}\n```\n")

md.append("## 9. Pagination")
md.append("Endpoints returning collections use `PaginationParams`. Pass query parameters:")
md.append("`?page=1&limit=20` (Defaults to page 1, limit 20).\n")

md.append("## 10. Filtering, Searching & Sorting")
md.append("Common query parameters (varies by endpoint):")
md.append("* `search_query` - String search across name/reference fields.\n* `status` - Filter by specific status.\n* `start_date` / `end_date` - Time boundary filtering (especially in reports).\n")

md.append("## 11. Important Business Workflows")
md.append("### Sales Workflow\n```text\nCreate Sale (Generates invoice) -> Add Sale Items -> Reduce Stock (Stock Movement) -> Create Payment (Sales Payments) -> Log Financial Transaction -> Real-time Reports\n```")
md.append("### Purchases Workflow\n```text\nCreate Purchase -> Add Purchase Items -> Increase Stock -> Create Purchase Payment -> Log Financial Transaction\n```")
md.append("### Payroll Workflow\n```text\nCreate Payroll -> Run Payroll -> Create Payroll Payment -> Log Financial Transaction\n```\n")

md.append("## 12. Financial API Flow")
md.append("The system uses an immutable ledger system. A **Business Transaction** (e.g. Sale) is recorded. A **Payment** is made against it. That payment immediately triggers a **Financial Transaction** linked to a **Financial Account** (Cash/Bank).")
md.append("\n```text\nBusiness Transaction -> Payment Table -> Financial Transaction\n```\n")

md.append("## 13. API Modules & Endpoint Reference\n")

for tag, endpoints in modules.items():
    md.append(f"### Module: {tag}\n")
    for ep in endpoints:
        path = ep['path']
        method = ep['method']
        details = ep['details']
        
        md.append(f"#### {method} {path}\n")
        
        summary = details.get('summary', '')
        desc = details.get('description', summary)
        if desc: md.append(f"**Purpose**\n{desc}\n")
        
        md.append("**Authentication**\nRequired (Bearer Token).\n")
        
        params = details.get('parameters', [])
        if params:
            md.append("**Request Parameters**")
            for p in params:
                md.append(f"* `{p['name']}` ({p['in']}) - Required: {p.get('required', False)}")
            md.append("")
            
        req_body = details.get('requestBody', {})
        if req_body:
            content = req_body.get('content', {}).get('application/json', {})
            schema = content.get('schema', {})
            example = get_schema_example(schema)
            md.append("**Request Body**\n```json")
            md.append(json.dumps(example, indent=2))
            md.append("```\n")
            
        responses = details.get('responses', {})
        succ_res = responses.get('200') or responses.get('201')
        if succ_res:
            content = succ_res.get('content', {}).get('application/json', {})
            schema = content.get('schema', {})
            example = get_schema_example(schema)
            md.append("**Response (Success)**\n```json")
            md.append(json.dumps(example, indent=2))
            md.append("```\n")
            
        md.append("**Status Codes**")
        for code in responses.keys():
            md.append(f"* `{code}`")
        md.append("\n---\n")

md.append("## 14. OpenAPI / Swagger")
md.append("Auto-generated interactive documentation is available when running the server:")
md.append("* Swagger UI: `http://localhost:8000/docs`")
md.append("* ReDoc: `http://localhost:8000/redoc`")
md.append("* Raw OpenAPI JSON: `http://localhost:8000/openapi.json`\n")

md.append("## 15. API Security")
md.append("* **CORS**: Configured via `CORSMiddleware` in `main.py` allowing specified frontend origins.")
md.append("* **Injection**: SQLAlchemy strictly sanitizes input preventing SQL injection.")
md.append("* **Password Hashing**: Stored using bcrypt/argon2 via Passlib.")
md.append("* **JWT**: Stateless tokens with expiration boundaries.")
md.append("* **RBAC**: Handled consistently through FastAPI Dependencies.\n")

md.append("## 16. API Maintenance Notes")
md.append("""When adding a new endpoint:
1. Add the endpoint to the appropriate module router in `app/api/v1/`.
2. Add/update Pydantic schemas in `schemas/`.
3. Implement business logic inside the `service/` layer.
4. Interact with the DB through the `repository/` layer.
5. Secure the endpoint using `get_current_user` and `RoleChecker`.
6. Use `PaginationParams` for list responses.
7. Restart the server and verify changes at `/docs`.""")

with open(output_path, 'w', encoding='utf-16') as f:
    f.write('\n'.join(md))

print("Markdown generated successfully.")
