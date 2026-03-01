from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from gettext import gettext as _

from telegram.ext import CallbackQueryHandler

from pdf_bot.analytics import TaskType
from pdf_bot.models import FileData, FileTaskResult, TaskData

from .abstract_document_processor import AbstractDocumentProcessor


class DocumentToPdfData(FileData):
    pass


class DocumentToPdfProcessor(AbstractDocumentProcessor):
    @property
    def task_type(self) -> TaskType:
        return TaskType.doc_to_pdf

    @property
    def task_data(self) -> TaskData:
        return TaskData(_("Convert to PDF"), DocumentToPdfData)

    @property
    def handler(self) -> CallbackQueryHandler:
        return CallbackQueryHandler(self.process_file, pattern=DocumentToPdfData)

    @asynccontextmanager
    async def process_file_task(
        self, file_data: FileData
    ) -> AsyncGenerator[FileTaskResult, None]:
        async with self.document_service.convert_document_to_pdf(file_data.id) as path:
            yield FileTaskResult(path)
