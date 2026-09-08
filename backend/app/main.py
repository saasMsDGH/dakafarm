from fastapi import FastAPI
from app.api import router as api
from app.core import seed_role



app = FastAPI()

app.include_router(api.router)
app.include_router(seed_role.router)





@app.get("/")
def test():
    return "heloo world"
