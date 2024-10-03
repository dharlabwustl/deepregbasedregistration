import nibabel as nib
import os,subprocess,sys,glob
import numpy as np
import argparse
import os
import shutil

import h5py
import tensorflow as tf

import deepreg.model.layer as layer
import deepreg.util as util
from deepreg.registry import REGISTRY
# ## load ddf file
FILE_PATH_DDF='/workingoutput/ddf.nii.gz' #'/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/demos/classical_mr_prostate_nonrigid/logs_reg/ddf.nii.gz'
import nibabel as nib
DDF_data=nib.load(FILE_PATH_DDF).get_fdata()
fixed_image_file='/workingoutput/fixed_image.nii.gz' #'/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/demos/classical_mr_prostate_nonrigid/logs_reg/fixed_image.nii.gz'
fixed_image=nib.load(fixed_image_file).get_fdata()
fixed_image=tf.cast(tf.expand_dims(fixed_image, axis=0), dtype=tf.float32)
warping = layer.Warping(fixed_image_size=fixed_image.shape[1:4])
# fid = h5py.File(FILE_PATH, "r")
var_ddf = tf.cast(tf.expand_dims(DDF_data, axis=0), dtype=tf.float32)
# fixed_image = tf.cast(tf.expand_dims(fid["image1"], axis=0), dtype=tf.float32)
# ## load template_ventricle_mask_file
ventricle_mask_file=sys.argv[1] #'/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/DATA/COLESIUM_SAMPLEDATA/workingoutput/SAH_10_02092014_1114_1_resaved_levelset_brain_fscct_strippedResampled1_onlyventricle_lin1_1.nii.gz'

# .nii.gz'/storage1/fs1/dharr/Active/ATUL/PROJECTS/SAH/SOFTWARE/REGISTRATION_APPROACH/scct_strippedResampled1_onlyventricle_BW.nii.gz' 
#'/storage1/fs1/dharr/Active/ATUL/PROJECTS/SAH/SOFTWARE/REGISTRATION_APPROACH/scct_strippedResampled1_onlyventricle_BET.nii.gz'
# '/storage1/fs1/dharr/Active/ATUL/PROJECTS/SAH/SOFTWARE/REGISTRATION_APPROACH/scct_strippedResampled1_ventricleVolume.nii.gz'
ventricle_mask_data=nib.load(ventricle_mask_file).get_fdata()
moving_image = tf.cast(tf.expand_dims(ventricle_mask_data, axis=0), dtype=tf.float32)
# ## warp template_ventricle_mask_file
# ## save warped_template_ventricle_mask_file
# moving_image = tf.cast(tf.expand_dims(fid["image0"], axis=0), dtype=tf.float32)
warped_moving_image = warping(inputs=[var_ddf, moving_image])
print(type(warped_moving_image))
# warped_moving_image[warped_moving_image<0.9]=0
print('warped_moving_image {}'.format(warped_moving_image.shape))
SAVE_PATH=sys.argv[2] #'/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/demos/classical_mr_prostate_nonrigid/logs_reg'
arr_name='warped_' + os.path.basename(ventricle_mask_file).split(".nii")[0] #scct_strippedResampled1_onlyventricle.nii.gz'
util.save_array(
    save_dir=SAVE_PATH, arr=tf.squeeze(warped_moving_image), name=arr_name, normalize=True, save_png=False
)
warped_image=nib.load(os.path.join(SAVE_PATH,'warped_'+ os.path.basename(ventricle_mask_file)))
warped_image_data=warped_image.get_fdata()
warped_image_data[warped_image_data<=0.5]=0
warped_image_data[warped_image_data>0.5]=1
arr_name='warped_1_' + os.path.basename(ventricle_mask_file).split(".nii")[0] #scct_strippedResampled1_onlyventricle.nii.gz'
util.save_array(
    save_dir=SAVE_PATH, arr=tf.squeeze(warped_image_data), name=arr_name, normalize=True, save_png=False
)
print(warped_image.get_fdata().shape)
print(os.path.join(SAVE_PATH,arr_name))