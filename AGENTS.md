# Do's
- functions should have a single responsibility
- functions should have maximum 15-20 lines, max 120 chars in line, and don't put function arguments in one long line. 
- classes should have maximum 100 lines
- no useless classes if it can be a simple function
- write clear and concise comments
- code should read easily like a story
# Don'ts
- Never run git restore
- Never run git reset HARD

# Architecture
This repository uses a **domain-oriented FastAPI architecture**.
All coding agents MUST follow these rules when generating or modifying code.
Violating these rules introduces architectural drift.

## 1. Project Structure
The project uses **domain-based modules**.
Structure:
src/
  main.py
  config.py
  database.py
  auth/
  users/
  posts/

Each directory inside `src/` represents a **business domain**.

Do NOT create global folders like:

  routers/
  services/
  schemas/

## 2. Module Layout

Each domain module should contain:

router.py  
schemas.py  
models.py  
service.py  
dependencies.py  
exceptions.py  

Optional files:

constants.py  
config.py  
utils.py  

Module responsibility rules:

router.py → HTTP endpoints  
schemas.py → Pydantic request/response models  
models.py → database models  
service.py → business logic  
dependencies.py → reusable FastAPI dependencies  
exceptions.py → domain errors

Routers must remain thin.

Business logic must live in `service.py`.


## 3. Routing Rules

Routes must:

• use REST conventions  
• return Pydantic models  
• delegate logic to services  

Example flow:

HTTP request  
→ router  
→ dependency validation  
→ service  
→ database  

Routers must NOT contain:

• database queries  
• complex business logic


## 4. Dependency Design

Use FastAPI dependencies for:

• authentication
• authorization
• resource loading
• validation

Dependencies must be:

• reusable
• composable
• side-effect free where possible

Dependencies should load domain resources such as:

get_current_user  
get_post_by_id  
get_project_member


## 5. Async Rules

All IO-bound operations must be asynchronous.

Rules:

• use async routes  
• use async database sessions  
• never run blocking IO in async routes  

CPU-heavy work must run in background workers.


## 6. Database Layer

Use:

SQLAlchemy  
Alembic migrations

Database access belongs inside services.

Do NOT access the database directly from routers.

Prefer designing queries first, then mapping results to schemas.


## 7. Pydantic Usage

Use Pydantic for:

• request validation  
• response serialization  
• settings management  
• enums and constrained types  

Create shared base schemas if serialization behavior must be standardized.


## 8. Shared Code

Only cross-domain code may exist at the root level.

Allowed shared files:

src/config.py  
src/database.py  
src/exceptions.py  
src/utils.py  

Domain logic must stay inside modules.


## 9. Testing

Every feature must include tests.

Testing stack:

pytest  
httpx AsyncClient

Tests should cover:

• services  
• routers  
• dependencies  


## 10. Tooling

Use existing project tooling.

Linting and formatting:
Ruff

Migrations:
Alembic

Testing:
pytest

Agents must follow existing configuration.


## 11. Feature Implementation Workflow

When adding a new feature:

1. Identify the correct domain module.
2. Add schemas.
3. Add service logic.
4. Add router endpoints.
5. Add dependencies if required.
6. Add database models and migrations.
7. Add tests.

Do NOT implement cross-domain features in a single module.


## 12. Layer Responsibilities

router → HTTP layer  
dependencies → request validation / access control  
service → business logic  
models → database representation  
schemas → API contract  

Code must respect this separation.


## 13. Anti-Patterns

Agents must avoid:

• fat routers  
• business logic in dependencies  
• cross-domain imports when unnecessary  
• blocking IO in async code  
• global utility dumping


## 14. Code Quality

Agents should generate code that is:

• modular  
• testable  
• readable  
• type-safe  

Prefer explicit typing.

Avoid hidden side effects.