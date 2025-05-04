# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Utilities - Common Helper Functions
# Description:  General utility functions used throughout the Muxi framework
# Role:         Provides reusable functionality for common operations
# Usage:        Imported by various components that need utility functions
# Author:       Muxi Framework Team
#
# The utils.py file provides a collection of utility functions that are used
# across the Muxi framework. These functions handle common operations such as:
#
# 1. File Operations
#    - Document loading from various file formats
#    - Content extraction and processing
#    - Format detection and handling
#
# 2. Text Processing
#    - Text chunking with overlap for context preservation
#    - Paragraph handling and processing
#    - Size management for LLM context windows
#
# These utilities are designed to be reusable, efficient, and handle edge
# cases appropriately. They abstract common patterns used throughout the
# framework to maintain consistency and reduce code duplication.
#
# Example usage:
#
#   from muxi.core.utils import load_document, chunk_text
#
#   # Load a document from a file
#   content = load_document("path/to/document.txt")
#
#   # Chunk the content for processing
#   chunks = chunk_text(content, chunk_size=2000, overlap=150)
# =============================================================================

import os
from typing import List


def load_document(file_path: str) -> str:
    """
    Load a document from a file.

    This function reads the content of a file and returns it as a string.
    It handles different file types based on their extensions, with special
    handling for common text formats.

    Args:
        file_path: Path to the file to be loaded. Can be absolute or relative path.
            Supports various text formats including .txt, .md, and .markdown.

    Returns:
        The document content as a string, ready for processing.

    Raises:
        FileNotFoundError: If the file does not exist or cannot be accessed.
        ValueError: If the file format is not supported or cannot be read as text.
            Binary files and certain document formats may not be supported.
    """
    # Extract the file extension for format detection
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()  # Normalize extension to lowercase for consistent comparison

    # Verify file exists before attempting to read
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Handle known text file formats
    if ext in [".txt", ".md", ".markdown"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # TODO: Add support for PDF, DOCX, etc.
    # This would require additional dependencies

    # Default fallback - attempt to read as text for unknown formats
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # If we can't decode as text, the format is likely unsupported
        raise ValueError(f"Unsupported file format: {ext}")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks with overlap.

    This function divides a large text into smaller chunks while maintaining
    context between chunks through overlapping content. It attempts to use
    paragraph breaks as natural division points to preserve semantic coherence.

    Args:
        text: The text to chunk into smaller pieces. Can be any string content
            including documents, transcripts, or other textual data.
        chunk_size: Maximum size (in characters) of each chunk. Default is 1000,
            which works well for most embedding and processing purposes.
        overlap: Number of characters to overlap between consecutive chunks. This
            helps maintain context across chunk boundaries. Default is 200 characters.

    Returns:
        List of text chunks with specified overlap. Each chunk is a string of
        size ≤ chunk_size, with the last overlap characters of each chunk
        appearing at the beginning of the next chunk (when applicable).
        Returns an empty list if input text is empty.
    """
    # Handle empty input case
    if not text:
        return []

    # Split text into paragraphs using double newlines as separators
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # Skip empty paragraphs to avoid unnecessary processing
        if not paragraph.strip():
            continue

        # Check if adding this paragraph would exceed the chunk size limit
        if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
            # Save the current chunk if it would exceed the size limit
            chunks.append(current_chunk.strip())

            # Create overlap by including the end of the previous chunk
            # If the current chunk is smaller than the overlap size, use the entire chunk
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""

            # Start a new chunk with the overlap text and the current paragraph
            current_chunk = overlap_text + paragraph + "\n\n"
        else:
            # If we're under the size limit, add the paragraph to the current chunk
            current_chunk += paragraph + "\n\n"

    # Add the final chunk if it contains any content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
