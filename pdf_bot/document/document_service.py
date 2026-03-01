import subprocess
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from gettext import gettext as _
from pathlib import Path

from loguru import logger

from pdf_bot.io_internal import IOService
from pdf_bot.telegram_internal import TelegramService

from .exceptions import DocumentConversionError


class DocumentService:
    SUPPORTED_EXTENSIONS = frozenset({".doc", ".docx", ".ppt", ".pptx", ".odt"})

    def __init__(
        self,
        io_service: IOService,
        telegram_service: TelegramService,
    ) -> None:
        self.io_service = io_service
        self.telegram_service = telegram_service

    @asynccontextmanager
    async def convert_document_to_pdf(self, file_id: str) -> AsyncGenerator[Path, None]:
        async with self.telegram_service.download_file_to_dir(file_id) as file_path:
            with self.io_service.create_temp_directory("doc_convert") as out_dir:
                try:
                    result = subprocess.run(  # noqa: S603
                        [
                            "libreoffice",
                            "--headless",
                            "--norestore",
                            "--convert-to",
                            "pdf",
                            "--outdir",
                            str(out_dir),
                            str(file_path),
                        ],
                        capture_output=True,
                        timeout=120,
                        check=False,
                    )

                    if result.returncode != 0:
                        logger.error(
                            "LibreOffice conversion failed.\nStdout: {stdout}\nStderr: {stderr}",
                            stdout=result.stdout.decode("utf-8", errors="replace"),
                            stderr=result.stderr.decode("utf-8", errors="replace"),
                        )
                        raise DocumentConversionError

                    # Find the generated PDF file in the output directory
                    pdf_files = list(out_dir.glob("*.pdf"))
                    if not pdf_files:
                        raise DocumentConversionError

                    yield pdf_files[0]
                except subprocess.TimeoutExpired as e:
                    logger.error("LibreOffice conversion timed out")
                    raise DocumentConversionError from e
                except DocumentConversionError:
                    raise
                except Exception as e:
                    logger.exception("Unexpected error during document conversion")
                    raise DocumentConversionError from e
