from pdf_bot.file_processor import AbstractFileTaskProcessor

from .abstract_document_processor import AbstractDocumentProcessor


class DocumentTaskProcessor(AbstractFileTaskProcessor):
    @property
    def processor_type(self) -> type[AbstractDocumentProcessor]:
        return AbstractDocumentProcessor
