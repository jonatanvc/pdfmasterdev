from gettext import gettext as _


class DocumentServiceError(Exception):
    pass


class DocumentConversionError(DocumentServiceError):
    def __init__(self) -> None:
        super().__init__(_("Failed to convert your document to PDF"))
