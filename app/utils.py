import re
import random
import string
from urllib.parse import urlparse
from models import url_store

def validate_url(url: str) -> bool:
    """
    Validate if the provided string is a valid URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Basic URL pattern validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False
    
    # Additional validation using urlparse
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False

def generate_short_code(length: int = 6) -> str:
    """
    Generate a random alphanumeric short code.
    
    Args:
        length: Length of the short code (default: 6)
        
    Returns:
        str: Random alphanumeric string
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_unique_short_code(max_attempts: int = 100) -> str:
    """
    Generate a unique short code that doesn't already exist.
    
    Args:
        max_attempts: Maximum number of attempts to generate unique code
        
    Returns:
        str: Unique short code
        
    Raises:
        RuntimeError: If unable to generate unique code after max_attempts
    """
    for _ in range(max_attempts):
        short_code = generate_short_code()
        if not url_store.short_code_exists(short_code):
            return short_code
    
    raise RuntimeError("Unable to generate unique short code")

def normalize_url(url: str) -> str:
    """
    Normalize URL by ensuring it has a scheme.
    
    Args:
        url: URL to normalize
        
    Returns:
        str: Normalized URL
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url
