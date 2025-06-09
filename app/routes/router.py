from fastapi import APIRouter,UploadFile, File
from fastapi.responses import HTMLResponse
import app.services.recognition_service as recognition_service
import app.db.init_db as db
import shutil
import os

router = APIRouter()
    
@router.post("/recognize")
def recognize(file: UploadFile = File(...)):
    temp_path = os.path.join("app/db/testes", "temp.jpg")

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        return recognition_service.recognize_face()