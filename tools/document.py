import os

from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pydantic import Field


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    file_path: str = Field(description="Absolute or relative path to a PDF or DOCX file"),
) -> str:
    """Convert a PDF or DOCX file to markdown-formatted text.

    Reads the file at the given path, detects the type from its extension,
    and converts the contents to markdown.

    When to use:
    - When you have a local file path to a document and need its content as markdown
    - Supports .pdf and .docx files

    When not to use:
    - When you already have the file's binary data in memory (use binary_document_to_markdown instead)

    Examples:
    >>> document_path_to_markdown("report.pdf")
    '# Report Title\\n\\nReport content...'
    >>> document_path_to_markdown("notes.docx")
    '# Notes\\n\\n- Item 1...'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    with open(file_path, "rb") as f:
        binary_data = f.read()

    file_type = ext.lstrip(".")
    return binary_document_to_markdown(binary_data, file_type)
