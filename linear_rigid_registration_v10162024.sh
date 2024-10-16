#!/usr/bin/env bash
moving_image_filename=${1}
fixed_image_filename=${2}
output_filename='mov_'${moving_image_filename%.nii*}_fixed_${fixed_image_filename%.nii*}
T_output_filename='mov_'${moving_image_filename%.nii*}_fixed_${fixed_image_filename%.nii*}.mat
/usr/lib/fsl/5.0/flirt  -in "${moving_image_filename}" -ref "${fixed_image_filename}"  -dof 12 -out "${output_filename}" -omat ${T_output_filename}
