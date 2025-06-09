
import os
import cv2
import numpy as np
import faiss
import pickle
import time

from app.core.face_analysis import face_app

IMAGEM_PATH = 'app/db/testes/temp.jpg'

def reconhecer(index):
    
    img = carregarImagem()
    
    emb = carregarEmbedding(img)
    
    distances, indices = index.search(emb, k=3)
    
    print("Distâncias:", distances[0])
    
    reconhecidos = []
    for i, dist in enumerate(distances[0]):
        if dist <= 1.0:
            reconhecidos.append(indices[0][i])

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

def carregar_indices():
    if os.path.exists("app/db/indice_rostos.index") and os.path.exists("app/db/nomes.pkl"):
        index = faiss.read_index("app/db/indice_rostos.index")
        with open("app/db/nomes.pkl", "rb") as f:
            nomes = pickle.load(f)
        return index,nomes
    return None, None

def recognize_face():
    tick = time.time()
    
    index,nomes = carregar_indices()
    
    if index is None:
        return "Falha ao carregar indíces"
    
    resultadoIndices = reconhecer(index)
    tack = time.time()
    print(f"Tempo de execução total : {tack-tick}")

    if resultadoIndices is None:
        return "Pessoa desconhecida"

    result = list()        
    for idx in resultadoIndices:
        result.append(nomes[idx])
    return result
