import PyPDF2
from io import BytesIO
from src.logger import logger


class DocumentProcessor:
    @staticmethod
    def extract_from_pdf(file_content: bytes) -> str:
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    @staticmethod
    def extract_from_txt(file_content: bytes) -> str:
        try:
            return file_content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting TXT: {e}")
            raise
    
    @staticmethod
    def extract_from_markdown(file_content: bytes) -> str:
        try:
            return file_content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting Markdown: {e}")
            raise
    
    @staticmethod
    def detect_and_extract(filename: str, file_content: bytes) -> str:
        if filename.lower().endswith('.pdf'):
            return DocumentProcessor.extract_from_pdf(file_content)
        elif filename.lower().endswith('.txt'):
            return DocumentProcessor.extract_from_txt(file_content)
        elif filename.lower().endswith('.md'):
            return DocumentProcessor.extract_from_markdown(file_content)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
