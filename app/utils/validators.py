import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator


def validate_file_path(file_path: str) -> bool:
    """
    Validate if the given string is a valid file path
    """
    # Basic file path validation
    if not file_path or len(file_path) > 1000:
        return False

    # Check for invalid characters (platform independent)
    invalid_chars = '<>:"|?*'
    if any(char in file_path for char in invalid_chars):
        return False

    # Basic pattern for file paths
    pattern = r'^[a-zA-Z0-9_\-./\\ ]+\.([a-zA-Z0-9]+)$'
    return bool(re.match(pattern, file_path))


def validate_url(url: str) -> bool:
    """
    Validate if the given string is a valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_api_key_format(api_key: str, provider: str = "generic") -> bool:
    """
    Validate API key format based on the provider
    """
    if not api_key:
        return False

    if provider == "gemini":
        # Gemini API keys typically start with "AIza"
        return api_key.startswith("AIza") and len(api_key) > 10
    elif provider == "openai":
        # OpenAI API keys typically start with "sk-"
        return api_key.startswith("sk-") and len(api_key) > 10
    elif provider == "qdrant":
        # Qdrant API keys are typically UUIDs or long alphanumeric strings
        return len(api_key) >= 16
    else:
        # Generic validation - just check length
        return len(api_key) >= 8

    return True


class FileValidationResult(BaseModel):
    """Model for file validation results"""
    is_valid: bool
    file_path: str
    extension: Optional[str] = None
    error_message: Optional[str] = None


class URLValidationResult(BaseModel):
    """Model for URL validation results"""
    is_valid: bool
    url: str
    domain: Optional[str] = None
    error_message: Optional[str] = None


def validate_markdown_content(content: str) -> bool:
    """
    Validate if the content appears to be valid markdown
    """
    if not content or len(content.strip()) == 0:
        return False

    # Basic checks for markdown elements
    markdown_indicators = [
        '# ', '## ', '### ',  # Headers
        '* ', '- ', '+ ',     # Lists
        '[', ']',             # Links
        '*', '_',             # Emphasis
        '`', '```',           # Code
        '---',               # Horizontal rules
    ]

    # Check if content contains at least one markdown element
    has_markdown = any(indicator in content for indicator in markdown_indicators)

    # Also check if content is not just whitespace
    has_content = len(content.strip()) > 0

    return has_content and has_markdown


def validate_embedding_vector(embedding: List[float], expected_dimension: int = 768) -> bool:
    """
    Validate embedding vector dimensions and content
    """
    if not isinstance(embedding, list) or len(embedding) != expected_dimension:
        return False

    # Check if all values are floats/numbers
    for value in embedding:
        if not isinstance(value, (int, float)) or not (-2.0 <= value <= 2.0):  # Typical embedding range
            return False

    return True


def validate_search_filters(filters: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate search filter parameters
    Returns a dictionary of validation errors if any
    """
    errors = {}

    for key, value in filters.items():
        # Validate key format (should be alphanumeric with underscores/hyphens)
        if not re.match(r'^[a-zA-Z0-9_-]+$', key):
            errors[key] = f"Invalid filter key format: {key}"

        # Validate value type (should be string, number, or boolean)
        if not isinstance(value, (str, int, float, bool)):
            errors[key] = f"Invalid filter value type for key {key}"

    return errors


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def safe_validate_json(json_str: str) -> bool:
    """
    Safely validate if a string is valid JSON
    """
    try:
        import json
        json.loads(json_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_content_chunk_size(text: str, max_size: int = 1000) -> bool:
    """
    Validate that content chunk is within acceptable size limits
    """
    if not isinstance(text, str):
        return False

    return 10 <= len(text) <= max_size  # At least 10 chars, max is configurable


# Pydantic validators as reusable functions
def validate_file_path_pydantic(cls, v):
    """Reusable validator for Pydantic models"""
    if not validate_file_path(v):
        raise ValueError(f'Invalid file path: {v}')
    return v


def validate_url_pydantic(cls, v):
    """Reusable validator for Pydantic models"""
    if not validate_url(v):
        raise ValueError(f'Invalid URL: {v}')
    return v


def validate_markdown_content_pydantic(cls, v):
    """Reusable validator for Pydantic models"""
    if not validate_markdown_content(v):
        raise ValueError('Content does not appear to be valid markdown')
    return v


def validate_embedding_vector_pydantic(cls, v, expected_dimension: int = 768):
    """Reusable validator for Pydantic models"""
    if not validate_embedding_vector(v, expected_dimension):
        raise ValueError(f'Invalid embedding vector, expected {expected_dimension} dimensions')
    return v