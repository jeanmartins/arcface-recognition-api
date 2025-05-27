from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.router import router
import app.init_db as db

db.initDb()
app = FastAPI()
app.include_router(router)
app.mount("/images", StaticFiles(directory="app/db/"), name="images")


