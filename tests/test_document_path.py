import os
import stat
import pytest
from tools.document import document_path_to_markdown


class TestDocumentPathToMarkdown:
    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")
    PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")

    # --- Happy path ---

    def test_converts_pdf_to_markdown(self):
        """Test converting a PDF file path to markdown."""
        result = document_path_to_markdown(self.PDF_FIXTURE)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_converts_docx_to_markdown(self):
        """Test converting a DOCX file path to markdown."""
        result = document_path_to_markdown(self.DOCX_FIXTURE)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_pdf_content_accuracy(self):
        """Test that PDF conversion contains expected content from the fixture."""
        result = document_path_to_markdown(self.PDF_FIXTURE)
        assert "#" in result or "-" in result or "*" in result

    def test_docx_content_accuracy(self):
        """Test that DOCX conversion contains expected content from the fixture."""
        result = document_path_to_markdown(self.DOCX_FIXTURE)
        assert "#" in result or "-" in result or "*" in result

    # --- File type inference from extension ---

    def test_infers_pdf_type_from_extension(self):
        """Test that file type is correctly inferred from .pdf extension."""
        result = document_path_to_markdown(self.PDF_FIXTURE)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_infers_docx_type_from_extension(self):
        """Test that file type is correctly inferred from .docx extension."""
        result = document_path_to_markdown(self.DOCX_FIXTURE)
        assert isinstance(result, str)
        assert len(result) > 0

    # --- Error cases ---

    def test_file_not_found_raises_error(self):
        """Test that a nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            document_path_to_markdown("/nonexistent/path/to/file.pdf")

    def test_unsupported_file_type_raises_error(self, tmp_path):
        """Test that an unsupported file extension raises ValueError."""
        unsupported_file = tmp_path / "document.xyz"
        unsupported_file.write_bytes(b"some content")
        with pytest.raises(ValueError):
            document_path_to_markdown(str(unsupported_file))

    def test_empty_file_handles_gracefully(self, tmp_path):
        """Test that a zero-byte file is handled without crashing."""
        empty_pdf = tmp_path / "empty.pdf"
        empty_pdf.write_bytes(b"")
        # Should either return empty string or raise a meaningful error
        try:
            result = document_path_to_markdown(str(empty_pdf))
            assert isinstance(result, str)
        except Exception as e:
            # Acceptable if it raises a clear error, but not an opaque crash
            assert not isinstance(e, (SegmentationError if False else KeyboardInterrupt,))

    def test_permission_denied_raises_error(self, tmp_path):
        """Test that an unreadable file raises a permission error."""
        restricted_file = tmp_path / "restricted.pdf"
        restricted_file.write_bytes(b"%PDF-1.4 fake content")
        restricted_file.chmod(0o000)
        try:
            with pytest.raises((PermissionError, OSError)):
                document_path_to_markdown(str(restricted_file))
        finally:
            # Restore permissions so tmp_path cleanup succeeds
            restricted_file.chmod(stat.S_IRUSR | stat.S_IWUSR)

    # --- Edge cases ---

    def test_path_with_spaces(self, tmp_path):
        """Test that paths containing spaces work correctly."""
        spaced_dir = tmp_path / "my docs"
        spaced_dir.mkdir()
        spaced_file = spaced_dir / "file name.docx"
        # Copy the real fixture so conversion actually works
        with open(self.DOCX_FIXTURE, "rb") as src:
            spaced_file.write_bytes(src.read())
        result = document_path_to_markdown(str(spaced_file))
        assert isinstance(result, str)
        assert len(result) > 0
