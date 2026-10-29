from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import router as api
from app.core import seed_role
from app.auth import loginroute, auth
from app.api.v1.user.models import Users
from sqlalchemy import text
from app.core.database import engine
from fastapi.responses import PlainTextResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.include_router(seed_role.router)
app.include_router(loginroute.router)


@app.get('/healthz', include_in_schema=False, response_class=PlainTextResponse)
async def healthz():
    try:
        async with engine.connect() as connection:
            await connection.execute(text('SELECT 1'))
        return PlainTextResponse('ok\n')
    except Exception:
        return PlainTextResponse('unavailable\n', status_code=503)






@app.get("/")
def test(current_user:Users=Depends(auth.get_current_user)):
    return "heloo world"
