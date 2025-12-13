import re
from typing import List
from app.core.config import settings


def semantic_chunking(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into semantically meaningful chunks with overlap.

    Args:
        text: The text to be chunked
        chunk_size: Number of tokens per chunk (default from settings)
        overlap: Number of tokens to overlap between chunks (default from settings)

    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP

    # Split text by paragraphs first
    paragraphs = text.split('\n\n')

    # Process each paragraph
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # If paragraph is too large, split it further
        if len(paragraph.split()) > chunk_size:
            sub_chunks = split_large_paragraph(paragraph, chunk_size, overlap)
            chunks.extend(sub_chunks)
        else:
            # Check if adding this paragraph would exceed chunk size
            if len(current_chunk.split()) + len(paragraph.split()) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from previous chunk
                current_chunk = get_overlap_content(current_chunk, overlap) + paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def split_large_paragraph(paragraph: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split a large paragraph into smaller chunks.

    Args:
        paragraph: The large paragraph to split
        chunk_size: Number of tokens per chunk
        overlap: Number of tokens to overlap between chunks

    Returns:
        List of text chunks
    """
    sentences = re.split(r'(?<=[.!?]) +', paragraph)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # Check if adding this sentence would exceed chunk size
        if len(current_chunk.split()) + len(sentence.split()) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            current_chunk = get_overlap_content(current_chunk, overlap) + sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def get_overlap_content(text: str, overlap_tokens: int) -> str:
    """
    Get the last 'overlap_tokens' tokens from the text.

    Args:
        text: Input text
        overlap_tokens: Number of tokens to take from the end

    Returns:
        Overlap content
    """
    words = text.split()
    if len(words) <= overlap_tokens:
        return text
    return " ".join(words[-overlap_tokens:])


def chunk_text_by_tokens(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Alternative method to chunk text by specific token counts.

    Args:
        text: The text to be chunked
        chunk_size: Number of tokens per chunk (default from settings)
        overlap: Number of tokens to overlap between chunks (default from settings)

    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP

    words = text.split()
    chunks = []

    start_idx = 0
    while start_idx < len(words):
        end_idx = min(start_idx + chunk_size, len(words))
        chunk = " ".join(words[start_idx:end_idx])
        chunks.append(chunk)

        # Move start index by chunk_size - overlap to create overlap
        start_idx = end_idx - overlap if overlap < end_idx else end_idx

        # Ensure we don't get stuck in an infinite loop
        if start_idx <= 0:
            start_idx = end_idx

    return chunks