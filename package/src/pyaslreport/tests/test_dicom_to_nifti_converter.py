import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pyaslreport.converters.dicom_to_nifti_converter import DICOM2NiFTIConverter


def test_convert_copies_files_to_temp_dir_and_runs_dcm2niix(tmp_path):
    dicom_file = tmp_path / "input1.dcm"
    dicom_file.write_bytes(b"fake dicom")
    output_dir = tmp_path / "converted"
    observed_temp_dir = {"path": None}

    def fake_dcmread(_path):
        def fake_get(tag, default=None):
            if tag == (0x0020, 0x0011):
                return SimpleNamespace(value=1)
            if tag == (0x0029, 0x1020):
                return SimpleNamespace(value=b"lRepetitions = 4")
            return default

        return SimpleNamespace(get=fake_get)

    def fake_run(cmd, check, stdout, stderr):
        temp_dir = Path(cmd[-1])
        observed_temp_dir["path"] = temp_dir
        assert any(temp_dir.iterdir())

        output_dir.mkdir(exist_ok=True)
        (output_dir / "series.nii.gz").write_bytes(b"fake nifti")
        (output_dir / "series.json").write_text(json.dumps({"SeriesNumber": 1}))
        return SimpleNamespace(stdout=b"", stderr=b"")

    with patch("pyaslreport.converters.dicom_to_nifti_converter.pydicom.dcmread", side_effect=fake_dcmread), \
         patch("pyaslreport.converters.dicom_to_nifti_converter.subprocess.run", side_effect=fake_run):
        converted_files, converted_filenames, nifti_file, file_format, error = DICOM2NiFTIConverter.convert(
            [str(dicom_file)],
            converted_files_location=str(output_dir),
        )

    assert observed_temp_dir["path"] is not None
    assert converted_filenames == ["series.json"]
    assert converted_files == [str(output_dir / "series.json")]
    assert nifti_file == str(output_dir / "series.nii.gz")
    assert file_format == "dicom"
    assert error is None

    json_data = json.loads((output_dir / "series.json").read_text())
    assert json_data["lRepetitions"] == "4"
