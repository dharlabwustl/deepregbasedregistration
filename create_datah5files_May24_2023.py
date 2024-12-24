#!/usr/bin/env python
# coding: utf-8
import numpy as np
import nibabel as nib 
import os,glob,subprocess,sys
import h5py
def gray2binary(filename_template):
#     filename_template='/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/brain/scct_strippedResampled1.nii.gz'
    I=nib.load(filename_template) 
    I_data=I.get_fdata()
    min_val=0 #np.min(I_data)
    print(min_val)
    I_data[I_data>0.9]=1
    I_data[I_data<=0.9]=0
    array_mask = nib.Nifti1Image(I_data, affine=I.affine, header=I.header)
    niigzfilenametosave2=filename_template.split('.nii')[0]+ '_BET.nii.gz' #os.path.join(OUTPUT_DIRECTORY,os.path.basename(levelset_file)) #.split(".nii")[0]+"RESIZED.nii.gz")
    nib.save(array_mask, niigzfilenametosave2)
    return niigzfilenametosave2
def createh5file(image0_file,image1_file,label0_file,label1_file,output_dir="./"):
    image0=nib.load(image0_file).get_fdata() #'/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_images/case_001.nii.gz').get_fdata()
    image0 = (image0 - np.min(image0)) / (np.max(image0) - np.min(image0))

    ## import gray 1
    image1=nib.load(image1_file).get_fdata() #nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_images/case_009.nii.gz').get_fdata()
    image1 = (image1 - np.min(image0)) / (np.max(image1) - np.min(image1))
# import label 0
    label0=nib.load(label0_file).get_fdata() # nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_labels/case_001.nii.gz').get_fdata()
    # import label 1
    label1=nib.load(label1_file).get_fdata() #nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_labels/case_009.nii.gz').get_fdata()
    h5filename=os.path.join(output_dir,os.path.basename(image1_file).split('.nii')[0] + '_h5data.h5')
    print("{}:{}".format('h5filename',h5filename))
    hf = h5py.File(h5filename, 'w')
    hf.create_dataset('image0',data=image0,dtype='i2') ##dtype='i2') # moving image
    hf.create_dataset('image1',data=image1,dtype='i2') ##dtype='i2') # fixed image
    hf.create_dataset('label0',data=label0,dtype='i') # moving mask
    hf.create_dataset('label1',data=label1,dtype='i') # fixed mask


# # In[18]:


# ########################################## GENERATE MASKS FOR THE TRANSFORMED TEMPLATE###############################################
# # template_T_OUTPUT_dir='/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/DATA/COLESIUM_SAMPLEDATA/workingoutput' ##'/storage1/fs1/dharr/Active/ATUL/PROJECTS/NWU/DATA/LVO/output_directoryAugust192021/OUTPUT_42_82/TEMPLATE_TRANS_OUTPUT'
# # for filename in glob.glob(os.path.join(template_T_OUTPUT_dir,'*.nii.gz')):
# #     gray2binary(filename)
# #     print(filename)
# #     x=1


# # In[19]:


# BET_GRAY_DIRECTORY='/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/DATA/COLESIUM_SAMPLEDATA/workingoutput' ##'/storage1/fs1/dharr/Active/ATUL/PROJECTS/NWU/DATA/LVO/output_directoryAugust192021/OUTPUT_42_82/BET_OUTPUT'
# BET_BINARY_DIRECTORY='/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/DATA/COLESIUM_SAMPLEDATA/workingoutput' ##'/storage1/fs1/dharr/Active/ATUL/PROJECTS/NWU/DATA/LVO/output_directoryAugust192021/betmask'
# template_T_OUTPUT_dir='/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/DATA/COLESIUM_SAMPLEDATA/workingoutput' ##'/storage1/fs1/dharr/Active/ATUL/PROJECTS/NWU/DATA/LVO/output_directoryAugust192021/OUTPUT_42_82/TEMPLATE_TRANS_OUTPUT'
# h5data_output_dir='/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/demos/classical_mr_prostate_nonrigid/dataset'
# for filename in glob.glob(os.path.join(template_T_OUTPUT_dir,'*_brain_fscct_strippedResampled1lin1_1.nii.gz')): #'*_BET.nii.gz')):
#     template_gray_file=filename #filename.split('_brain_fscct_strippedResampled1lin1_1.nii.gz')[0]+'_brain_f.nii.gz' #('_BET')[0]+'.nii.gz'
#     print(template_gray_file)
#     template_bet_file=gray2binary(template_gray_file)
#     grayfilebase=os.path.basename(filename).split('_brain_fscct_strippedResampled1lin1_1')[0]+'_brain_f.nii.gz'
#     grayfilename=os.path.join(BET_GRAY_DIRECTORY,grayfilebase)
#     print(grayfilename)
#     betfile_base=os.path.basename(filename).split('_brain_fscct_strippedResampled1lin1_1')[0]+'_bet.nii.gz'
#     betfilename=os.path.join(BET_BINARY_DIRECTORY,betfile_base)
# #     command ="cp " + betfilename + "  " + h5data_output_dir
# #     subprocess.call(command,shell=True)
# #     command ="cp " + betfilename + "  " + h5data_output_dir
# #     subprocess.call(command,shell=True)
# #     print(betfilename)
#     if os.path.exists(template_gray_file) and os.path.exists(template_bet_file) and os.path.exists(grayfilename) and os.path.exists(betfilename): # and os.path.exists(betfilename):
#         print("ALL EXIST")
#         createh5file(template_gray_file,template_bet_file,grayfilename,betfilename,output_dir=h5data_output_dir)
# #         x=1
        


# # In[1]:


## import gray 0
image0_file=sys.argv[1] ## template file after linear registration '/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/DATA/COLESIUM_SAMPLEDATA/workingoutput/scct_strippedResampled1SAH_10_02092014_1114_1_resaved_levelset_brain_f.nii.gz' #'/storage1/fs1/dharr/Active/ATUL/PROJECTS/SAH/SOFTWARE/REGISTRATION_APPROACH/scct_strippedResampled1.nii.gz'
gray2binary(image0_file)
image1_file=sys.argv[2] # target file that is the original nifti file '/storage1/fs1/dharr/Active/ATUL/PROJECTS/DeepReg/DATA/COLESIUM_SAMPLEDATA/workingoutput/SAH_10_02092014_1114_1_resaved_levelset_brain_f.nii.gz' ##'/storage1/fs1/dharr/Active/ATUL/PROJECTS/NWU/DATA/LVO/output_directoryAugust192021/OUTPUT_42_82/LINEAR_REGISTRATION_OUTPUT/BJH_025_08312019_1743_Head_Spiral_3.0_J40s_2_2_levelset_brain_fscct_strippedResampled1lin1.nii.gz'
gray2binary(image1_file)
label0_file=image0_file.split('.nii')[0]+ '_BET.nii.gz'
print(label0_file)
label1_file=image1_file.split('.nii')[0]+ '_BET.nii.gz'
print(label1_file)
image0=nib.load(image0_file).get_fdata() #'/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_images/case_001.nii.gz').get_fdata()

## import gray 1
image1=nib.load(image1_file).get_fdata() #nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_images/case_009.nii.gz').get_fdata()
# import label 0
label0=nib.load(label0_file).get_fdata() # nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_labels/case_001.nii.gz').get_fdata()
# import label 1
label1=nib.load(label1_file).get_fdata() #nib.load('/home/atul/Documents/DEEPREG/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/fixed_labels/case_009.nii.gz').get_fdata()

hf = h5py.File('data.h5', 'w')
hf.create_dataset('image0',data=image0,dtype='i2')
hf.create_dataset('image1',data=image1,dtype='i2')
hf.create_dataset('label0',data=label0,dtype='i')
hf.create_dataset('label1',data=label1,dtype='i')


# In[2]:


# ventricle_mask_file='/storage1/fs1/dharr/Active/ATUL/PROJECTS/SAH/SOFTWARE/REGISTRATION_APPROACH/scct_strippedResampled1_onlyventricle.nii.gz'
# gray2binary(ventricle_mask_file)


# In[ ]:



