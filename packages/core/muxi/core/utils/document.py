"""
Document handling utilities for MUXI Framework.

This module provides functions for loading and processing documents.
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
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: The text to split
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # If this is not the last chunk, try to find a good break point
        if end < text_length:
            # Try to break at paragraph
            paragraph_break = text.rfind('\n\n', start, end)
            if paragraph_break != -1 and paragraph_break > start + chunk_size // 2:
                end = paragraph_break + 2  # Include the newlines
            else:
                # Try to break at sentence
                sentence_breaks = ['.', '!', '?', '\n']
                for sep in sentence_breaks:
                    sentence_break = text.rfind(sep, start, end)
                    if sentence_break != -1 and sentence_break > start + chunk_size // 2:
                        end = sentence_break + 1  # Include the separator
                        break

        chunks.append(text[start:end])
        start = max(start, end - overlap)  # Ensure we move forward

    return chunks
