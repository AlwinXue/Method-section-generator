import os
import tempfile

from pyaslreport.core.config import Config
from pyaslreport.converters.dicom_to_nifti_converter import DICOM2NiFTIConverter


def test_config_normalizes_tmp_paths_to_platform_temp_dir():
    config_loader = Config("/tmp/does-not-matter")
    paths = {
        "upload_folder": "/tmp/upload",
        "basic_report": "/tmp/basic_report.txt",
        "json_report": "backend/tests/test_data/expected_response.json",
    }

    normalized = config_loader._normalize_temp_paths(paths)

    assert normalized["upload_folder"] == os.path.join(tempfile.gettempdir(), "upload")
    assert normalized["basic_report"] == os.path.join(tempfile.gettempdir(), "basic_report.txt")
    assert normalized["json_report"] == "backend/tests/test_data/expected_response.json"


def test_converter_uses_platform_temp_dir_default():
    converted_files_location = DICOM2NiFTIConverter.convert.__defaults__[0]
    assert converted_files_location is None
