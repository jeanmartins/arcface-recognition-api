
import os
import shutil
import uuid
import cv2
import numpy as np
import faiss
import pickle
import time
from filelock import FileLock, Timeout

from app.core.face_analysis import face_app

IMAGEM_PATH = 'app/db/testes/temp.jpg'

def recognize_face(k=1,adicionarImgAoDb=False):
    tick = time.time()
    
    index,nomes = carregar_indices()
    
    if index is None:
        return "Falha ao carregar indíces"
    
    resultadoIndices = reconhecer(index,nomes,k,adicionarImgAoDb)
    tack = time.time()
    print(f"Tempo de execução total : {tack-tick}")

    if resultadoIndices is None:
        return "Pessoa desconhecida"

    result = list()        
    for idx in resultadoIndices:
        result.append(nomes[idx])
    return result

def carregar_indices():
    if os.path.exists("app/db/indice_rostos.index") and os.path.exists("app/db/nomes.pkl"):
        index = faiss.read_index("app/db/indice_rostos.index")
        with open("app/db/nomes.pkl", "rb") as f:
            nomes = pickle.load(f)
        return index,nomes
    return None, None

def reconhecer(index,nomes,k,adicionarImgAoDb=False):
    
    img = carregarImagem()
    
    emb = carregarEmbedding(img)
    
    if emb is None:
        print("Nenhuma face detectada.")
        return None
    
    distances, indices = index.search(emb, k=k)
    
    reconhecidos = []
    for i, dist in enumerate(distances[0]):
        print(f"Match {i+1}: distância = {dist:.4f}, nome = {nomes[indices[0][i]]}")
        if dist <= 1.0:
            reconhecidos.append(indices[0][i])
    
    if not reconhecidos and adicionarImgAoDb:
        adicionar_ao_database_e_index(index,emb)
    
    if not reconhecidos:
        return None
    
    return reconhecidos

def carregarImagem():
    img = cv2.imread(IMAGEM_PATH)
    if img is None:
        print("Erro ao carregar a imagem")
        return None
    return img

def carregarEmbedding(img):
    faces = face_app.get(img)
    if not faces:
        return None

    emb = faces[0].embedding.reshape(1, -1).astype('float32')
    return emb / np.linalg.norm(emb, axis=1, keepdims=True)

def adicionar_ao_database_e_index(index, embedding):
    nome_arquivo = f"{uuid.uuid4().hex}.jpg"
    shutil.copyfile(IMAGEM_PATH, f"app/db/rostos_dataset/{nome_arquivo}")
    try:
        with FileLock("app/db/nomes.lock", timeout=10):
            if os.path.exists("app/db/nomes.pkl"):
                with open("app/db/nomes.pkl", "rb") as f:
                    nomes = pickle.load(f)
            else:
                nomes = []

            nomes.append(nome_arquivo)
            with open("app/db/nomes.pkl", "wb") as f:
                pickle.dump(nomes, f)

        with FileLock("app/db/indice_rostos.index.lock", timeout=10):
            index.add(embedding)
            faiss.write_index(index, "app/db/indice_rostos.index")
    except Timeout:
        print("Falha ao obter lock — recurso ocupado por muito tempo.")