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
RUN mkdir -p /callfromgithub
RUN chmod 755 /callfromgithub
COPY downloadcodefromgithub.sh /callfromgithub/
RUN chmod +x /callfromgithub/downloadcodefromgithub.sh
RUN mkdir -p /rapids/notebooks/DeepReg/demos/classical_mr_prostate_nonrigid/dataset
RUN chmod 755 /rapids/notebooks/DeepReg/demos/classical_mr_prostate_nonrigid/dataset
RUN apt-get update && apt-get install -y \
  dcm2niix  \
  vim  \
  zip  \
  unzip  \
  curl  \
  git \
  tree
RUN pip install \
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

ENV REDCAP_API='36F3BA05DE0507BEBDFB94CC5DA13F93'
ENV GOOGLE_MYSQL_DB_IP='34.58.59.235'
ENV GOOGLE_MYSQL_DB_PASS='dharlabwustl1!'

CMD ["/bin/bash"]

