session_id_filename=${1}
#python bulk_start.py  --project COLI --session_label_file session_labels.txt  --container TRANFORM_BEFORE_DEEPREG_V2 --delay 2  --user ${XNAT_USER} --password ${XNAT_PASS} --host ${XNAT_HOST}
container_name=${2}
/opt/conda/envs/deepreg/bin/python3  /software/bulk_start.py  --project COLI --session_id_file ${session_id_filename}  --container ${container_name}  --delay 2 --user ${XNAT_USER} --password ${XNAT_PASS} --host ${XNAT_HOST}
