#!/usr/bin/env bash
moving_image_filename=${1}
fixed_image_filename=${2}
T_output_filename=${3}
output_directory=${4}
output_filename=${output_directory}/'mov_'$(basename ${moving_image_filename%.nii*})_fixed_$(basename  ${fixed_image_filename%.nii*})_lin1
#T_output_filename=${output_filename}.mat
echo "RUNNING:: /usr/lib/fsl/5.0/flirt -in ${moving_image_filename} -ref ${fixed_image_filename} -out "${output_filename}" -init ${T_output_filename}  -applyxfm"
/usr/lib/fsl/5.0/flirt -in ${moving_image_filename} -ref ${fixed_image_filename} -out "${output_filename}" -init ${T_output_filename}  -applyxfm
