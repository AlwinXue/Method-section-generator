from pathlib import Path
from unittest.mock import patch

from pyaslreport.main import get_dicom_header


def test_get_dicom_header_returns_first_valid_header_without_scanning_rest(tmp_path):
    first_file = tmp_path / "first.dcm"
    second_file = tmp_path / "second.dcm"
    first_file.write_bytes(b"first")
    second_file.write_bytes(b"second")

    calls = []

    def fake_dcmread(path, stop_before_pixels=True):
        calls.append(Path(path).name)
        return {"path": Path(path).name}

    with patch("pyaslreport.main.pydicom.dcmread", side_effect=fake_dcmread):
        header = get_dicom_header(str(tmp_path))

    assert header == {"path": "first.dcm"}
    assert calls == ["first.dcm"]
