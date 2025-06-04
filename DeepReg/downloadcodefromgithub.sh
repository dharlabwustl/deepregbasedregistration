#!/bin/bash
cd /software/
git_link=${4}
git clone ${git_link} #https://github.com/dharlabwustl/EDEMA_MARKERS_PROD.git
y=${git_link%.git}
git_dir=$(basename $y)
mv ${git_dir}/DeepReg/deepreg /software/
mv ${git_dir}/* /software/
chmod +x /software/*.sh 
#cp -r /home/rapids/DeepReg/deepreg /software/
#cp -r  /software/DeepReg/deepreg /software/
#cp -r /workspace/DeepReg/* /software/
#chmod 755 /software/*
SESSION_ID=${1}
XNAT_USER=${2}
XNAT_PASS=${3}
export XNAT_USER=$XNAT_USER
export XNAT_PASS=$XNAT_PASS
echo XNAT_USER=$XNAT_USER
echo XNAT_PASS=$XNAT_PASS
TYPE_OF_PROGRAM=${5}
export XNAT_HOST=${6}
/software/script_to_call_main_program.sh $SESSION_ID $XNAT_USER $XNAT_PASS ${TYPE_OF_PROGRAM} ${6}
