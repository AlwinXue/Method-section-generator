import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

# filepath: /home/ibrahim/MyPc/Projects/GSoC/ASL-Parameter-Generator/apps/backend/tests/test_report.py

client = TestClient(app)

def test_get_report_bids_no_files():
    response = client.post("/api/report/process/bids", data={"modality": "ASL"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_get_report_dicom_no_files():
    response = client.post("/api/report/process/dicom", data={"modality": "ASL"})
    assert response.status_code == 400
    assert response.json()["detail"] == "No DICOM files provided"

def test_get_report_dicom_with_invalid_file(tmp_path):
    # Create a dummy non-dicom file
    file_path = tmp_path / "not_a_dicom.txt"
    file_path.write_text("not a dicom")
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/report/process/dicom",
            files={"dcm_files": ("not_a_dicom.txt", f, "text/plain")},
            data={"modality": "ASL"}
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "No valid DICOM files provided"

def test_report_pdf_endpoint():
    # Minimal valid report_data for rendering
    report_data = {
        "report_data": {
            "asl_parameters": {"param1": "value1"},
            "other": "test"
        }
    }
    response = client.post("/api/report/report-pdf", json=report_data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"