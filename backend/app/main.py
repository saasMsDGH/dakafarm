from fastapi import FastAPI,Depends
from app.api import router as api
from app.core import seed_role
from app.auth import loginroute,auth
from app.api.v1.user.models import Users




app = FastAPI()

app.include_router(api.router)
app.include_router(seed_role.router)
app.include_router(loginroute.router)






@app.get("/")
def test(current_user:Users=Depends(auth.get_current_user)):
    return "heloo world"
