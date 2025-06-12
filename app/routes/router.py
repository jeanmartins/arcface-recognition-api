from fastapi import APIRouter,UploadFile, File,Form
import app.services.recognition_service as recognition_service
import shutil
import os

router = APIRouter()
    
@router.post("/recognize")
async def recognize(file: UploadFile = File(...), k: int = Form(1), adicionarImgAoDb: bool = Form(False)):
    temp_path = os.path.join("app/db/testes", "temp.jpg")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    nomes = recognition_service.recognize_face(k,adicionarImgAoDb)

    return nomes