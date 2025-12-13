import re
from typing import Dict, List, Optional
import markdown
from bs4 import BeautifulSoup


def extract_text_from_markdown(markdown_content: str) -> str:
    """
    Extract plain text from Markdown content by converting to HTML and then extracting text.

    Args:
        markdown_content: Raw Markdown content

    Returns:
        Plain text extracted from the Markdown
    """
    try:
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)

        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ')

        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    except Exception as e:
        raise ValueError(f"Error parsing Markdown content: {str(e)}")


def parse_markdown_structure(markdown_content: str) -> Dict:
    """
    Parse the structure of Markdown content including headings, paragraphs, etc.

    Args:
        markdown_content: Raw Markdown content

    Returns:
        Dictionary containing structured information about the Markdown
    """
    lines = markdown_content.split('\n')

    structure = {
        'headings': [],
        'paragraphs': [],
        'lists': [],
        'code_blocks': [],
        'tables': [],
        'metadata': {}
    }

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for headings
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title = line.lstrip('# ').strip()
            structure['headings'].append({
                'level': level,
                'title': title,
                'content': ''
            })
        # Check for code blocks
        elif line.startswith('```'):
            code_block = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_block.append(lines[i])
                i += 1
            if i < len(lines):
                code_block.append(lines[i])  # Add closing ```
            structure['code_blocks'].append('\n'.join(code_block))
        # Check for list items
        elif re.match(r'^(\d+\.|-|\*)\s+', line):
            structure['lists'].append(line)
        # Regular paragraphs (non-empty lines that aren't headings or list items)
        elif line and not line.startswith('|') and not line.startswith('>'):
            structure['paragraphs'].append(line)

        i += 1

    return structure


def extract_markdown_metadata(markdown_content: str) -> Dict:
    """
    Extract metadata from Markdown content (YAML front matter or other metadata).

    Args:
        markdown_content: Raw Markdown content

    Returns:
        Dictionary containing extracted metadata
    """
    metadata = {}

    # Look for YAML front matter
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', markdown_content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        # Simple YAML parsing (for basic key-value pairs)
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')

    return metadata


def split_markdown_by_headings(markdown_content: str) -> List[Dict]:
    """
    Split Markdown content by headings to create semantic chunks.

    Args:
        markdown_content: Raw Markdown content

    Returns:
        List of dictionaries, each containing heading info and content
    """
    lines = markdown_content.split('\n')
    sections = []
    current_section = {'heading': '', 'level': 0, 'content': []}

    for line in lines:
        # Check if line is a heading
        if line.startswith('#'):
            # Save previous section if it has content
            if current_section['content'] or current_section['heading']:
                sections.append({
                    'heading': current_section['heading'],
                    'level': current_section['level'],
                    'content': '\n'.join(current_section['content']).strip()
                })

            # Start new section
            level = len(line) - len(line.lstrip('#'))
            title = line.lstrip('# ').strip()
            current_section = {
                'heading': title,
                'level': level,
                'content': []
            }
        else:
            current_section['content'].append(line)

    # Add the last section
    if current_section['content'] or current_section['heading']:
        sections.append({
            'heading': current_section['heading'],
            'level': current_section['level'],
            'content': '\n'.join(current_section['content']).strip()
        })

    return sections


def clean_markdown_content(markdown_content: str) -> str:
    """
    Clean Markdown content by removing unnecessary elements while preserving meaning.

    Args:
        markdown_content: Raw Markdown content

    Returns:
        Cleaned Markdown content
    """
    # Remove comments
    content = re.sub(r'<!--.*?-->', '', markdown_content, flags=re.DOTALL)

    # Normalize whitespace
    content = re.sub(r'\n\s*\n', '\n\n', content)  # Remove excessive empty lines
    content = content.strip()

    return content