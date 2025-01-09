import nibabel as nib
import os,subprocess,sys,glob
import numpy as np
import argparse
import os
import shutil
import pandas as pd
import h5py
import tensorflow as tf

import deepreg.model.layer as layer
import deepreg.util as util
from deepreg.registry import REGISTRY
from numpy.lib.shape_base import expand_dims

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
# warped_moving_image = warping(inputs=[var_ddf, moving_image])
# Apply warping with nearest-neighbor interpolation
warped_moving_image = warping([var_ddf, moving_image], interp_method="nearest")
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
threshold_for_probability=0.5
warped_image_data[warped_image_data<=threshold_for_probability]=0
warped_image_data[warped_image_data>threshold_for_probability]=1 ##+ str(threshold_for_probability).replace('.','thresh_')
arr_name='warped_1_' +os.path.basename(ventricle_mask_file).split(".nii")[0] #scct_strippedResampled1_onlyventricle.nii.gz'
util.save_array(
    save_dir=SAVE_PATH, arr=tf.squeeze(warped_image_data), name=arr_name, normalize=True, save_png=False
)
print(warped_image.get_fdata().shape)
print(os.path.join(SAVE_PATH,arr_name))

## find top and botton slice and write into csv file:

sessionID=sys.argv[3]
scanID=sys.argv[4]
original_nifti_filename=sys.argv[5]


ventricle_mask=nib.load(os.path.join(SAVE_PATH,arr_name+".nii.gz")).get_fdata()
try:
    non_zero_slice_num=[]
    # print(ventricle_mask.get_fdata().shape[2])
    for slice_num in range(ventricle_mask.shape[2]):
        this_slice_sum=np.sum(ventricle_mask[:,:,slice_num])
        if this_slice_sum >0 :
            # print(this_slice_sum)
            non_zero_slice_num.append(slice_num)
    if len(non_zero_slice_num)>0:
        upper_lower_limit_vent=[sessionID,scanID,original_nifti_filename,min(non_zero_slice_num),max(non_zero_slice_num)]
    print(upper_lower_limit_vent)
    upper_lower_limit_vent_df=pd.DataFrame(upper_lower_limit_vent).T
    upper_lower_limit_vent_df.columns=['SESSION_ID','SCAN_ID','NIFTI_FILENAME','LOWER_SLICE_NUM','UPPER_SCLICE_NUM']
    print(upper_lower_limit_vent_df)
    upper_lower_limit_vent_df.to_csv(os.path.join(SAVE_PATH,original_nifti_filename.split('.nii')[0]+'_ventricle_bounds.csv'),index=False)
except:

    print(" YOU DID NOT GIVE THE PROPER MASK!")
    pass

