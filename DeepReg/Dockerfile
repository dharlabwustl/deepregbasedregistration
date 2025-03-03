### Use NVIDIA's TensorFlow 2.12 image with CUDA 11.8 and cuDNN 8.6
##FROM nvcr.io/nvidia/rapidsai/base:24.12-cuda12.0-py3.10
#FROM nvcr.io/nvidia/tensorflow:23.12-tf2-py3
## #nvcr.io/nvidia/tensorflow:23.06-tf2-py3
##USER root
##RUN  apt-get -y update
##RUN  apt-get -y install graphviz
#FROM nvcr.io/nvidia/rapidsai/base:24.12-cuda12.0-py3.10
#
## Ensure root user permissions
#USER root
##COPY entrypoint.sh /home/rapids/entrypoint.sh
#RUN chmod +x /home/rapids/entrypoint.sh
#
## Set environment variables
#ENV DEBIAN_FRONTEND=noninteractive \
#    TZ=UTC \
#    LANG=C.UTF-8 \
#    LC_ALL=C.UTF-8
#
## Update APT package manager and install Graphviz
#RUN apt-get update && apt-get install -y graphviz git && apt-get clean
#
## Verify Graphviz installation
#RUN dot -V
FROM nvcr.io/nvidia/rapidsai/notebooks:24.12-cuda12.0-py3.10
USER root
RUN chmod 777 /var/lib/apt/lists/lock

RUN chmod +x /home/rapids/entrypoint.sh

RUN  apt-get -y update
RUN  apt-get -y install graphviz git
ENV CONDA_DIR=/opt/conda
RUN chmod -R 777 /opt/conda
## clone DeepReg
RUN git clone https://github.com/DeepRegNet/DeepReg.git
COPY environment.yml DeepReg/environment.yml
WORKDIR DeepReg
RUN git pull
#### install conda env
RUN conda env create -f environment.yml \
    && conda init bash \
    && echo "conda activate deepreg" >> /root/.bashrc
### install deepreg
ENV CONDA_PIP="${CONDA_DIR}/envs/deepreg/bin/pip"
#RUN ${CONDA_PIP} install -e .
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN /opt/conda/envs/deepreg/bin/pip install opencv-python
RUN mkdir /DEEPREG

###ADD DeepRegForSNIPR /DEEPREG/

RUN mkdir /templateventricle
RUN mkdir /templatenifti
RUN mkdir /templatemasks
COPY scct_strippedResampled1.nii.gz   /templatenifti/
COPY  midlinecssfResampled1.nii.gz   /templatemasks/
COPY scct_strippedResampled1_onlyventricle.nii.gz /templateventricle/
RUN mkdir -p /callfromgithub
RUN chmod 755 /callfromgithub
COPY downloadcodefromgithub.sh /callfromgithub/
RUN chmod +x /callfromgithub/downloadcodefromgithub.sh
RUN apt install -y \
  dcm2niix  \
  vim  \
  zip  \
  unzip  \
  curl  \
  git \
  tree
RUN /opt/conda/envs/deepreg/bin/pip install \
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
  scikit-image \
  matplotlib
ENV REDCAP_API='36F3BA05DE0507BEBDFB94CC5DA13F93'
RUN chmod -R 777 /home/rapids/DeepReg
ENTRYPOINT ["/bin/bash"]
