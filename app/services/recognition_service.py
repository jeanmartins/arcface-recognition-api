import os
import shutil
import cv2
import numpy as np
import faiss
import pickle
import time
from filelock import FileLock, Timeout

from app.core.face_analysis import face_app

PASTA_BASE = os.path.abspath("app/db")
PASTA_TESTES = os.path.join(PASTA_BASE, "testes")
PASTA_INDICE = os.path.join(PASTA_BASE, "index")
PASTA_NOVAS_IMAGENS = os.getenv("PASTA_NOVAS_IMAGENS", os.path.join(PASTA_BASE, "novas_imagens"))


def recognize_face(nome_arquivo, k=1, adicionarImgAoDb=False):
    if not nome_arquivo:
        return {"status": "failure", "message": "Nome do arquivo não informado.", "data": []}
    
    tick = time.time()
    
    index, nomes = carregar_indices()
    if index is None:
        return {"status": "failure", "message": "Falha ao carregar índices.", "data": []}
    
    resultado_indices, mensagens = reconhecer(nome_arquivo, index, nomes, k, adicionarImgAoDb)
    tack = time.time()
    print(f"Tempo de execução total: {tack - tick:.2f} segundos")

    if resultado_indices is None:
        return {"status": "failure", "message": " ".join(mensagens), "data": []}

    result = [nomes[idx] for idx in resultado_indices]
    return {"status": "success", "message": " ".join(mensagens), "data": result}


def carregar_indices():
    indice_path = os.path.join(PASTA_INDICE, "indice_rostos.index")
    nomes_path = os.path.join(PASTA_INDICE, "nomes.pkl")
    
    if os.path.exists(indice_path) and os.path.exists(nomes_path):
        index = faiss.read_index(indice_path)
        with open(nomes_path, "rb") as f:
            nomes = pickle.load(f)
        return index, nomes
    
    return None, None


def reconhecer(nome_arquivo, index, nomes, k, adicionarImgAoDb=False):
    mensagens = []

    img = carregar_imagem(nome_arquivo)
    if img is None:
        return None, ["Erro ao carregar a imagem."]
    
    emb = carregar_embedding(img)
    if emb is None:
        return None, ["Erro ao processar a imagem."]
    
    distances, indices = index.search(emb, k=k)

    reconhecidos = []
    for i, dist in enumerate(distances[0]):
        print(f"Match {i+1}: distância = {dist:.4f}, nome = {nomes[indices[0][i]]}")
        if dist <= 1.0:
            reconhecidos.append(indices[0][i])
    
    if adicionarImgAoDb:
        msg = adicionar_ao_database_e_index(index, emb, nome_arquivo)
        mensagens.append(msg)
    
    if not reconhecidos:
        mensagens.append("Pessoa não reconhecida.")
        return None, mensagens
    
    mensagens.append("Pessoa reconhecida.")
    return reconhecidos, mensagens


def carregar_imagem(nome_arquivo):
    caminho = os.path.join(PASTA_TESTES, nome_arquivo)
    if not os.path.exists(caminho):
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return None
    return cv2.imread(caminho)


def carregar_embedding(img):
    faces = face_app.get(img)
    if not faces:
        return None
    emb = faces[0].embedding.reshape(1, -1).astype('float32')
    return emb / np.linalg.norm(emb, axis=1, keepdims=True)


def adicionar_ao_database_e_index(index, embedding, nome_arquivo):
    os.makedirs(PASTA_NOVAS_IMAGENS, exist_ok=True)

    src = os.path.join(PASTA_TESTES, nome_arquivo)
    dst = os.path.join(PASTA_NOVAS_IMAGENS, nome_arquivo)
    shutil.copyfile(src, dst)

    nomes_path = os.path.join(PASTA_INDICE, "nomes.pkl")
    indice_path = os.path.join(PASTA_INDICE, "indice_rostos.index")

    try:
        with FileLock(nomes_path + ".lock", timeout=10):
            nomes = []
            if os.path.exists(nomes_path):
                with open(nomes_path, "rb") as f:
                    nomes = pickle.load(f)

            caminho_relativo = os.path.relpath(dst, PASTA_BASE)
            if caminho_relativo not in nomes:
                nomes.append(caminho_relativo)

            with open(nomes_path, "wb") as f:
                pickle.dump(nomes, f)

        with FileLock(indice_path + ".lock", timeout=10):
            index.add(embedding)
            faiss.write_index(index, indice_path)

        return "Foto adicionada ao banco de dados."
    except Timeout:
        print("Falha ao obter lock — recurso ocupado por muito tempo.")
        return "Erro ao adicionar foto ao banco de dados."
