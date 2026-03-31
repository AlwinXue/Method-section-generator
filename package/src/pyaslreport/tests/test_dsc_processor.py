from pyaslreport.modalities.testdsc.processor import DSCProcessor


def test_dsc_processor_returns_structured_placeholder_response():
    result = DSCProcessor({"modality": "DSC"}).process()

    assert result == {
        "modality": "DSC",
        "status": "not_implemented",
        "message": "DSC report generation is not implemented yet."
    }
