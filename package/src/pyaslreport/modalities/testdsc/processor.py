from pyaslreport.modalities.base_processor import BaseProcessor


class DSCProcessor(BaseProcessor):
    """
    Class for processing DSC (Dynamic Susceptibility Contrast) data.
    """

    def __init__(self, data) -> None:
        """
        Initialize the DSCProcessor with the input data.

        :param data: The input DSC data to be processed.
        """
        super().__init__(data)

    def process(self) -> dict:
        """
        Process the input DSC data.

        :param data: The input DSC data to be processed.
        :return: Processed DSC data.
        """
        return {
            "modality": "DSC",
            "status": "not_implemented",
            "message": "DSC report generation is not implemented yet."
        }
