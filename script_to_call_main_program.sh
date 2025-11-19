#!/bin/bash
SESSION_ID=${1}
XNAT_USER=${2}
XNAT_PASS=${3}
TYPE_OF_PROGRAM=${4}
echo TYPE_OF_PROGRAM::${TYPE_OF_PROGRAM}
#'https://redcap.wustl.edu/redcap/api/' #
echo ${REDCAP_API}
#export REDCAP_API=${6}
#echo REDCAP_API::${REDCAP_API}
# The input string
input=$XNAT_HOST ##"one::two::three::four"
# Check if '::' is present
if echo "$input" | grep -q "+"; then
  # Set the delimiter
  IFS='+'

  # Read the split words into an array
  read -ra ADDR <<< "$input"
  export XNAT_HOST=${ADDR[0]} 
  SUBTYPE_OF_PROGRAM=${ADDR[1]} 
else
export XNAT_HOST=${5} 
    echo "'+' is not present in the string"
fi


echo ${TYPE_OF_PROGRAM}::TYPE_OF_PROGRAM::${SUBTYPE_OF_PROGRAM}::${ADDR[0]}::${ADDR[2]}::${ADDR[3]}

if [[ ${TYPE_OF_PROGRAM} ==   'APPLYDEEPREG_CSF_SEP' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_CSF_SEP"
  /software/deepregbasedregis_csf_separation.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi

if [[ ${TYPE_OF_PROGRAM} ==   'APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP"
  /software/deepregbasedregis_csf_cistern_midline_separation.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi

if [[ ${TYPE_OF_PROGRAM} ==   'APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62_LOCAL_COMPUTER' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62_LOCAL_COMPUTER"
  /software/deepregbasedregis_csf_cistern_midline_separation_with_COLIHM62_local_computer.sh  $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi

if [[ ${TYPE_OF_PROGRAM} ==   'APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62"
  /software/deepregbasedregis_csf_cistern_midline_separation_with_COLIHM62.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi

if [[ ${TYPE_OF_PROGRAM} ==   'NO_RAPIDS_APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==NO_RAPIDS_APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62"
  /software/deepregbasedregis_csf_cistern_midline_separation_with_COLIHM62_NO_RAPIDS.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi

if [[ ${TYPE_OF_PROGRAM} ==   'APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62_VENTRICLE' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62_VENTRICLE"
  /software/deepregbasedregis_csf_cistern_midline_separation_with_COLIHM62_ventriclemask.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi

if [[ ${TYPE_OF_PROGRAM} == 'APPLYDEEPREG_V1' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_V1"
  /software/deepregbasedregis_location_v1.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi
if [[ ${TYPE_OF_PROGRAM} == 'APPLYDEEPREG_V2' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_V2"
  /software/deepregbasedregis_location_v2.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi
if [[ ${TYPE_OF_PROGRAM} == 'APPLYDEEPREG_V2_WITH_TF' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_V2_WITH_TF"
  /software/deepregbasedregis_location_v2_with_tf.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi

if [[ ${TYPE_OF_PROGRAM} == 'APPLYDDFTOMASK' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDDFTOMASK"
  /software/deepregbasedregis_location_v3.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi

if [[ ${TYPE_OF_PROGRAM} == 'APPLYDEEPREG' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG"
  /software/deepregbasedregis.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi
if [[ ${TYPE_OF_PROGRAM} == 'APPLYDEEPREG_FOR_VEN_SEP'   ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREG_FOR_VEN_SEP"
  /software/deepregbasedregis_for_vent_sep.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi
if [[ ${TYPE_OF_PROGRAM} == 'APPLYDEEPREGONREGIONMASKS' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREGONREGIONMASKS"
  /software/deepregbasedregis_location.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
fi
if [[ ${TYPE_OF_PROGRAM} == 'APPLYDEEPREGTOMRI' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREGTOMRI"
#  /software/deepregapplication.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
    /software/deepregbasedregis_location_MRI_11042024.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output

fi
if [[ ${TYPE_OF_PROGRAM} == 'APPLYDEEPREGTOMRIREFCOLIHLP62' ]]; then
  echo " I AM AT TYPE_OF_PROGRAM==APPLYDEEPREGTOMRIREFCOLIHLP62"
#  /software/deepregapplication.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output
    /software/deepregbasedregis_location_MRI_REGTO_COLIHLP62.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input1 /output

fi


