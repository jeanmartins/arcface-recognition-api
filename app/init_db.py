
import os
import cv2
import numpy as np
import faiss
import pickle
import time

from app.face_analysis import face_app 

PASTA_REFERENCIAS = 'app/db/rostos_dataset'

def carregar_database(pasta):
    database = {}
    for arquivo in os.listdir(pasta):
        caminho = os.path.join(pasta, arquivo)
        if not arquivo.lower().endswith(('.jpg', '.jpeg', '.png')): 
            continue
        nome = arquivo
        print(nome)
        img = cv2.imread(caminho)
        if img is None:
            print(f"[ERRO] Não foi possível carregar a imagem {arquivo}")
            continue
        
        faces = face_app.get(img)
        if not faces:
            print(f"[AVISO] Nenhum rosto detectado em {arquivo}")
            continue
        emb = faces[0].embedding
        database[nome] = emb
    return database

def criar_index(database):
    nomes = list(database.keys())
    embeddings_referencias = np.array(list(database.values()),'f')
    faiss.normalize_L2(embeddings_referencias)
    
    index = faiss.IndexFlatL2(embeddings_referencias.shape[1])  # L2 = Distância Euclidiana
    index.add(embeddings_referencias)
    
    faiss.write_index(index, "app/db/indice_rostos.index")
    with open("app/db/nomes.pkl", "wb") as f:
        pickle.dump(nomes, f)


def initDb():
    if os.path.exists("app/db/indice_rostos.index") and os.path.exists("app/db/nomes.pkl"):
        print("[INFO] Índices já existentes.")
        return
    
    tick = time.time()
    database = carregar_database(PASTA_REFERENCIAS)
    tack = time.time()
    print(f"Tempo de execução total : {tack-tick}")
    print(f"[INFO] {len(database)} rostos carregados na base.")
    criar_index(database)