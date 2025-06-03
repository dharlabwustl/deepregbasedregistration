# Base image with PyTorch + CUDA (PyTorch 2.0.1, CUDA 11.8)
FROM nvcr.io/nvidia/pytorch:23.06-py3

# Set working directory
WORKDIR /workspace/deepreg

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install DeepReg and dependencies (including TensorFlow, PyTorch is already in base)
#RUN pip install deepreg[all]

# Optionally clone the repo (if you plan to modify code or access examples)
#RUN git clone https://github.com/DeepRegNet/DeepReg.git && \
    #cd DeepReg && pip install -e .

# Default command - open bash
CMD ["/bin/bash"]

