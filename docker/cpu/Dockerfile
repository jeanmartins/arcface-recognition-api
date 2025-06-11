FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    wget \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/list

WORKDIR /app

COPY requirements_cpu.txt .


RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements_cpu.txt


RUN mkdir -p /root/.insightface/models/buffalo_l && \
    wget -O /root/.insightface/models/buffalo_l.zip https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip && \
    unzip /root/.insightface/models/buffalo_l.zip -d /root/.insightface/models/buffalo_l/ && \
    rm /root/.insightface/models/buffalo_l.zip

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
