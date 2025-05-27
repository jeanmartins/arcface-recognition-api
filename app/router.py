from fastapi import APIRouter,UploadFile, File
from fastapi.responses import HTMLResponse
import app.recognition as recognition
import app.init_db as db
import shutil
import os

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def read_root():
    with open("frontend/index.html",encoding="utf-8") as f:
        return f.read()
    
@router.post("/recognize")
def recognize(file: UploadFile = File(...)):
    temp_path = os.path.join("app/db/testes", "temp.jpg")

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        return recognition.recognize_face()