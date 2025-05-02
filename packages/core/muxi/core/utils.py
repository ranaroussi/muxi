"""
Utility functions for the MUXI Framework.
"""

import os
from typing import List


def load_document(file_path: str) -> str:
    """
    Load a document from a file.

    Args:
        file_path: Path to the file

    Returns:
        The document content as a string

    Raises:
        FileNotFoundError: If the file does not exist
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # Check file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Simple text file handling for now
    if ext in ['.txt', '.md', '.markdown']:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    # TODO: Add support for PDF, DOCX, etc.
    # This would require additional dependencies

    # Default fallback - try to read as text
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(f"Unsupported file format: {ext}")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks with overlap.

    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if not text:
        return []

    # Simple paragraph-based chunking
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # Skip empty paragraphs
        if not paragraph.strip():
            continue

        # If adding this paragraph would exceed chunk size, save current chunk and start a new one
        if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep some overlap from the end of the previous chunk
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
            current_chunk = overlap_text + paragraph + "\n\n"
        else:
            current_chunk += paragraph + "\n\n"

    # Add the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
