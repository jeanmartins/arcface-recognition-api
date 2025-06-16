
import os
import shutil
import cv2
import numpy as np
import faiss
import pickle
import time
from filelock import FileLock, Timeout

from app.core.face_analysis import face_app

IMAGEM_PATH = 'app/db/testes'
DATASET_PATH = 'app/db/rostos_dataset'

def recognize_face(nome_arquivo,k=1,adicionarImgAoDb=False):
    
    if nome_arquivo is None:
        return {"status": "failure", "message": "Nome do arquivo não informado.", "data": []}
    
    tick = time.time()
    
    index,nomes = carregar_indices()
    
    if index is None:
        return {"status": "failure", "message": "Falha ao carregar indíces.", "data": []}
    
    resultadoIndices,messages = reconhecer(nome_arquivo,index,nomes,k,adicionarImgAoDb)
    tack = time.time()
    print(f"Tempo de execução total : {tack-tick}")

    if resultadoIndices is None:
        return {"status": "failure", "message": " ".join(messages), "data": []}

    result = [nomes[idx] for idx in resultadoIndices]

    return {"status": "success", "message": " ".join(messages), "data": result}

def carregar_indices():
    if os.path.exists("app/db/indice_rostos.index") and os.path.exists("app/db/nomes.pkl"):
        index = faiss.read_index("app/db/indice_rostos.index")
        with open("app/db/nomes.pkl", "rb") as f:
            nomes = pickle.load(f)
        return index,nomes
    return None, None

def reconhecer(nome_arquivo,index,nomes,k,adicionarImgAoDb=False):
    msgs = []
    img = carregarImagem(nome_arquivo)
    
    if img is None:
        return None,["Erro ao carregar a imagem."]
    
    emb = carregarEmbedding(img)
    
    if emb is None:
        return None,["Erro ao processar imagem."]
    
    distances, indices = index.search(emb, k=k)
    
    reconhecidos = []
    for i, dist in enumerate(distances[0]):
        print(f"Match {i+1}: distância = {dist:.4f}, nome = {nomes[indices[0][i]]}")
        if dist <= 1.0:
            reconhecidos.append(indices[0][i])
    
    
    if adicionarImgAoDb:
        msg = adicionar_ao_database_e_index(index,emb,nome_arquivo)
        msgs.append(msg)
    
    if not reconhecidos:
        msgs.append("Pessoa não reconhecida.")
        return None,msgs
    
    msgs.append("Pessoa reconhecida.")
    return reconhecidos,msgs

def carregarImagem(nome_arquivo):
    img = cv2.imread(os.path.join(IMAGEM_PATH, nome_arquivo))
    
    if img is None:
        return None
    return img

def carregarEmbedding(img):
    faces = face_app.get(img)
    if not faces:
        return None

    emb = faces[0].embedding.reshape(1, -1).astype('float32')
    return emb / np.linalg.norm(emb, axis=1, keepdims=True)

def adicionar_ao_database_e_index(index, embedding,nome_arquivo):
    shutil.copyfile(os.path.join(IMAGEM_PATH, nome_arquivo), os.path.join(DATASET_PATH, nome_arquivo))
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
            
        return "Foto adicionada ao banco de dados."
    except Timeout:
        print("Falha ao obter lock — recurso ocupado por muito tempo.")
        return "Ocorreu um erro ao adicionar foto ao banco de dados."