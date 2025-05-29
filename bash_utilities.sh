#working_dir=/workinginput/
get_scan_id(){
    local sessionid=${1}
    call_download_files_in_a_resource_in_a_session_arguments=('call_download_files_in_a_resource_in_a_session' ${sessionid} "NIFTI_LOCATION" ${working_dir})
    outputfiles_present=$(/opt/conda/envs/deepreg/bin/python3 download_with_session_ID.py "${call_download_files_in_a_resource_in_a_session_arguments[@]}")

    # Get CSV file
    shopt -s nullglob
    files=("${working_dir}"/*_NIFTILOCATION.csv)
    csv_file="${files[0]}"

#    csv_file=$(ls ${working_dir}/*_NIFTILOCATION.csv)

    # Extract scan ID (assuming column "ID")
    column_name="ID"
    col_index=$(awk -F',' -v colname="$column_name" '
        NR == 1 {
            for (i = 1; i <= NF; i++) {
                if ($i == colname) {
                    print i
                    break
                }
            }
        }' "$csv_file")

    scan_id=$(awk -F',' -v col="$col_index" 'NR > 1 { print $col; exit }' "$csv_file")

    echo "$scan_id"  # ✅ This line makes the function return the value
}

download_resource_dir(){
  local sessionID=${1}
  local scanID=${2}
  local resource_dir=${3}
  curl -u "$XNAT_USER:$XNAT_PASS" -X GET \
    "${XNAT_HOST}/data/experiments/${sessionID}/scans/${scanID}/resources/${resource_dir}/files?format=zip" \
    -o "${working_dir}/${sessionID}_${scanID}_${resource_dir}.zip"
  cd ${working_dir}
  unzip *.zip
  rm *.zip
  mv $(find ./ -name ${resource_dir}) ./
  cd ${resource_dir}
  mv files/* ./
  rm -r files

}
delete_a_file(){
    local sessionID=${1}
    local scanID=${2}
    local snipr_output_foldername=${3}
    local substring=${4}
#        snipr_output_foldername='PREPROCESS_SEGM'
        function_with_arguments=('call_delete_file_with_ext' ${sessionID} ${scanID} ${snipr_output_foldername} ${substring} ) ##'warped_1_mov_mri_region_' )
        echo "outputfiles_present="'$(/opt/conda/envs/deepreg/bin/python3 utilities_simple_trimmed.py' "${function_with_arguments[@]}"

}
to_original_nifti_rf(){
  local original_ct_file=${1}
  local levelset_infarct_mask_file=${2}
  local output_directory=${3}

  /opt/conda/envs/deepreg/bin/python3 -c "
import sys
sys.path.append('/software/')
from utilities_simple_trimmed import levelset2originalRF_new_flip_py
levelset2originalRF_new_flip_py(sys.argv[1], sys.argv[2], sys.argv[3])
" "$original_ct_file" "$levelset_infarct_mask_file" "$output_directory"

echo "_parsehere_${output_directory}/$(basename ${levelset_infarct_mask_file})"

}

to_betgray_given_gray_n_binary(){
  local original_ct_file=${1}
  local levelset_infarct_mask_file=${2}
  local output_directory=${3}

  /opt/conda/envs/deepreg/bin/python3 -c "
import sys
sys.path.append('/software/')
from utilities_simple_trimmed import betgrayfrombetbinary1_py
betgrayfrombetbinary1_py(sys.argv[1], sys.argv[2], sys.argv[3])
" "$original_ct_file" "$levelset_infarct_mask_file" "$output_directory"

echo "_parsehere_${output_directory}/$(basename ${original_ct_file%.nii*}_brain_f.nii.gz)"
}

transform_files_with_given_mat_wrt_sccttemplate(){
  local moving_img=${1}
  local transformed_output_file=${2}
  local transform_mat_file=${3}
  local static_image=/software/scct_strippedResampled1.nii.gz
#  /usr/lib/fsl/5.0/flirt  -in "${img}" -ref "${template_image}"  -dof 12 -out "${output_filename}${exten}lin1" -omat ${output_filename}_${exten}lin1.mat
/usr/lib/fsl/5.0/flirt -in ${moving_img%.nii*} -ref ${static_image%.nii*} -out ${transformed_output_file} -init ${transform_mat_file} -applyxfm


#echo "_parsehere_"

}

uploadsinglefile(){
local sessionID=${1}
local scanID=${2}
local mask_binary_output_dir=${3}
local snipr_output_foldername=${4}
local mask_binary_output_filename=${5}

echo ${mask_binary_output_dir}/${mask_binary_output_filename}
/opt/conda/envs/deepreg/bin/python3 -c "
import sys
sys.path.append('/software');
from download_with_session_ID import *;
uploadsinglefile()" ${sessionID} ${scanID} ${mask_binary_output_dir} ${snipr_output_foldername} ${mask_binary_output_filename}
}

copy_nifti_parameters(){
local  file=${1}
local file1=${2}
local output_directoryname=${3} #  sys.argv[2]
/opt/conda/envs/deepreg/bin/python3 -c "
import sys
sys.path.append('/software');
from utilities_simple_trimmed import *;
copy_nifti_parameters_py(sys.argv[1], sys.argv[2], sys.argv[3])" ${file} ${file1} ${output_directoryname}
}

 mask_area_from_gray(){
   echo " AM AT mask_area_from_gray"
 local  grayscaleimagefile=${1}
 local maskfilename=${2}
 local outputfilename=${3} #  sys.argv[2] (grayscaleimagefile,maskfilename,outputfilename)
#  /opt/conda/envs/deepreg/bin/python3 -c "
# import sys
# sys.path.append('/software');
# from utilities_simple_trimmed import *;
# mask_area_from_gray(sys.argv[1], sys.argv[2], sys.argv[3])" ${grayscaleimagefile} ${maskfilename} ${outputfilename}
#  # rm -r /ZIPFILEDIR/*
#  sessionID=${1}
#  scanID=${2}
#  resource_dirname=${3} #str(sys.argv[4])
#  output_dirname=${4}   #str(sys.argv[3])
#  echo output_dirname::${output_dirname}
  /opt/conda/envs/deepreg/bin/python3 -c "
import sys
sys.path.append('/software');
from utilities_simple_trimmed import *;
mask_area_from_gray(sys.argv[1], sys.argv[2], sys.argv[3])" ${grayscaleimagefile} ${maskfilename} ${outputfilename}
}

save_grayscale_slices_with_ventricles(){
local  grayscaleimagefile=${1}
local maskfilename=${2}
local outputfilename=${3} #  sys.argv[2]
  /opt/conda/envs/deepreg/bin/python3 -c "
import sys
sys.path.append('/software');
from utilities_simple_trimmed import *;
save_grayscale_slices_with_ventricles(sys.argv[1], sys.argv[2], sys.argv[3])" ${grayscaleimagefile} ${maskfilename} ${outputfilename}
}


