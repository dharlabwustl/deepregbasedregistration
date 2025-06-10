#!/bin/bash
#export XNAT_USER=${2}
#export XNAT_PASS=${3}
#export XNAT_HOST=${4}
sessionID=${1}
working_dir=/workinginput
working_dir_1=/input1
output_directory=/workingoutput

final_output_directory=/outputinsidedocker

copyoutput_to_snipr() {
  sessionID=$1
  scanID=$2
  resource_dirname=$4 #"MASKS" #sys.argv[4]
  file_suffix=$5
  output_dir=$3
  echo " I AM IN copyoutput_to_snipr "
   python3 -c "
import sys 
sys.path.append('/software');
from download_with_session_ID import *; 
uploadfile()" ${sessionID} ${scanID} ${output_dir} ${resource_dirname} ${file_suffix} # ${infarctfile_present}  ##$static_template_image $new_image $backslicenumber #$single_slice_filename

}
copyoutput_with_prefix_to_snipr() {
  sessionID=$1
  scanID=$2
  resource_dirname=$4 #"MASKS" #sys.argv[4]
  file_suffix=$5
  output_dir=$3
  echo " I AM IN copyoutput_to_snipr "
   python3 -c "
import sys
sys.path.append('/software');
from download_with_session_ID import *;
uploadfile_withprefix()" ${sessionID} ${scanID} ${output_dir} ${resource_dirname} ${file_suffix} # ${infarctfile_present}  ##$static_template_image $new_image $backslicenumber #$single_slice_filename

}


copy_masks_data() {
  echo " I AM IN copy_masks_data "
  # rm -r /ZIPFILEDIR/*
  sessionID=${1}
  scanID=${2}
  resource_dirname=${3} #str(sys.argv[4])
  output_dirname=${4}   #str(sys.argv[3])
  echo output_dirname::${output_dirname}
  python3 -c "
import sys 
sys.path.append('/software');
from download_with_session_ID import *; 
downloadfiletolocaldir()" ${sessionID} ${scanID} ${resource_dirname} ${output_dirname} ### ${infarctfile_present}  ##$static_template_image $new_image $backslicenumber #$single_slice_filename

}

copy_scan_data() {
  echo " I AM IN copy_scan_data "
  # rm -r /ZIPFILEDIR/*
  # rm -r ${working_dir}/*
  # rm -r ${output_dir}/*
  sessionID=$1
  dir_to_receive_the_data=${2}
  resource_dir=${3}
  # sessionId=sys.argv[1]
  # dir_to_receive_the_data=sys.argv[2]
  # resource_dir=sys.argv[3]
  # scanID=$2
  python3 -c "
import sys 
sys.path.append('/Stroke_CT_Processing');
from download_with_session_ID import *; 
get_relevantfile_in_A_DIRECTORY()" ${sessionID} ${dir_to_receive_the_data} ${resource_dir}

}

run_IML_NWU_CSF_CALC() {
  this_filename=${1}
  this_betfilename=${2}
  this_csfmaskfilename=${3}
  this_infarctmaskfilename=${4}
  echo "BET USING LEVELSET MASK"

  /software/bet_withlevelset.sh $this_filename ${this_betfilename} #${output_directory} #Helsinki2000_1019_10132014_1048_Head_2.0_ax_Tilt_1_levelset # ${3} # Helsinki2000_702_12172013_2318_Head_2.0_ax_levelset.nii.gz #${3} # $6 $7 $8 $9 ${10}

#  echo "bet_withlevelset successful" >${output_directory}/success.txt
#  this_filename_brain=${this_filename%.nii*}_brain_f.nii.gz
#  # cp ${this_filename_brain} ${output_directory}/ #  ${final_output_directory}/
#  echo "LINEAR REGISTRATION TO TEMPLATE"
#  /software/linear_rigid_registration.sh ${this_filename_brain} #${templatefilename} #$3 ${6} WUSTL_233_11122015_0840__levelset_brain_f.nii.gz
#  echo "linear_rigid_registration successful" >>${output_directory}/success.txt
#  echo "RUNNING IML FSL PART"
#  /software/ideal_midline_fslpart.sh ${this_filename} # ${templatefilename} ${mask_on_template}  #$9 #${10} #$8
#  echo "ideal_midline_fslpart successful" >>${output_directory}/success.txt
#  echo "RUNNING IML PYTHON PART"
#
#  /software/ideal_midline_pythonpart.sh ${this_filename} #${templatefilename}  #$3 #$8 $9 ${10}
#  echo "ideal_midline_pythonpart successful" >>${output_directory}/success.txt
#
#  echo "RUNNING NWU AND CSF VOLUME CALCULATION "
#
#  /software/nwu_csf_volume.sh ${this_filename} ${this_betfilename} ${this_csfmaskfilename} ${this_infarctmaskfilename} ${lower_threshold} ${upper_threshold}
#  echo "nwu_csf_volume successful" >>${output_directory}/success.txt
#  thisfile_basename=$(basename $this_filename)
#  # for texfile in $(/usr/lib/fsl/5.0/remove_ext ${output_directory}/$thisfile_basename)*.tex ;
#  for texfile in ${output_directory}/*.tex; do
#    pdflatex -halt-on-error -interaction=nonstopmode -output-directory=${output_directory} $texfile ##${output_directory}/$(/usr/lib/fsl/5.0/remove_ext $this_filename)*.tex
#    rm ${output_directory}/*.aux
#    rm ${output_directory}/*.log
#  done

#  for filetocopy in $(/usr/lib/fsl/5.0/remove_ext ${output_directory}/$thisfile_basename)*_brain_f.nii.gz; do
#    cp ${filetocopy} ${final_output_directory}/
#  done
#
#  for filetocopy in $(/usr/lib/fsl/5.0/remove_ext ${output_directory}/$thisfile_basename)*.mat; do
#    cp ${filetocopy} ${final_output_directory}/
#  done
#
#  for filetocopy in ${output_directory}/*.pdf; do
#    cp ${filetocopy} ${final_output_directory}/
#  done
#  for filetocopy in ${output_directory}/*.csv; do
#    cp ${filetocopy} ${final_output_directory}/
#  done

}

nwucalculation_each_scan() {

  eachfile_basename_noext=''
  originalfile_basename=''
  original_ct_file=''
  #  for eachfile in ${working_dir}/*.nii*; do
  for eachfile in ${working_dir_1}/*.nii*; do
    original_ct_file=${eachfile}
    eachfile_basename=$(basename ${eachfile})
    originalfile_basename=${eachfile_basename}
    eachfile_basename_noext=${eachfile_basename%.nii*}

    ############## files basename ##################################
    grayfilename=${eachfile_basename_noext}_resaved_levelset.nii
    if [[ "$eachfile_basename" == *".nii.gz"* ]]; then #"$STR" == *"$SUB"*
      grayfilename=${eachfile_basename_noext}_resaved_levelset.nii.gz
    fi
    betfilename=${eachfile_basename_noext}_resaved_levelset_bet.nii.gz
    csffilename=${eachfile_basename_noext}_resaved_csf_unet.nii.gz
    infarctfilename=${eachfile_basename_noext}_resaved_infarct_auto_removesmall.nii.gz
    ################################################
    ############## copy those files to the docker image ##################################
    cp ${working_dir}/${betfilename} ${output_directory}/
    cp ${working_dir}/${csffilename} ${output_directory}/
    cp ${working_dir}/${infarctfilename} ${output_directory}/
    ####################################################################################
    source /software/bash_functions_forhost.sh

    cp ${original_ct_file} ${output_directory}/${grayfilename}
    grayimage=${output_directory}/${grayfilename} #${gray_output_subdir}/${eachfile_basename_noext}_resaved_levelset.nii
    ###########################################################################

    #### originalfiel: .nii
    #### betfile: *bet.nii.gz

    # original_ct_file=$original_CT_directory_names/
    levelset_infarct_mask_file=${output_directory}/${infarctfilename}
    echo "levelset_infarct_mask_file:${levelset_infarct_mask_file}"
    ## preprocessing infarct mask:
    python3 -c "
import sys ;
sys.path.append('/software/') ;
from utilities_simple_trimmed import * ;  levelset2originalRF_new_flip()" "${original_ct_file}" "${levelset_infarct_mask_file}" "${output_directory}"

    ## preprocessing bet mask:
    levelset_bet_mask_file=${output_directory}/${betfilename}
    echo "levelset_bet_mask_file:${levelset_bet_mask_file}"
    python3 -c "

import sys ;
sys.path.append('/software/') ;
from utilities_simple_trimmed import * ;  levelset2originalRF_new_flip()" "${original_ct_file}" "${levelset_bet_mask_file}" "${output_directory}"

    #### preprocessing csf mask:
    levelset_csf_mask_file=${output_directory}/${csffilename}
    echo "levelset_csf_mask_file:${levelset_csf_mask_file}"
    python3 -c "
import sys ;
sys.path.append('/software/') ;
from utilities_simple_trimmed import * ;   levelset2originalRF_new_flip()" "${original_ct_file}" "${levelset_csf_mask_file}" "${output_directory}"

    lower_threshold=0
    upper_threshold=20
    templatefilename=${template_prefix}.nii.gz
    mask_on_template=midlinecssfResampled1.nii.gz

    x=$grayimage
    bet_mask_filename=${output_directory}/${betfilename}
    infarct_mask_filename=${output_directory}/${infarctfilename}
    csf_mask_filename=${output_directory}/${csffilename}
    run_IML_NWU_CSF_CALC $x ${bet_mask_filename} ${csf_mask_filename} ${infarct_mask_filename}

  done

  # for f in ${output_directory}/*; do
  #     # if [ -d "$f" ]; then
  #         # $f is a directory
  #         rm -r $f
  #     # fi
  # done

}

# #####################################################
get_nifti_scan_uri() {
  # csvfilename=sys.argv[1]
  # dir_to_save=sys.argv[2]
  # echo " I AM IN copy_scan_data "
  # rm -r /ZIPFILEDIR/*

  sessionID=$1
  working_dir=${2}
  output_csvfile=${3}
  rm -r ${working_dir}/*
  output_dir=$(dirname ${output_csvfile})
  rm -r ${output_dir}/*
  # scanID=$2
  python3 -c "
import sys 
sys.path.append('/software');
from download_with_session_ID import *; 
call_decision_which_nifti()" ${sessionID} ${working_dir} ${output_csvfile}

}

copy_scan_data() {
  csvfilename=${1} #sys.argv[1]
  dir_to_save=${2} #sys.argv[2]
  # 		echo " I AM IN copy_scan_data "
  # rm -r /ZIPFILEDIR/*
  # rm -r ${working_dir}/*
  # rm -r ${output_dir}/*
  # sessionID=$1
  # # scanID=$2
  python3 -c "
import sys 
sys.path.append('/software');
from download_with_session_ID import *; 
downloadniftiwithuri_withcsv()" ${csvfilename} ${dir_to_save}

}
uploadsinglefile(){
local sessionID=${1}
local scanID=${2}
local mask_binary_output_dir=${3}
local snipr_output_foldername=${4}
local mask_binary_output_filename=${5}

echo ${mask_binary_output_dir}/${mask_binary_output_filename}
python3 -c "
import sys
sys.path.append('/software');
from download_with_session_ID import *;
uploadsinglefile()" ${sessionID} ${scanID} ${mask_binary_output_dir} ${snipr_output_foldername} ${mask_binary_output_filename}
}
getmaskfilesscanmetadata() {
  # def get_maskfile_scan_metadata():
  sessionId=${1}           #sys.argv[1]
  scanId=${2}              # sys.argv[2]
  resource_foldername=${3} # sys.argv[3]
  dir_to_save=${4}         # sys.argv[4]
  csvfilename=${5}         # sys.argv[5]
  python3 -c "
import sys 
sys.path.append('/software');
from download_with_session_ID import *; 
get_maskfile_scan_metadata()" ${sessionId} ${scanId} ${resource_foldername} ${dir_to_save} ${csvfilename}
}

#########################################################################
## GET THE SINGLE CT NIFTI FILE NAME AND COPY IT TO THE WORKING_DIR
#niftifile_csvfilename=${working_dir}/'this_session_final_ct.csv'
#get_nifti_scan_uri ${sessionID}  ${working_dir} ${niftifile_csvfilename}
call_download_files_in_a_resource_in_a_session_arguments=('call_download_files_in_a_resource_in_a_session' ${sessionID} "NIFTI_LOCATION" ${working_dir})
outputfiles_present=$(python3 download_with_session_ID.py "${call_download_files_in_a_resource_in_a_session_arguments[@]}")
echo '$outputfiles_present'::$outputfiles_present
echo $(ls ${working_dir}/*NIFTILOCATION.csv)
echo ${XNAT_HOST}:XNAT_HOST
########################################
for niftifile_csvfilename in ${working_dir}/*NIFTILOCATION.csv; do
  rm ${final_output_directory}/*.*
  rm ${output_directory}/*.*
  outputfiles_present=0
  echo $niftifile_csvfilename
  while IFS=',' read -ra array; do
    scanID=${array[2]}
    echo sessionId::${sessionID}
    echo scanId::${scanID}
    snipr_output_foldername="PREPROCESS_SEGM_3"
    ### check if the file exists:
    call_check_if_a_file_exist_in_snipr_arguments=('call_check_if_a_file_exist_in_snipr' ${sessionID} ${scanID} ${snipr_output_foldername} .pdf .csv)
    outputfiles_present=$(python3 download_with_session_ID.py "${call_check_if_a_file_exist_in_snipr_arguments[@]}")

    ################################################
    ####################################
    function_with_arguments=('call_delete_file_with_ext' ${sessionID} ${scanID} ${snipr_output_foldername} 'warped_mov_' ) ##'warped_1_mov_mri_region_' )
    #    echo "outputfiles_present="'$(python3 utilities_simple_trimmed.py' "${function_with_arguments[@]}"
    outputfiles_present=$(python3 download_with_session_ID.py "${function_with_arguments[@]}")

        function_with_arguments=('call_delete_file_with_ext' ${sessionID} ${scanID} ${snipr_output_foldername} 'warped_1_mov_' ) ##'warped_1_mov_mri_region_' )
        #    echo "outputfiles_present="'$(python3 utilities_simple_trimmed.py' "${function_with_arguments[@]}"
        outputfiles_present=$(python3 download_with_session_ID.py "${function_with_arguments[@]}")
#    function_with_arguments=('call_delete_file_with_ext' ${sessionID} ${scanID} MASKS '_total.nii.gz' ) ##'warped_1_mov_mri_region_' )
#    #    echo "outputfiles_present="'$(python3 utilities_simple_trimmed.py' "${function_with_arguments[@]}"
#    outputfiles_present=$(python3 download_with_session_ID.py "${function_with_arguments[@]}")
    ####################################

#    outputfiles_present=0
    echo "outputfiles_present:: "${outputfiles_present: -1}"::outputfiles_present"
    #echo "outputfiles_present::ATUL${outputfiles_present}::outputfiles_present"
    if [[ "${outputfiles_present: -1}" -eq 1 ]]; then
      echo " I AM THE ONE"
    fi
    if  [[ "${outputfiles_present: -1}" -eq 0 ]]; then ## [[ 1 -gt 0 ]]  ; then #

      echo "outputfiles_present:: "${outputfiles_present: -1}"::outputfiles_present"

      copy_scan_data ${niftifile_csvfilename} ${working_dir_1} #${working_dir}
      nifti_file_without_ext=$(basename $(ls ${working_dir_1}/*.nii))
      nifti_file_without_ext=${nifti_file_without_ext%.nii*}
      ##############################################################################################################

      ## GET THE RESPECTIVS MASKS NIFTI FILE NAME AND COPY IT TO THE WORKING_DIR

      #####################################################################################
      resource_dirname='MASKS'
      output_dirname=${working_dir}
      while IFS=',' read -ra array; do
        scanID=${array[2]}
        echo sessionId::${sessionID}
        echo scanId::${scanID}
      done < <(tail -n +2 "${niftifile_csvfilename}")
      echo working_dir::${working_dir}
      echo output_dirname::${output_dirname}
#      copy_masks_data ${sessionID} ${scanID} ${resource_dirname} ${output_dirname}
      resource_dirname='PREPROCESS_SEGM_3'
      copy_masks_data ${sessionID} ${scanID} ${resource_dirname} ${output_dirname}
      ###########################
      session_ct=$( ls ${working_dir_1}/*'.nii' )
      session_ct_bname_noext=$(basename ${session_ct})
      session_ct_bname_noext=${session_ct_bname_noext%.nii*}
#      template_ct='/software/COLIHM620406202215542.nii.gz' ###${template_prefix}.nii.gz'

      moving_image_original_filename=/software/COLIHM620406202215542.nii.gz ###COLIHM620406202215542.nii.gz ##'  ####${template_prefix}.nii.gz ##${session_ct_bet_gray}
      ##'COLIHM620406202215542'
#      template_prefix=${session_ct_bname_noext}  ##'COLIHM620406202215542'
      fixed_image_original_filename=${working_dir}/${session_ct_bname_noext}_brain_f.nii.gz
#      template_prefix=$(basename ${fixed_image_filename%.nii*})
      rigid_registration_nii_file=${working_dir}/'mov_'$(basename ${moving_image_original_filename%.nii*})_fixed_$(basename  ${fixed_image_original_filename%.nii*})_lin1.nii.gz

fixed_image=${fixed_image_original_filename}
moving_image=${rigid_registration_nii_file} #${working_dir}/mov_${session_ct_bname_noext}_brain_f_fixed_${template_prefix}_lin1.nii.gz ##${session_ct_bet_gray} ##${working_dir}/"mov_warped_mov_mni_icbm152_t1_tal_nlin_sym_55_ext_bet_gray_fixed_${template_prefix}_lin1_fixed_${nifti_file_without_ext}_brain_f_lin1.nii.gz"
echo "moving_image::${moving_image}::fixed_image::${fixed_image_original_filename}"
rm ${working_dir}/warped_1*
#####################################################################################################################

      python3 create_datah5files_May24_2023.py ${moving_image} ${fixed_image}
##      mkdir /workspace/deepreg/DeepReg/demos/classical_mr_prostate_nonrigid/dataset
      cp -r /workspace/deepreg/DeepReg /software/
      cp /software/data.h5 /software/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/
      cp /software/demo_register_batch_atul.py /software/DeepReg/demos/classical_mr_prostate_nonrigid/
      if [ ! -f /workinginput/fixed_image.nii.gz  ]; then
          echo "File does not exist."
      python3 /software/demo_register_batch_atul.py /software/DeepReg/demos/classical_mr_prostate_nonrigid/dataset/data.h5 ${output_directory}
          fi
    cp /workinginput/ddf.nii.gz  /workingoutput/
    cp /workinginput/fixed_image.nii.gz  /workingoutput/

    original_nifti_filename=$(ls ${working_dir_1}/*.nii)
    csf_mask_file_moving_original=/software/VENTRICLE_COLIHM62.nii.gz
#    moving_image_filename='mov_'$(basename ${csf_mask_file_moving_original%.nii*})_fixed_$(basename  ${fixed_image_original_filename%.nii*})_lin1.nii.gz
    #moving_image_filename=${moving_image_filename%.nii*}resampled_mov.nii.gz
    csf_mask_after_lin_reg=${working_dir}/'mov_'$(basename ${csf_mask_file_moving_original%.nii*})_fixed_$(basename  ${fixed_image_original_filename%.nii*})_lin1.nii.gz

# mov_${moving_image_filename%.nii*}_fixed_${template_prefix}_lin1_BET.nii.gz
      echo "python3 /software/runoncsfmask_atul09272024.py ${csf_mask_after_lin_reg} ${working_dir_1} ${sessionID} ${scanID} $(basename  ${original_nifti_filename})"
      python3 /software/runoncsfmask_atul09272024.py ${csf_mask_after_lin_reg} ${working_dir_1} ${sessionID} ${scanID} $(basename  ${original_nifti_filename})
########### cistern
cistern_mask_file_moving_original=/software/CISTERN_COLIHM62.nii.gz
cistern_mask_after_lin_reg=${working_dir}/'mov_'$(basename ${cistern_mask_file_moving_original%.nii*})_fixed_$(basename  ${fixed_image_original_filename%.nii*})_lin1_BET.nii.gz
python3 /software/runoncsfmask_atul09272024.py ${cistern_mask_after_lin_reg} ${working_dir_1} ${sessionID} ${scanID} $(basename  ${original_nifti_filename})
######
midline_mask_file_moving_original=/software/midlinecssfResampled1.nii.gz  ##scct_strippedResampled1_left_mask.nii.gz ####midlinecssfResampled1.nii.gz ##CISTERN_COLIHM62.nii.gz
midline_mask_after_lin_reg=${working_dir}/'mov_'$(basename ${midline_mask_file_moving_original%.nii*})_fixed_$(basename  ${fixed_image_original_filename%.nii*})_lin1_BET.nii.gz

############ midline
python3 /software/runoncsfmask_atul09272024.py ${midline_mask_after_lin_reg} ${working_dir_1} ${sessionID} ${scanID} $(basename  ${original_nifti_filename})
######
######
midline_mask_file_moving_original=/software/midlinecssfResampled1.nii.gz ##CISTERN_COLIHM62.nii.gz scct_strippedResampled1_left_half.nii.gz ####
midline_mask_after_lin_reg=${working_dir}/'mov_'$(basename ${midline_mask_file_moving_original%.nii*})_fixed_$(basename  ${fixed_image_original_filename%.nii*})_lin1_BET.nii.gz

############ half brain
python3 /software/runoncsfmask_atul09272024.py ${midline_mask_after_lin_reg} ${working_dir_1} ${sessionID} ${scanID} $(basename  ${original_nifti_filename})
######

#      done mov_COLI_HLP12_09122020_2351_3_resaved_csf_unet_fixed_COLIHM620406202215542_lin1_BET.nii.gz
#    moving_image_filename=${session_ct_bname_noext}_resaved_csf_unet.nii.gz
    #moving_image_filename=${moving_image_filename%.nii*}resampled_mov.nii.gz
#      csf_mask_after_lin_reg=${working_dir}/mov_${moving_image_filename%.nii*}_fixed_${template_prefix}_lin1_BET.nii.gz
#      echo "python3 /software/runoncsfmask_atul09272024.py ${csf_mask_after_lin_reg} ${working_dir_1} ${sessionID} ${scanID} $(basename  ${original_nifti_filename})"
#      python3 /software/runoncsfmask_atul09272024.py ${csf_mask_after_lin_reg} ${working_dir_1} ${sessionID} ${scanID} $(basename  ${original_nifti_filename})
#      done

      snipr_output_foldername="PREPROCESS_SEGM_3"
#      uploadsinglefile ${sessionID} ${scanID} ${mask_binary_output_dir} ${snipr_output_foldername} ${mask_binary_output_filename}
#      uploadsinglefile ${sessionID} ${scanID} ${mask_binary_output_dir} ${snipr_output_foldername} ${mask_binary_output_filename}
#            snipr_output_foldername="PREPROCESS_SEGM_3"
            all_files_to_upload=()
            all_warped_files=$(find ${working_dir} -name 'warped'*${template_prefix}*'.nii.gz')
            for eachfile in ${all_warped_files};
            do
              echo ${eachfile}
              all_files_to_upload+=("$(basename ${eachfile})")
              uploadsinglefile ${sessionID} ${scanID} $(dirname ${eachfile}) ${snipr_output_foldername} $(basename ${eachfile} )
            done
            all_warped_files=$(find ${working_dir_1} -name 'warped'*${template_prefix}*'.nii.gz')
            for eachfile in ${all_warped_files};
            do
              echo ${eachfile}
              all_files_to_upload+=("$(basename ${eachfile})")
              uploadsinglefile ${sessionID} ${scanID} $(dirname ${eachfile}) ${snipr_output_foldername} $(basename ${eachfile} )
            done
            for eachfile in ${output_directory}/*image*.nii*;
            do
              echo ${eachfile}
              all_files_to_upload+=("$(basename ${eachfile})")
              uploadsinglefile ${sessionID} ${scanID} $(dirname ${eachfile}) ${snipr_output_foldername} $(basename ${eachfile} )
            done
            for eachfile in ${output_directory}/*ddf*.nii*;
            do
              echo ${eachfile}
              all_files_to_upload+=("$(basename ${eachfile})")
              uploadsinglefile ${sessionID} ${scanID} $(dirname ${eachfile}) ${snipr_output_foldername} $(basename ${eachfile} )
            done


#  for each_warped_1 in ${working_dir_1}/warped_1* ; do
#  call_function=('call_copy_affine' ${each_warped_1} ${original_nifti_filename} ${each_warped_1} )
#  outputfiles_present=$(python3 utilities_simple_trimmed.py "${call_function[@]}")
#  done
      ## COPY IT TO THE SNIPR RESPECTIVE SCAN RESOURCES
#      file_suffixes=( warped_1_*resaved_infarct_auto_removesmall_fixed_${template_prefix}_lin1_BET* ) #sys.argv[5]
#      for file_suffix in ${file_suffixes[@]}; do
#        copyoutput_with_prefix_to_snipr ${sessionID} ${scanID} "${working_dir_1}" ${snipr_output_foldername} ${file_suffix}
#      done
###      ######################################################################################################################
      call_get_session_label_arguments=('call_get_session_project' ${sessionID} ${output_directory}/${session_ct_bname_noext}_SESSION_PROJECT.csv)
      outputfiles_present=$(python3 download_with_session_ID.py "${call_get_session_label_arguments[@]}")
      ####################### GET PROJECT NAME ###############################
      #################### WRITE TO THE MYSQL DATABASE IF THE STEP IS DONE #######################################################
      csv_file=${output_directory}/${session_ct_bname_noext}_SESSION_PROJECT.csv
      column_name="SESSION_PROJECT"
      # Get the index (column number) of the desired column
      col_index=$(awk -F, -v col="$column_name" 'NR==1 {
        for (i=1; i<=NF; i++) if ($i == col) { print i; exit }
      }' "$csv_file")
      # Get the first value under that column (excluding header)
      first_value=$(awk -F, -v idx="$col_index" 'NR==2 { print $idx }' "$csv_file")
      database_table_name=${first_value}
      echo "database_table_name::${database_table_name}"
      function_with_arguments=('call_pipeline_step_completed' ${database_table_name} ${sessionID} ${scanID} "NONRIGID_REGIS_WITH_COLIHM62_COMPLETE" 0 ${snipr_output_foldername} ) ##$(basename  ${fixed_image_filename}) $(basename  ${infarct_mask_binary_output_filename})  $(basename  ${registration_mat_file}) $(basename  ${registration_nii_file}) $(basename  ${mask_binary_output_dir}/${mask_binary_output_filename})  ) ##'warped_1_mov_mri_region_' )
      # Append all warped files to the arguments array
      for f in "${all_files_to_upload[@]}"; do
        function_with_arguments+=("$f")
      done

      echo "outputfiles_present=(python3 download_with_session_ID.py ${function_with_arguments[@]})"
      outputfiles_present=$(python3 download_with_session_ID.py "${function_with_arguments[@]}")
      echo " FILES NOT PRESENT I AM WORKING ON IT"
    else
      echo " FILES ARE PRESENT "
    ######################################################################################################################
    fi
    ##


  done < <(tail -n +2 "${niftifile_csvfilename}")
done
