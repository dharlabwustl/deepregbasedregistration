FROM sharmaatul11/deepregoct22023.v2
RUN #apt update
#RUN mkdir /templateventricle
#COPY scct_strippedResampled1.nii.gz   /templatenifti/
#COPY  midlinecssfResampled1.nii.gz   /templatemasks/
#COPY scct_strippedResampled1_onlyventricle.nii.gz /templateventricle/
RUN mkdir -p /callfromgithub
RUN chmod 755 /callfromgithub
COPY downloadcodefromgithub.sh /callfromgithub/
RUN chmod +x /callfromgithub/downloadcodefromgithub.sh
RUN mkdir -p /rapids/notebooks/DeepReg/demos/classical_mr_prostate_nonrigid/dataset
RUN apt install -y \
  dcm2niix  \ 
  vim  \ 
  zip  \ 
  unzip  \ 
  curl  \ 
  git \
  tree
RUN /opt/conda/envs/deepreg/bin/pip3 install \
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
  webcolors

