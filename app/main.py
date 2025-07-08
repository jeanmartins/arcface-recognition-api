from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.router import router
import app.db.init_db as db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    db.initDb()


app.include_router(router)


app.mount("/images", StaticFiles(directory="app/db/"), name="images")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
