#!/bin/bash
######################
######## USER DETAILS#######
SESSION_ID=${1}
snipr_step='scan_selections'
XNAT_PASS='Mrityor1!'
XNAT_USER=atulkumar
XNAT_HOST='https://snipr.wustl.edu'
function directory_to_create_destroy(){
working_dir=${PWD}/workinginput
working_dir_1=${PWD}/input1
output_directory=${PWD}/workingoutput
final_output_directory=${PWD}/outputinsidedocker
software=${PWD}/software
ZIPFILEDIR=${PWD}/ZIPFILEDIR 
NIFTIFILEDIR=$PWD/NIFTIFILEDIR 
DICOMFILEDIR=$PWD/DICOMFILEDIR
working=$PWD/working
input=$PWD/input
input1=$PWD/input1
output=$PWD/output
rm  -r    ${working_dir}/*
rm  -r    ${working_dir_1}/*
rm  -r    ${output_directory}/*
rm  -r    ${final_output_directory}/*
# rm  -r    ${software}
rm  -r    ${ZIPFILEDIR}/*
rm  -r    ${NIFTIFILEDIR}/*
rm  -r    ${DICOMFILEDIR}/*
rm  -r    ${working}/*
rm  -r    ${input}/*
rm  -r    ${output}/*


}
# EXAMPLE: ICH_0058_CT_20170324  SNIPR02_E03684
function scan_selection(){
local SESSION_ID=${1}

script_number='APPLYDEEPREG_V2_SNIPR_CALL_LOCATION_DISTRIBUTION'  #'APPLYDEEPREG_V2' ##'APPLYDEEPREG_CSF_CISTERN_MIDLINE_SEP_COLIHM62'  ######APPLYDEEPREG' ###_V2' #######'APPLYDEEPREGTOMRI' ##'APPLYDEEPREG_V1' ##APPLYDEEPREGONREGIONMASKS' #'APPLYDEEPREGTOMRI' ####'APPLYDEEPREG'
git_repo='https://github.com/dharlabwustl/deepregbasedregistration.git' ##'https://github.com/dharlabwustl/EDEMA_MARKERS_PROD.git'
#script_number='APPLYDEEPREGTOMRI' ##'TO_ORIGINAL_REF_FRAME' #2 ###EDEMABIOMARKERS #2 #12
snipr_host='https://snipr.wustl.edu'
/callfromgithub/downloadcodefromgithub.sh $SESSION_ID $XNAT_USER $XNAT_PASS ${git_repo} ${script_number}  ${snipr_host}
}



# Function to get the column number given the column name
get_column_number() {
    local csv_file="$1"   # The CSV file to search in
    local column_name="$2" # The column name to find

    # Get the header (first line) of the CSV file
    header=$(head -n 1 "$csv_file")

    # Split the header into an array of column names
    IFS=',' read -r -a columns <<< "$header"

    # Loop through the columns and find the index of the column name
    for i in "${!columns[@]}"; do
        if [[ "${columns[$i]}" == "$column_name" ]]; then
            # Print the 1-based index (cut and other tools expect 1-based indexes)
            echo $((i  ))
            return
        fi
    done

    # If the column is not found, print an error and return a failure status
    echo "Column '$column_name' not found!" >&2
    return 1
}
##sessions_list='wrong_data_from_arjun.csv' ##vns_list_to_fix_df_1.csv' ###'sessions_COLI_ANALYTICS_STEP3_20231122041129_ordered.csv' 
#directory_to_create_destroy
#sessions_list=${working_dir}/session.csv
#curl -u $XNAT_USER:$XNAT_PASS -X GET $XNAT_HOST/data/projects/${project_ID}/experiments/?format=csv > ${sessions_list}
#
#csv_file=${sessions_list} 
#column_name="ID" ##"SESSION_ID" 
#column_number=$(get_column_number "$csv_file" "$column_name")
#echo ${column_number}
#count=0
#while IFS=',' read -ra array; do
#    if [ ${count} -gt -114 ]; then
#    SESSION_ID=${array[${column_number}]}
#    echo ${SESSION_ID}  
    directory_to_create_destroy
    echo ${SESSION_ID}
    scan_selection ${SESSION_ID}  
#    break
#    fi
#    count=$((count+1))
#done < <(tail -n +2 "${sessions_list}")
