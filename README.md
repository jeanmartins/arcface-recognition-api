## Setup

After installing [Conda](https://docs.conda.io/en/latest/miniconda.html), run the following commands in the root of the project:

```bash
conda create -n facial-rec-env python=3.10 -y
conda activate facial-rec-env

pip install -r requirements.txt
fastapi dev app/main.py

```

Running on GPU (optional)
To enable GPU support, make sure your system has an NVIDIA GPU and the required drivers/libraries installed:

1. Install the CUDA Toolkit:
https://developer.nvidia.com/cuda-downloads

Recommended version: CUDA 12.x

2. Install cuDNN (Deep Neural Network library):
https://developer.nvidia.com/rdp/cudnn-download


Running on Docker (optional):

docker build -t arcface-api .

docker run --gpus all -p 8000:8000 arcface-api

