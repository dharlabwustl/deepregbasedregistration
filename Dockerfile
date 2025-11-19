
##FROM tensorflow/tensorflow:2.3.1-gpu
#FROM nvcr.io/nvidia/tensorflow:23.06-tf2-py3
#
## install miniconda
#ENV CONDA_DIR=/root/miniconda3
#ENV PATH=${CONDA_DIR}/bin:${PATH}
#ARG PATH=${CONDA_DIR}/bin:${PATH}
#RUN apt-get update
#RUN apt-get install -y wget git && rm -rf /var/lib/apt/lists/*
#RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub && \
#    apt-get update
#
#RUN wget \
#    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#    && mkdir /root/.conda \
#    && bash Miniconda3-latest-Linux-x86_64.sh -b \
#    && rm -f Miniconda3-latest-Linux-x86_64.sh
#
## directory for following operations
#WORKDIR /app
#
## clone DeepReg
#RUN git clone https://github.com/DeepRegNet/DeepReg.git
#WORKDIR DeepReg
#RUN git pull
#
## install conda env
#RUN conda env create -f environment.yml \
#    && conda init bash \
#    && echo "conda activate deepreg" >> /root/.bashrc
#
## install deepreg
#ENV CONDA_PIP="${CONDA_DIR}/envs/deepreg/bin/pip"
#RUN ${CONDA_PIP} install -e .


# Base image with PyTorch + CUDA (PyTorch 2.0.1, CUDA 11.8)
#FROM nvcr.io/nvidia/pytorch:23.06-py3
FROM nvcr.io/nvidia/tensorflow:23.06-tf2-py3

# Set working directory
WORKDIR /workspace/deepreg
COPY DeepReg/ /workspace/deepreg/DeepReg
# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
#RUN #pip install deepreg #[all]
# Upgrade pip
RUN pip install --upgrade pip
RUN mkdir -p /callfromgithub
RUN chmod 755 /callfromgithub
RUN chmod 755 /workspace/deepreg/DeepReg
COPY downloadcodefromgithub.sh /callfromgithub/
RUN chmod +x /callfromgithub/downloadcodefromgithub.sh
RUN mkdir -p /workspace/deepreg/DeepReg/demos/classical_mr_prostate_nonrigid/dataset
RUN chmod 755 /workspace/deepreg/DeepReg/demos/classical_mr_prostate_nonrigid/dataset
RUN apt-get update && apt-get install -y  \
  dcm2niix  \
  vim  \
  zip  \
  unzip  \
  curl  \
  git \
  tree
RUN pip3 install \
  nibabel  \
  numpy  \
  xmltodict  \
  pandas  \
  requests  \
  pydicom  \
  python-gdcm  \
  glob2  \
  scipy  \
  pypng  \
  PyGithub \
  SimpleITK \
  h5py \
  webcolors \
  antspyx \
  SQLAlchemy \
  mysql-connector-python==8.0.27
RUN export NVIDIA_VISIBLE_DEVICES=all
ENV REDCAP_API='36F3BA05DE0507BEBDFB94CC5DA13F93'
ENV GOOGLE_MYSQL_DB_IP='34.58.59.235'
ENV GOOGLE_MYSQL_DB_PASS='dharlabwustl1!'



# Install DeepReg and dependencies (including TensorFlow, PyTorch is already in base)


# Optionally clone the repo (if you plan to modify code or access examples)
#RUN git clone https://github.com/DeepRegNet/DeepReg.git && \
#    cd DeepReg && pip install -e .

# Default command - open bash
CMD ["/bin/bash"]

