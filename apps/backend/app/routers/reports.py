import json
import os
import uuid
import tempfile
import pydicom
from fastapi import APIRouter, HTTPException, status, File, Form, UploadFile
from typing import List, Optional
from .data import data
from pyaslreport import generate_report, get_bids_metadata
from pyaslreport.main import get_dicom_header
from pyaslreport.enums import ModalityTypeValues
from fastapi.responses import FileResponse
from weasyprint import HTML
from app.utils.report_template import render_report_html
from app.utils.lib import default_serializer, save_upload, remove_dir

report_router = APIRouter(prefix="/report")

# create the uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

@report_router.post("/process/bids", response_model=dict, status_code=status.HTTP_200_OK)
async def get_report_bids(
        modality: Optional[str] = Form(None),
        files: Optional[List[UploadFile]] = File(None),
        nifti_file: Optional[UploadFile] = File(None),
        dcm_files: Optional[List[UploadFile]] = File(None),
):
    """
    Receives form data and two files: a NIfTI file and a DICOM file.
    """
    data = {
        "modality": ModalityTypeValues(modality) if modality else ModalityTypeValues.ASL,
        "files": [],
        "nifti_file": None,
        "dcm_files": []
    }

    report_id = str(uuid.uuid4())

    # save the incoming files to the uploads directory
    if files:
        for file in files:
            file_path = await save_upload(file, base_dir=f"uploads/{report_id}")
            data["files"].append(file_path)

    if nifti_file:
        file_path = await save_upload(nifti_file, base_dir=f"uploads/{report_id}")
        data["nifti_file"] = file_path

    if dcm_files:
        for file in dcm_files:
            file_path = await save_upload(file, base_dir=f"uploads/{report_id}/dicom")
            data["dcm_files"].append(file_path)

    try: 
        report = generate_report(data)
        await remove_dir(f"uploads/{report_id}")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    return report

@report_router.post("/process/dicom", response_model=dict, status_code=status.HTTP_200_OK)
async def get_report_dicom(
        modality: Optional[str] = Form(None),
        dcm_files: Optional[List[UploadFile]] = File(None),
):
    if not dcm_files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No DICOM files provided")

    # generate random string for report ID
    report_id = str(uuid.uuid4())
    base_dir = f"uploads/{report_id}"

    print(base_dir)

    data = {
        "modality": ModalityTypeValues(modality) if modality else ModalityTypeValues.ASL,
        "dicom_dir": f"{base_dir}/dicom"
    }

    print(data)

    for file in dcm_files:
        # check it's a dicom file 
        try:
            await save_upload(file, base_dir=data["dicom_dir"])
        except Exception as e:
            print(f"Error reading DICOM file {file.filename}: {e}")

    try:
        get_dicom_header(data["dicom_dir"])
    except (TypeError, ValueError, OSError, FileNotFoundError) as e:
        print(f"Invalid DICOM upload: {e}")
        await remove_dir(base_dir)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid DICOM files provided"
        )

    try:
        metadata, asl_context = get_bids_metadata(data)
        print("Generated BIDS metadata:", metadata)

        # save metadata to a file
        with open(f"{base_dir}/_asl.json", "w") as f:
            json.dump(metadata, f, indent=2, default=default_serializer)

        # save context to tsv it is a list and only 1 key
        with open(f"{base_dir}/_aslcontext.tsv", "w") as f:
            f.write("volume_type\n")
            for value in asl_context:
                f.write(f'"{value.lower()}"\n')

        bids_data = {
            "modality": data["modality"],
            "files": [f"{base_dir}/_asl.json", f"{base_dir}/_aslcontext.tsv"],
            "nifti_file": "app/utils/sample_nifti.nii.gz"
        }

        report = generate_report(bids_data)

        await remove_dir(base_dir)

    except Exception as e:
        print(f"Error generating report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return report


@report_router.post("/report-pdf")
async def download_pdf(report_data: dict):
    print("--------------------------------")
    print(report_data["report_data"]["asl_parameters"])
    print("--------------------------------")
    html_content = render_report_html(report_data["report_data"])
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        tmp_path = tmp.name
    return FileResponse(tmp_path, media_type="application/pdf", filename="report.pdf")

