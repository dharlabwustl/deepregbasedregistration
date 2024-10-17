#!/usr/bin/env bash
templatefilename=scct_strippedResampled1.nii.gz 
mask_on_template=midlinecssfResampled1.nii.gz
template_ventricle_filename=scct_strippedResampled1_onlyventricle.nii.gz
intensity=0.01
filename=$1 
echo " I AM WORKING IN DOCKER"
output_directory=$(dirname ${filename})
input_directory=${output_directory} #/output # /BET_OUTPUT 
output_directory=${output_directory} ###/output #/LINEAR_REGISTRATION_OUTPUT  
echo " I am in LINEAR_REGISTRATION"
# mkdir -p $output_directory
template_directory=/templatenifti
template_ventricle_directory=/templateventricle
template_file_name=$templatefilename
# x=$input_directory/$1 

echo $filename
template_image=$template_directory/$template_file_name
template_image_ventricle=$template_ventricle_directory/$template_ventricle_filename
template_basename="$(basename -- $template_image)"
exten="${template_basename%%.nii*}"
echo $template_basename 
img=$(/usr/lib/fsl/5.0/remove_ext $filename)
img_basename=$(basename -- $img)
output_filename=$output_directory/$img_basename
echo $output_filename
/usr/lib/fsl/5.0/flirt -in ${img} -ref ${template_image} -out "${output_filename}${exten}lin1" -init ${output_filename}_${exten}lin1.mat  -applyxfm
#/usr/lib/fsl/5.0/flirt  -in "${img}" -ref "${template_image}"  -dof 12 -out "${output_filename}${exten}lin1" -omat ${output_filename}_${exten}lin1.mat

/usr/lib/fsl/5.0/flirt -in ${template_image} -ref ${img} -out "${output_filename}${exten}lin1_1" -init ${output_filename}_${exten}lin1_1.mat  -applyxfm

/usr/lib/fsl/5.0/flirt -in ${template_image_ventricle} -ref ${img} -out "${output_filename}${exten}_onlyventricle_lin1_1" -init ${output_filename}_${exten}lin1_1.mat  -applyxfm
#/usr/lib/fsl/5.0/flirt -ref  "${img}"  -in "${template_image}"  -dof 12 -out "${output_filename}${exten}lin1_1" -omat ${output_filename}_${exten}lin1_1.mat

echo "IMAGE REGISTERED"
echo "REGISTRATION OUTPUT:""${output_filename}_${exten}lin1.nii.gz"
echo "REGISTRATION OUTPUT:""${output_filename}_${exten}lin1_1.nii.gz"
