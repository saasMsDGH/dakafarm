from fastapi import FastAPI
from app.api import router as api



app = FastAPI()

app.include_router(api.router)





@app.get("/")
def test():
    return "heloo world"
