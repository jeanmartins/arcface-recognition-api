import pickle
from fastapi import APIRouter,UploadFile, File,Form
import app.services.recognition_service as recognition_service
import shutil
import os
import uuid

router = APIRouter()
    
@router.post("/recognize")
async def recognize(file: UploadFile = File(...), k: int = Form(1), adicionarImgAoDb: bool = Form(False)):
    nome_arquivo = f"{uuid.uuid4().hex}.jpg"
    temp_path = os.path.join("app/db/testes", nome_arquivo)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    response = recognition_service.recognize_face(nome_arquivo,k,adicionarImgAoDb)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return response

@router.get("/info")
def get_info():
    try:
        with open("app/db/nomes.pkl", "rb") as f:
            nomes = pickle.load(f)
        return {
            "status": "success",
            "data": {
                "quantidade_rostos": len(nomes)
            }
        }
    except FileNotFoundError:
        return {
            "status": "failure",
            "message": "Arquivo de nomes não encontrado.",
            "data": {
                "quantidade_rostos": 0
            }
        }