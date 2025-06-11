FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências do sistema e ferramentas necessárias
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3.10-dev \
    build-essential \
    libgl1-mesa-glx libglib2.0-0 git ca-certificates \
    wget unzip \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Alinha aliases padrão de python e pip
RUN ln -sf /usr/bin/python3.10 /usr/bin/python && ln -sf /usr/bin/pip3 /usr/bin/pip

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements_gpu.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements_gpu.txt

# Baixa e prepara o modelo buffalo_l apenas uma vez na build
RUN mkdir -p /root/.insightface/models/buffalo_l && \
    wget -O /root/.insightface/models/buffalo_l.zip https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip && \
    unzip /root/.insightface/models/buffalo_l.zip -d /root/.insightface/models/buffalo_l/ && \
    rm /root/.insightface/models/buffalo_l.zip

# Copia código da aplicação
COPY . .

# Expõe porta do serviço
EXPOSE 8000

# Comando de inicialização do serviço
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
