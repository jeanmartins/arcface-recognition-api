import os
import cv2
import numpy as np
import faiss
import pickle
import time

from app.core.face_analysis import face_app 

PASTA_BASE = "/app/db"
# PASTA_BASE = r"C:\Users\jean_martins\Desktop\facial-recognition-api\app\db"
PASTA_REFERENCIAS = os.getenv("PASTA_REFERENCIAS", os.path.join(PASTA_BASE, "rostos_dataset"))
PASTA_INDICE = PASTA_BASE+"/index"

def initDb():
    indice_path = os.path.join(PASTA_INDICE, "indice_rostos.index")
    nomes_path = os.path.join(PASTA_INDICE, "nomes.pkl")

    if os.path.exists(indice_path) and os.path.exists(nomes_path):
        print("[INFO] Índices já existentes.")
        return
    
    tick = time.time()

    if os.path.exists(nomes_path):
        with open(nomes_path, "rb") as f:
            caminhos_relativos = pickle.load(f)
        database = carregar_database_por_caminhos(caminhos_relativos)
    else:
        database = carregar_database(PASTA_REFERENCIAS)
    
    tack = time.time()
    print(f"Tempo de execução total : {tack - tick}")
    print(f"[INFO] {len(database)} rostos carregados na base.")
    criar_index(database)

def carregar_database_por_caminhos(caminhos_relativos):
    database = {}
    for caminho_rel in caminhos_relativos:
        caminho_rel = os.path.normpath(caminho_rel)
        caminho_completo = os.path.join(PASTA_BASE, caminho_rel)
        print(f"Carregando imagem: {caminho_completo}")
        img = cv2.imread(caminho_completo)
        if img is None:
            print(f"[ERRO] Não foi possível carregar a imagem {caminho_rel}")
            continue
        
        faces = face_app.get(img)
        if not faces:
            print(f"[AVISO] Nenhum rosto detectado em {caminho_rel}")
            continue
        
        emb = faces[0].embedding
        database[caminho_rel] = emb
    return database

def carregar_database(pasta):
    database = {}
    for root, _, arquivos in os.walk(pasta):  # percorre todas as subpastas
        for arquivo in arquivos:
            if not arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            caminho = os.path.join(root, arquivo)
            caminho_relativo = os.path.relpath(caminho, PASTA_BASE)
            print(f"Carregando imagem: {caminho} (relativo: {caminho_relativo})")

            img = cv2.imread(caminho)
            if img is None:
                print(f"[ERRO] Não foi possível carregar a imagem {arquivo}")
                continue

            faces = face_app.get(img)
            if not faces:
                print(f"[AVISO] Nenhum rosto detectado em {arquivo}")
                continue

            emb = faces[0].embedding
            database[caminho_relativo] = emb
    return database


def criar_index(database):
    nomes = list(database.keys())
    embeddings_referencias = np.array(list(database.values()), 'f')
    faiss.normalize_L2(embeddings_referencias)
    
    index = faiss.IndexFlatL2(embeddings_referencias.shape[1])
    index.add(embeddings_referencias)
    
    indice_path = os.path.join(PASTA_INDICE, "indice_rostos.index")
    nomes_path = os.path.join(PASTA_INDICE, "nomes.pkl")

    
    faiss.write_index(index, indice_path)
    with open(nomes_path, "wb") as f:
        pickle.dump(nomes, f)
