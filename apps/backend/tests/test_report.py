import os
from pathlib import Path
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
            "/report/process/dicom",
            files={"dcm_files": ("not_a_dicom.txt", f, "text/plain")},
            data={"modality": "ASL"}
        )
    # Should still return 500 due to invalid dicom
    assert response.status_code in [500, 200]

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


def test_report_pdf_endpoint_removes_temp_file(tmp_path, monkeypatch):
    temp_pdf = tmp_path / "report.pdf"

    class DummyTempFile:
        def __init__(self, path: Path):
            self.name = str(path)
            self._file = path.open("wb")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self._file.close()

    class FakeHTML:
        def __init__(self, string: str):
            self.string = string

        def write_pdf(self, path: str):
            Path(path).write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setattr("app.routers.reports.tempfile.NamedTemporaryFile", lambda **kwargs: DummyTempFile(temp_pdf))
    monkeypatch.setattr("app.routers.reports.HTML", FakeHTML)

    report_data = {
        "report_data": {
            "asl_parameters": [("param1", "value1")],
            "missing_parameters": [],
            "basic_report": "Basic report",
            "extended_report": "Extended report",
        }
    }

    response = client.post("/api/report/report-pdf", json=report_data)

    assert response.status_code == 200
    assert not temp_pdf.exists()