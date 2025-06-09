from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.router import router
import app.db.init_db as db

db.initDb()
app = FastAPI()
app.include_router(router)
app.mount("/images", StaticFiles(directory="app/db/"), name="images")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


