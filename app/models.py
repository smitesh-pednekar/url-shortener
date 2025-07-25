from datetime import datetime
import threading
from typing import Dict, Optional

class URLMapping:
    """Data model for storing URL mappings and analytics."""
    
    def __init__(self, original_url: str, short_code: str):
        self.original_url = original_url
        self.short_code = short_code
        self.clicks = 0
        self.created_at = datetime.utcnow()
    
    def increment_clicks(self):
        """Thread-safe method to increment click count."""
        self.clicks += 1
    
    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            'url': self.original_url,
            'short_code': self.short_code,
            'clicks': self.clicks,
            'created_at': self.created_at.isoformat()
        }

class URLStore:
    """Thread-safe in-memory storage for URL mappings."""
    
    def __init__(self):
        self._mappings: Dict[str, URLMapping] = {}
        self._lock = threading.RLock()
    
    def save_mapping(self, mapping: URLMapping) -> bool:
        """Save a URL mapping. Returns False if short_code already exists."""
        with self._lock:
            if mapping.short_code in self._mappings:
                return False
            self._mappings[mapping.short_code] = mapping
            return True
    
    def get_mapping(self, short_code: str) -> Optional[URLMapping]:
        """Retrieve a URL mapping by short code."""
        with self._lock:
            return self._mappings.get(short_code)
    
    def increment_clicks(self, short_code: str) -> bool:
        """Increment click count for a short code. Returns False if not found."""
        with self._lock:
            mapping = self._mappings.get(short_code)
            if mapping:
                mapping.increment_clicks()
                return True
            return False
    
    def short_code_exists(self, short_code: str) -> bool:
        """Check if short code already exists."""
        with self._lock:
            return short_code in self._mappings


url_store = URLStore()
