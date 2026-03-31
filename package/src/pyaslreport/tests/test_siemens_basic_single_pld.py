from unittest.mock import patch

from pyaslreport.sequences.siemens.asl.siemens_basic_single_pld import SiemensBasicSinglePLD


def test_extract_bids_metadata_returns_metadata_and_context_tuple():
    sequence = SiemensBasicSinglePLD({})

    with patch.object(SiemensBasicSinglePLD, "_extract_common_metadata", return_value={"Manufacturer": "Siemens"}), \
         patch.object(SiemensBasicSinglePLD, "_extract_siemens_common_metadata", return_value={"MRAcquisitionType": "3D"}):
        metadata, asl_context = sequence.extract_bids_metadata()

    assert metadata == {
        "Manufacturer": "Siemens",
        "MRAcquisitionType": "3D",
    }
    assert asl_context == ["deltaM", "m0scan"]
