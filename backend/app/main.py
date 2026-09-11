from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api
from app.core import seed_role
from app.auth import loginroute, auth
from app.api.v1.user.models import Users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's a dev environment, we allow all for ease
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.include_router(seed_role.router)
app.include_router(loginroute.router)






@app.get("/")
def test(current_user:Users=Depends(auth.get_current_user)):
    return "heloo world"
