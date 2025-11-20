#!/bin/bash
set -euo pipefail

###############################################################################
# CONFIGURATION (edit these paths if needed)
###############################################################################

# If you still want to pass session/scan IDs for naming, keep these.
SESSION_ID='SNIPR12_E00443' ##"${1:-LOCAL_SESSION}"
SCAN_ID=2 ##"${2:-LOCAL_SCAN}"

# Directories
WORKING_DIR="/workinginput"     # intermediate files, registered masks, etc.
INPUT_DIR="/input1"             # original CT NIfTI(s)
OUTPUT_DIR="/workingoutput"     # DeepReg outputs, etc.
FINAL_OUTPUT_DIR="/outputinsidedocker"

############
cp /input/SCANS/2/NIFTI/* ${INPUT_DIR}/
# Directory containing masks from prior pipeline (Yasheng outputs etc.)
#WORKING_DIR_MASKS="/workinginput"
cp /input/SCANS/2/PREPROCESS_SEGM/* ${WORKING_DIR}/
cp /input/SCANS/2/PREPROCESS_SEGM_3/* ${WORKING_DIR}/
###

# Template & masks (already on local machine)
TEMPLATE_CT="/software/COLIHM620406202215542.nii.gz"
VENTRICLE_MASK="/software/VENTRICLE_COLIHM62.nii.gz"
CISTERN_MASK="/software/CISTERN_COLIHM62.nii.gz"
MIDLINE_MASK="/software/scct_strippedResampled1_left_mask.nii.gz"
MIDLINE_HALF_MASK="/software/scct_strippedResampled1_left_half.nii.gz"

DEEPREG_DATA_H5="/software/data.h5"
DEEPREG_ROOT="/software/DeepReg"
DEEPREG_DEMO_DIR="${DEEPREG_ROOT}/demos/classical_mr_prostate_nonrigid"
DEEPREG_DEMO_DATASET_DIR="${DEEPREG_DEMO_DIR}/dataset"

PYTHON_BIN="/opt/conda/envs/deepreg/bin/python3"

###############################################################################
# FUNCTIONS
###############################################################################

prepare_deepreg_dataset() {
  local moving_image="$1"
  local fixed_image="$2"

  echo "[*] Creating DeepReg data.h5 from:"
  echo "    moving: ${moving_image}"
  echo "    fixed : ${fixed_image}"

  ${PYTHON_BIN} /software/create_datah5files_May24_2023.py "${moving_image}" "${fixed_image}"

  mkdir -p "${DEEPREG_DEMO_DATASET_DIR}"
  cp -f "${DEEPREG_DATA_H5}" "${DEEPREG_DEMO_DATASET_DIR}/"

  mkdir -p "${DEEPREG_DEMO_DIR}"
  cp -f /software/demo_register_batch_atul.py "${DEEPREG_DEMO_DIR}/"
}

run_deepreg_registration() {
  echo "[*] Running DeepReg registration (if needed)..."

  if [ ! -f "${WORKING_DIR}/fixed_image.nii.gz" ]; then
    ${PYTHON_BIN} "${DEEPREG_DEMO_DIR}/demo_register_batch_atul.py" \
      "${DEEPREG_DEMO_DATASET_DIR}/data.h5" \
      "${OUTPUT_DIR}"
  else
    echo "    DeepReg output fixed_image.nii.gz already exists, skipping demo_register_batch_atul.py."
  fi

  # Copy key outputs into OUTPUT_DIR
  if [ -f "${WORKING_DIR}/ddf.nii.gz" ]; then
    cp -f "${WORKING_DIR}/ddf.nii.gz" "${OUTPUT_DIR}/"
  fi
  if [ -f "${WORKING_DIR}/fixed_image.nii.gz" ]; then
    cp -f "${WORKING_DIR}/fixed_image.nii.gz" "${OUTPUT_DIR}/"
  fi
}

run_csf_and_midline_pipeline() {
  local ct_file="$1"

  local ct_basename
  ct_basename="$(basename "${ct_file}")"
  local ct_root="${ct_basename%.nii*}"

  echo "================================================================="
  echo "[*] Processing CT: ${ct_basename}"
  echo "================================================================="

  # Expected precomputed fixed brain image
  local fixed_image_original="${WORKING_DIR}/${ct_root}_brain_f.nii.gz"
  if [ ! -f "${fixed_image_original}" ]; then
    echo "ERROR: Expected fixed brain image not found:"
    echo "       ${fixed_image_original}"
    exit 1
  fi

  # Expected rigidly registered template CT (already computed earlier)
  local rigid_registration_nii="${WORKING_DIR}/mov_$(basename "${TEMPLATE_CT%.nii*}")_fixed_$(basename "${fixed_image_original%.nii*}")_lin1.nii.gz"

  if [ ! -f "${rigid_registration_nii}" ]; then
    echo "WARNING: Expected rigid registration file not found:"
    echo "         ${rigid_registration_nii}"
    echo "         Continuing but DeepReg may fail if this is required."
  fi

  local moving_image="${rigid_registration_nii}"
  local fixed_image="${fixed_image_original}"

  prepare_deepreg_dataset "${moving_image}" "${fixed_image}"
  run_deepreg_registration

  local original_nifti_filename="${ct_file}"

  # Paths to linearly registered masks (already created earlier in your pipeline)
  local csf_mask_after_lin_reg="${WORKING_DIR}/mov_$(basename "${VENTRICLE_MASK%.nii*}")_fixed_$(basename "${fixed_image_original%.nii*}")_lin1.nii.gz"
  local cistern_mask_after_lin_reg="${WORKING_DIR}/mov_$(basename "${CISTERN_MASK%.nii*}")_fixed_$(basename "${fixed_image_original%.nii*}")_lin1_BET.nii.gz"
  local midline_mask_after_lin_reg="${WORKING_DIR}/mov_$(basename "${MIDLINE_MASK%.nii*}")_fixed_$(basename "${fixed_image_original%.nii*}")_lin1_BET.nii.gz"
  local midline_half_mask_after_lin_reg="${WORKING_DIR}/mov_$(basename "${MIDLINE_HALF_MASK%.nii*}")_fixed_$(basename "${fixed_image_original%.nii*}")_lin1_BET.nii.gz"

  echo "[*] Running CSF / cistern / midline mask processing with runoncsfmask_atul09272024.py"

  # CSF (ventricle) mask
  if [ -f "${csf_mask_after_lin_reg}" ]; then
    ${PYTHON_BIN} /software/runoncsfmask_atul09272024.py \
      "${csf_mask_after_lin_reg}" \
      "${INPUT_DIR}" \
      "${SESSION_ID}" \
      "${SCAN_ID}" \
      "$(basename "${original_nifti_filename}")"
  else
    echo "WARNING: CSF mask after linear registration not found:"
    echo "         ${csf_mask_after_lin_reg}"
  fi

  # Cistern mask
  if [ -f "${cistern_mask_after_lin_reg}" ]; then
    ${PYTHON_BIN} /software/runoncsfmask_atul09272024.py \
      "${cistern_mask_after_lin_reg}" \
      "${INPUT_DIR}" \
      "${SESSION_ID}" \
      "${SCAN_ID}" \
      "$(basename "${original_nifti_filename}")"
  else
    echo "WARNING: Cistern mask after linear registration not found:"
    echo "         ${cistern_mask_after_lin_reg}"
  fi

  # Midline mask
  if [ -f "${midline_mask_after_lin_reg}" ]; then
    ${PYTHON_BIN} /software/runoncsfmask_atul09272024.py \
      "${midline_mask_after_lin_reg}" \
      "${INPUT_DIR}" \
      "${SESSION_ID}" \
      "${SCAN_ID}" \
      "$(basename "${original_nifti_filename}")"
  else
    echo "WARNING: Midline mask after linear registration not found:"
    echo "         ${midline_mask_after_lin_reg}"
  fi

  # Half-brain midline mask
  if [ -f "${midline_half_mask_after_lin_reg}" ]; then
    ${PYTHON_BIN} /software/runoncsfmask_atul09272024.py \
      "${midline_half_mask_after_lin_reg}" \
      "${INPUT_DIR}" \
      "${SESSION_ID}" \
      "${SCAN_ID}" \
      "$(basename "${original_nifti_filename}")"
  else
    echo "WARNING: Half-brain midline mask after linear registration not found:"
    echo "         ${midline_half_mask_after_lin_reg}"
  fi
}

###############################################################################
# MAIN
###############################################################################

echo "================================================================="
echo "[*] Local-only pipeline (no XNAT/SNIPR download/upload)"
echo "    SESSION_ID = ${SESSION_ID}"
echo "    SCAN_ID    = ${SCAN_ID}"
echo "    INPUT_DIR  = ${INPUT_DIR}"
echo "    WORKING_DIR= ${WORKING_DIR}"
echo "    OUTPUT_DIR = ${OUTPUT_DIR}"
echo "================================================================="

shopt -s nullglob
ct_files=("${INPUT_DIR}"/*.nii*)

if [ "${#ct_files[@]}" -eq 0 ]; then
  echo "ERROR: No NIfTI files found in ${INPUT_DIR}"
  exit 1
fi

for ct in "${ct_files[@]}"; do
  run_csf_and_midline_pipeline "${ct}"
done

echo "[*] Done."
