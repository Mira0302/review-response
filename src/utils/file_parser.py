"""文件解析工具：支持 PDF、Word、Markdown、纯文本"""
import os
from pathlib import Path


def extract_text_from_pdf(filepath: str) -> str:
    """提取PDF文本（优先pdfplumber，降级PyPDF2）"""
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception:
        pass

    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        raise ValueError(f"PDF解析失败：{e}")


def extract_text_from_docx(filepath: str) -> str:
    """提取Word文档文本"""
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Word文档解析失败：{e}")


def extract_text(filepath: str) -> tuple[str, str]:
    """
    自动识别文件类型并提取文本

    Returns:
        (text_content, file_type_label) 如 ("论文正文...", "PDF文件")
    """
    ext = Path(filepath).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(filepath), "PDF文件"
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(filepath), "Word文档"
    elif ext in (".md", ".markdown"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read(), "Markdown文件"
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read(), "纯文本文件"
    else:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read(), "文本文件"
        except Exception:
            raise ValueError(f"不支持的文件格式：{ext}")
