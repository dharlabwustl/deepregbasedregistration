#!/usr/bin/python
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os, sys, errno, shutil, uuid,subprocess,csv,json
import math,inspect
import glob,xnat
import re,time
import requests
import pandas as pd
import nibabel as nib
import numpy as np
import pathlib
import os
import traceback
# import xnat
import argparse,xmltodict
from redcapapi_functions import *
catalogXmlRegex = re.compile(r'.*\.xml$')
XNAT_HOST_URL=os.environ['XNAT_HOST']  #'http://snipr02.nrg.wustl.edu:8080' #'https://snipr02.nrg.wustl.edu' #'https://snipr.wustl.edu'
XNAT_HOST = XNAT_HOST_URL # os.environ['XNAT_HOST'] #
XNAT_USER = os.environ['XNAT_USER']#
XNAT_PASS =os.environ['XNAT_PASS'] #
api_token=os.environ['REDCAP_API']

# import xnat
import inspect
import traceback
from datetime import datetime
from railway_fill_database import apply_single_row_csv_to_table
LOG_FILE = "./xnat_session_errors.log"
import inspect
import traceback
from datetime import datetime

LOG_FILE = "/software/railway_db_errors.log"

ERROR_FILE = "/software/error.log"
def log_error(msg,func_name):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # err = (
    #     f"[{ts}]\n"
    #     f"{msg}\n"
    #     f"Traceback:\n{traceback.format_exc()}\n"
    #     f"{'-' * 80}\n"
    # )
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    err = (
        f"[{ts}] Function: {func_name}\n"
        f"[{ts}] Function: {msg}\n"
        # f"Session ID: {session_id}\n"
        f"{msg}\n"
        f"Traceback:\n{traceback.format_exc()}\n"
        f"{'-' * 80}\n"
    )
    with open(ERROR_FILE, "w") as f:
        f.write(err)
import re
from datetime import datetime

def _extract_mmddyyyy_from_tail(filename: str, ext_lower: str):
    """
    Extract date from tail pattern: _MM_DD_YYYY.<ext>
    Example: ..._09_26_2023.pdf  -> datetime.date(2023, 9, 26)
    Returns None if pattern not found.
    """
    # Ensure we match the date immediately before the extension
    # e.g. "_09_26_2023.pdf" or "_09_26_2023.nii.gz" (ext_lower passed in)
    pattern = re.compile(rf"_(\d{{2}})_(\d{{2}})_(\d{{4}}){re.escape(ext_lower)}$", re.IGNORECASE)
    m = pattern.search(filename)
    if not m:
        return None
    mm, dd, yyyy = m.group(1), m.group(2), m.group(3)
    try:
        return datetime.strptime(f"{mm}_{dd}_{yyyy}", "%m_%d_%Y").date()
    except Exception:
        return None


# # ---- replace your old sort with this ----
# ext_lower = ext_lower  # already computed earlier (like ".pdf")
# dated = []
# undated = []
#
# for fn in matches:
#     d = _extract_mmddyyyy_from_tail(fn, ext_lower)
#     if d is None:
#         undated.append(fn)
#     else:
#         dated.append((d, fn))
#
# if dated:
#     # sort by actual date, then filename as tie-breaker
#     dated.sort(key=lambda x: (x[0], x[1]))
#     latest_name = dated[-1][1]
# else:
#     # fallback if none have the date pattern
#     matches_sorted = sorted(matches)
#     latest_name = matches_sorted[-1]

def download_file_from_xnat_uri(uri: str, out_path: str, verify: bool = True):
    """
    Download a file from XNAT given a REST URI like:
      /data/projects/.../files/<filename>

    Saves to out_path and returns out_path on success, else None.
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        if not uri or not uri.startswith("/data/"):
            log_error(f"Invalid uri: {uri}", func_name)
            return None

        if not out_path:
            log_error("out_path is empty", func_name)
            return None

        # Build full URL
        base = XNAT_HOST.rstrip("/")
        url = f"{base}{uri}"

        # Ensure parent dir exists
        parent = os.path.dirname(out_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        # Stream download
        with requests.get(url, auth=(XNAT_USER, XNAT_PASS), stream=True, verify=verify) as r:
            if r.status_code != 200:
                log_error(f"Download failed: HTTP {r.status_code} url={url} text={r.text[:200]}", func_name)
                return None

            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

        return out_path

    except Exception:
        log_error("Unhandled exception during download_file_from_xnat_uri", func_name)
        return None

def get_latest_file_uri_from_scan_resource(
    session_id: str,
    scan_id: str,
    scan_resource_dir_name: str,
    file_extension: str,
):
    """
    Given:
      - session_id (experiment id)
      - scan_id (scan identifier)
      - scan_resource_dir_name (resource folder name under the scan)
      - file_extension (e.g. ".pdf" or "pdf")

    Do:
      - list files in scan resource folder that end with the extension
      - sort filenames
      - pick the last one (latest by sort order)
      - return the URI of that file

    Returns:
      - uri (str) OR None on failure
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        # Normalize extension
        ext = file_extension.strip()
        if not ext:
            log_error("Empty file_extension provided", func_name)
            return None
        if not ext.startswith("."):
            ext = "." + ext
        ext_lower = ext.lower()

        with xnat.connect(XNAT_HOST, user=XNAT_USER, password=XNAT_PASS) as conn:
            if session_id not in conn.experiments:
                log_error(f"Session ID not found on XNAT: {session_id}", func_name)
                return None

            exp = conn.experiments[session_id]

            # Find scan
            if scan_id not in exp.scans:
                log_error(f"Scan ID not found in session: {scan_id}", func_name)
                return None

            scan = exp.scans[scan_id]

            # Find scan resource directory
            if scan_resource_dir_name not in scan.resources:
                log_error(
                    f'Scan resource "{scan_resource_dir_name}" not found for scan_id={scan_id}',
                    func_name,
                )
                return None

            res = scan.resources[scan_resource_dir_name]

            # List files with the requested extension
            file_names = [str(fn) for fn in res.files.keys()]
            matches = [fn for fn in file_names if fn.lower().endswith(ext_lower)]

            if not matches:
                log_error(
                    f'No files ending with "{ext}" found in scan_resource="{scan_resource_dir_name}" '
                    f'for scan_id={scan_id}',
                    func_name,
                )
                return None

            # Sort and pick "latest" by sort order
            # matches_sorted = sorted(matches)
            # latest_name = matches_sorted[-1]
            ext_lower = ext_lower  # already computed earlier (like ".pdf")
            dated = []
            undated = []

            for fn in matches:
                d = _extract_mmddyyyy_from_tail(fn, ext_lower)
                if d is None:
                    undated.append(fn)
                else:
                    dated.append((d, fn))

            if dated:
                # sort by actual date, then filename as tie-breaker
                dated.sort(key=lambda x: (x[0], x[1]))
                latest_name = dated[-1][1]
            else:
                # fallback if none have the date pattern
                matches_sorted = sorted(matches)
                latest_name = matches_sorted[-1]

            fobj = res.files[latest_name]

            # Best-effort URI extraction across xnatpy versions
            uri = (
                getattr(fobj, "uri", None)
                or getattr(fobj, "_uri", None)
                or getattr(fobj, "data_uri", None)
                or getattr(fobj, "URI", None)
            )

            if uri is None:
                # Fallback: try to expose something still useful for debugging
                try:
                    uri = str(getattr(fobj, "xnat_uri"))
                except Exception:
                    uri = None

            if uri is None:
                log_error(
                    f"Could not determine URI for file: {latest_name} (scan_id={scan_id}, resource={scan_resource_dir_name})",
                    func_name,
                )
                return None

            return uri

    except Exception:
        log_error("Unhandled exception during execution", func_name)
        return None


def get_id_from_nifti_location_csv(
    session_id: str,
    resource_name: str = "NIFTI_LOCATION",
    csv_suffix: str = "NIFTILOCATION.csv",
    id_col: str = "ID",
):
    """
    Returns:
      - scalar ID value (first unique value) OR None on failure
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        msg = " I AM HERE!!!!!!!!!!!!!!!!!"
        log_error(msg, func_name)

        with xnat.connect(XNAT_HOST, user=XNAT_USER, password=XNAT_PASS) as conn:

            if session_id not in conn.experiments:
                log_error("Session ID not found on XNAT", func_name)
                return None

            exp = conn.experiments[session_id]

            if resource_name not in exp.resources:
                log_error(f'Resource "{resource_name}" not found', func_name)
                return None

            res = exp.resources[resource_name]

            csv_files = [
                fname for fname in res.files.keys()
                if str(fname).endswith(csv_suffix)
            ]

            if not csv_files:
                log_error(f'No file ending with "{csv_suffix}" found', func_name)
                return None

            csv_name = sorted(csv_files)[0]

            # --- FIX: download using xnatpy download() ---
            import tempfile, os

            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                    tmp_path = tmp.name

                # xnatpy file object supports download(path)
                res.files[csv_name].download(tmp_path)

                df = pd.read_csv(tmp_path)

            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

            # --- extract ID ---
            if id_col not in df.columns:
                log_error(f'Column "{id_col}" not found in {csv_name}. ', func_name)
                return None

            series = df[id_col].dropna()
            if series.empty:
                log_error(f'Column "{id_col}" exists but has no valid values', func_name)
                return None

            return series.unique()[0]

    except Exception:
        log_error("Unhandled exception during execution", func_name)
        return None



def call_apply_single_row_csv_to_table(session_id, csv_file):
    """
    Wrapper to:
    - resolve project/subject from session_id
    - use project_id as table name
    - apply single-row CSV to DB table
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        # Resolve project & subject
        project_id, subject_label = given_sessionid_get_project_n_subjectids(session_id)

        if not project_id:
            raise ValueError(f"Could not resolve project for session_id={session_id}")

        table_name = project_id  # as per your design

        result = apply_single_row_csv_to_table(
            # engine=ENGINE,                    # global/shared engine
            csv_file=csv_file,
            table_name=table_name,
            session_id=session_id,      # identifier column in CSV & DB
        )

        return result

    except Exception as e:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f"[{ts}] Function: {func_name}\n"
            f"session_id={session_id}\n"
            f"csv_file={csv_file}\n"
            f"Error: {e}\n"
            f"Traceback:\n{traceback.format_exc()}\n"
            f"{'-'*80}\n"
        )
        with open(LOG_FILE, "a") as f:
            f.write(msg)

        # Propagate or return sentinel (choose one)
        raise
        # or: return None

def given_sessionid_get_project_n_subjectids(session_id):
    """
    Given an XNAT experiment/session ID, return (project_id, subject_id).
    Logs any exception with function name and timestamp.
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        with xnat.connect(XNAT_HOST, user=XNAT_USER, password=XNAT_PASS) as connection:
            exp = connection.experiments[session_id]
            subj = exp.subject
            # print("Project ID:", exp.project)  # project identifier
            # print("Subject ID:", subj.id)  # system-wide subject id
            # print("Subject Label:", subj.label)
            return exp.project, subj.label

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        error_msg = (
            f"[{timestamp}] "
            f"Function: {func_name}\n"
            f"Session ID: {session_id}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}\n"
            f"{'-'*80}\n"
        )

        with open(LOG_FILE, "a") as f:
            f.write(error_msg)

        # Safe failure return (important for batch pipelines)
        return None, None



def given_csvfile_proj_subjids_append(csvfile, session_id):
    """
    Read CSV with session IDs, append/overwrite PROJECT_ID and SUBJECT_ID columns.
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        df = pd.read_csv(csvfile)

        # Ensure columns exist
        df["PROJECT_ID"] = ""
        df["SUBJECT_ID"] = ""

        for idx, row in df.iterrows():
            # session_id = str(row.get(session_col, "")).strip()
            if not session_id:
                continue

            try:
                proj, subj = given_sessionid_get_project_n_subjectids(session_id)
                df.at[idx, "PROJECT_ID"] = "" if proj is None else proj
                df.at[idx, "SUBJECT_ID"] = "" if subj is None else subj
            except Exception:
                df.at[idx, "PROJECT_ID"] = ""
                df.at[idx, "SUBJECT_ID"] = ""

        out_csv = csvfile #.replace(".csv", "_with_proj_subj.csv")
        df.to_csv(out_csv, index=False)
        return out_csv

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        err = (
            f"[{timestamp}] Function: {func_name}\n"
            f"CSV file: {csvfile}\n"
            f"Error: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}\n"
            f"{'-' * 80}\n"
        )
        with open(LOG_FILE, "a") as f:
            f.write(err)
        return None
def get_scan_dicom_metadata_from_first_dicom(
    session_id: str,
    scan_id: str,
    dicom_resource_name: str = "DICOM",
    bash_safe: bool = True,
):
    """
    Given session_id and scan_id:
      - find scan's resource folder (default: "DICOM")
      - download the first DICOM file from that resource
      - read DICOM header tags using SimpleITK (GDCM)
      - return tuple:
          (acquisition_site, acquisition_datetime, scanner, body_part, kvp)

    Returns:
      (site, acq_dt, scanner, body_part, kvp) OR (None, None, None, None, None) on failure
    """
    func_name = inspect.currentframe().f_code.co_name

    def _clean(v):
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        # Collapse whitespace
        s = " ".join(s.split())
        if bash_safe:
            s = s.replace(" ", "_")
        return s

    def _get_tag(reader, tag, default=None):
        try:
            if reader.HasMetaDataKey(tag):
                return reader.GetMetaData(tag)
        except Exception:
            pass
        return default

    try:
        if not session_id or not str(session_id).strip():
            log_error("session_id is empty", func_name)
            return None, None, None, None, None
        if not scan_id or not str(scan_id).strip():
            log_error("scan_id is empty", func_name)
            return None, None, None, None, None

        import tempfile
        import os
        import SimpleITK as sitk

        # -------------------------
        # 1) Find first DICOM file in scan resource
        # -------------------------
        with xnat.connect(XNAT_HOST, user=XNAT_USER, password=XNAT_PASS) as conn:
            if session_id not in conn.experiments:
                log_error(f"Session ID not found on XNAT: {session_id}", func_name)
                return None, None, None, None, None

            exp = conn.experiments[session_id]

            if scan_id not in exp.scans:
                log_error(f"Scan ID not found in session: {scan_id}", func_name)
                return None, None, None, None, None

            scan = exp.scans[scan_id]

            if dicom_resource_name not in scan.resources:
                log_error(
                    f'Scan resource "{dicom_resource_name}" not found for scan_id={scan_id}',
                    func_name,
                )
                return None, None, None, None, None

            res = scan.resources[dicom_resource_name]

            # list all files (keys may include paths)
            all_files = [str(k) for k in res.files.keys()]

            # Prefer .dcm (case-insensitive), otherwise take the first file
            dcm_files = [f for f in all_files if f.lower().endswith(".dcm")]
            candidates = sorted(dcm_files) if dcm_files else sorted(all_files)

            if not candidates:
                log_error(
                    f'No files found in scan resource "{dicom_resource_name}" (scan_id={scan_id})',
                    func_name,
                )
                return None, None, None, None, None

            first_name = candidates[0]

            # download to temp file
            tmp_path = None
            try:
                suffix = ".dcm" if first_name.lower().endswith(".dcm") else ".bin"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp_path = tmp.name

                res.files[first_name].download(tmp_path)

            except Exception:
                log_error(
                    f"Failed to download first DICOM file: {first_name} (scan_id={scan_id})",
                    func_name,
                )
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                return None, None, None, None, None

        # -------------------------
        # 2) Read DICOM header tags using SimpleITK (no pixel load)
        # -------------------------
        try:
            # Use ImageFileReader for metadata
            reader = sitk.ImageFileReader()
            reader.SetFileName(tmp_path)

            # Ensure GDCM for DICOM
            image_io = sitk.GDCMImageIO()
            reader.SetImageIO(image_io)

            # Only read header info (fast)
            reader.ReadImageInformation()

            # DICOM tags (group|element)
            institution = _get_tag(reader, "0008|0080")  # InstitutionName
            acq_dt = _get_tag(reader, "0008|002a")       # AcquisitionDateTime

            # Fallback if AcquisitionDateTime missing:
            if not acq_dt:
                acq_date = _get_tag(reader, "0008|0022")  # AcquisitionDate
                acq_time = _get_tag(reader, "0008|0032")  # AcquisitionTime
                if acq_date and acq_time:
                    acq_dt = f"{acq_date}_{acq_time}"
                else:
                    # Additional fallbacks (often present)
                    study_date = _get_tag(reader, "0008|0020")  # StudyDate
                    study_time = _get_tag(reader, "0008|0030")  # StudyTime
                    if study_date and study_time:
                        acq_dt = f"{study_date}_{study_time}"

            manufacturer = _get_tag(reader, "0008|0070")  # Manufacturer
            model = _get_tag(reader, "0008|1090")         # ManufacturerModelName
            body_part = _get_tag(reader, "0018|0015")     # BodyPartExamined
            kvp = _get_tag(reader, "0018|0060")           # KVP

            scanner = None
            if manufacturer and model:
                scanner = f"{manufacturer}_{model}"
            else:
                scanner = manufacturer or model

            # Clean for Bash if requested
            institution = _clean(institution)
            acq_dt = _clean(acq_dt)
            scanner = _clean(scanner)
            body_part = _clean(body_part)
            kvp = _clean(kvp)

            return institution, acq_dt, scanner, body_part, kvp

        finally:
            # cleanup temp file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    except Exception:
        log_error("Unhandled exception during get_scan_dicom_metadata_from_first_dicom", func_name)
        return None, None, None, None, None


def get_session_label_from_session_id(session_id: str):
    """
    Given an XNAT experiment/session ID, return the session label.

    Returns:
      - session_label (str) OR None on failure
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        if not session_id or not str(session_id).strip():
            log_error("session_id is empty", func_name)
            return None

        with xnat.connect(XNAT_HOST, user=XNAT_USER, password=XNAT_PASS) as conn:
            if session_id not in conn.experiments:
                log_error(f"Session ID not found on XNAT: {session_id}", func_name)
                return None

            exp = conn.experiments[session_id]
            return exp.label

    except Exception:
        log_error("Unhandled exception during get_session_label_from_session_id", func_name)
        return None


def upload_file_to_project_resource(
    project_id: str,
    resource_label: str,
    local_file_path: str,
    remote_filename: str , #| None = None,
    verify: bool = True,
    use_multipart: bool = True,
    log_file: str = "xnat_upload_errors.log"
) -> dict:
    """
    Upload a local file into a PROJECT-level resource folder in XNAT.

    Target REST shape (project resources):
      - Create resource folder:
          PUT  /data/projects/{project-id}/resources/{resource-label}
      - Upload file:
          PUT  /data/projects/{project-id}/resources/{resource-label}/files/{filename}
        (either multipart 'file=@...' OR raw body with ?inbody=true)
    See XNAT API docs. :contentReference[oaicite:0]{index=0}

    Returns:
      {"ok": True, "project_id": ..., "resource_label": ..., "filename": ..., "uploaded_to": ...}
      or {"ok": False, "error": "...", "where": "..."} on failure (and logs traceback).
    """
    xnat_host=XNAT_HOST
    username = XNAT_USER
    password = XNAT_PASS
    try:
        if not os.path.isfile(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")

        filename = remote_filename or os.path.basename(local_file_path)

        # XNAT expects paths under /data/...
        resource_base = f"/data/projects/{project_id}/resources/{resource_label}"
        upload_endpoint = f"{resource_base}/files/{filename}"

        with xnat.connect(xnat_host, user=username, password=password, verify=verify) as sess:
            # xnatpy session exposes requests-like methods; use interface.* if present
            http = getattr(sess, "interface", sess)

            # 1) Ensure the project resource folder exists (idempotent PUT)
            r1 = http.put(resource_base)
            if hasattr(r1, "ok") and not r1.ok:
                raise RuntimeError(f"Failed creating/ensuring resource folder: {r1.status_code} {getattr(r1, 'text', '')}")

            # 2) Upload the file
            with open(local_file_path, "rb") as f:
                if use_multipart:
                    # multipart form upload (like: curl -F "file=@x")
                    r2 = http.put(upload_endpoint, files={"file": f})
                else:
                    # raw body upload requires inbody=true
                    r2 = http.put(upload_endpoint, params={"inbody": "true"}, data=f)

            if hasattr(r2, "ok") and not r2.ok:
                raise RuntimeError(f"Upload failed: {r2.status_code} {getattr(r2, 'text', '')}")

        return {
            "ok": True,
            "project_id": project_id,
            "resource_label": resource_label,
            "filename": filename,
            "uploaded_to": upload_endpoint,
        }

    except Exception as e:
        # Write full traceback to a log file (so you can debug auth/permissions/paths)
        try:
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write("\n" + "=" * 80 + "\n")
                lf.write(f"Error uploading to XNAT project resource\n")
                lf.write(f"xnat_host={xnat_host}\nproject_id={project_id}\nresource_label={resource_label}\nfile={local_file_path}\n")
                lf.write(f"Exception: {repr(e)}\n")
                lf.write(traceback.format_exc())
        except Exception:
            pass

        return {"ok": False, "where": "upload_file_to_project_resource", "error": str(e)}


