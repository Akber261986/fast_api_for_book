import re
from typing import Dict, List, Tuple
from pathlib import Path


def extract_headers_from_markdown(content: str) -> List[Dict[str, str]]:
    """
    Extract headers from markdown content to identify sections
    """
    headers = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Match markdown headers (h1 to h6)
        header_match = re.match(r'^(#{1,6})\s+(.+)', line.strip())
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            headers.append({
                'line_number': i,
                'level': level,
                'title': title,
                'content': title  # For now, just use the title
            })

    return headers


def extract_title_from_markdown(content: str) -> str:
    """
    Extract the main title from markdown content
    """
    # First try to find a YAML frontmatter title
    frontmatter_match = re.search(r'---\s*\n.*?title:\s*(.+?)\s*\n.*?---', content, re.DOTALL | re.IGNORECASE)
    if frontmatter_match:
        return frontmatter_match.group(1).strip()

    # Then try to find the first H1 header
    h1_match = re.match(r'^#\s+(.+)$', content.strip(), re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    # If no title found, return first 50 characters of content
    clean_content = re.sub(r'\s+', ' ', content.strip())
    return clean_content[:50] + "..." if len(clean_content) > 50 else clean_content


def parse_markdown_sections(content: str) -> List[Dict[str, str]]:
    """
    Parse markdown content into sections based on headers
    """
    lines = content.split('\n')
    sections = []
    current_section = {
        'title': 'Introduction',  # Default title for content before first header
        'content': '',
        'start_line': 0
    }

    for i, line in enumerate(lines):
        header_match = re.match(r'^(#{1,6})\s+(.+)', line.strip())

        if header_match:
            # Save the previous section if it has content
            if current_section['content'].strip():
                sections.append(current_section)

            # Start a new section
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            current_section = {
                'title': title,
                'content': f"{title}\n",  # Start with the header
                'start_line': i,
                'level': level
            }
        else:
            current_section['content'] += f"{line}\n"

    # Add the last section
    if current_section['content'].strip():
        sections.append(current_section)

    return sections


def clean_markdown_content(content: str) -> str:
    """
    Remove markdown syntax to get plain text content
    """
    # Remove headers but keep the text
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

    # Remove emphasis markers
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italic
    content = re.sub(r'__(.*?)__', r'\1', content)      # Bold
    content = re.sub(r'_(.*?)_', r'\1', content)        # Italic

    # Remove inline code
    content = re.sub(r'`(.*?)`', r'\1', content)

    # Remove links [text](url) -> text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

    # Remove images ![alt](url) -> alt
    content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)

    # Remove blockquotes
    content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)

    # Remove list markers
    content = re.sub(r'^\s*[\*\-\+]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)

    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n', '\n\n', content)  # Multiple blank lines to single
    content = content.strip()

    return content


def extract_metadata_from_frontmatter(content: str) -> Dict[str, str]:
    """
    Extract metadata from YAML frontmatter if present
    """
    metadata = {}

    # Look for YAML frontmatter
    frontmatter_match = re.match(r'---\s*\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_content = frontmatter_match.group(1)

        # Parse simple key-value pairs
        for line in frontmatter_content.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')

    return metadata


def parse_markdown_file(file_path: str) -> Dict[str, str]:
    """
    Parse a markdown file and return its components
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return {
        'content': content,
        'title': extract_title_from_markdown(content),
        'headers': extract_headers_from_markdown(content),
        'sections': parse_markdown_sections(content),
        'metadata': extract_metadata_from_frontmatter(content),
        'clean_content': clean_markdown_content(content)
    }


def split_markdown_by_headings(content: str, max_chunk_size: int = 1000) -> List[str]:
    """
    Split markdown content into chunks based on headings, respecting max chunk size
    """
    sections = parse_markdown_sections(content)
    chunks = []

    for section in sections:
        section_content = section['content']

        if len(section_content) <= max_chunk_size:
            chunks.append(section_content)
        else:
            # If the section is too large, split it further
            sub_chunks = split_large_text(section_content, max_chunk_size)
            chunks.extend(sub_chunks)

    return chunks


def split_large_text(text: str, max_chunk_size: int, overlap: int = 100) -> List[str]:
    """
    Split a large text into chunks of approximately max_chunk_size with overlap
    """
    if len(text) <= max_chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chunk_size

        if end >= len(text):
            # Last chunk, include everything remaining
            chunks.append(text[start:])
            break

        # Find a good break point (try to break at sentence or word boundary)
        chunk = text[start:end]
        break_point = find_break_point(chunk)

        if break_point and break_point < len(chunk):
            actual_end = start + break_point
            chunks.append(text[start:actual_end])
            start = actual_end - overlap  # Apply overlap
        else:
            chunks.append(chunk)
            start = end - overlap

        # Ensure we're making progress to avoid infinite loops
        if start <= end - overlap:
            start = end  # Fallback to avoid infinite loops

    # Remove empty chunks
    chunks = [chunk for chunk in chunks if chunk.strip()]

    return chunks


def find_break_point(text: str) -> int:
    """
    Find a good break point in text (at sentence or word boundaries)
    """
    # Look for sentence endings first
    for i in range(len(text) - 1, -1, -1):
        if text[i] in '.!?':
            return i + 1

    # If no sentence ending found, look for word boundaries
    for i in range(len(text) - 1, -1, -1):
        if text[i] in ' \t\n':
            return i + 1

    # If no good break point found, return length of text (no break needed)
    return len(text)