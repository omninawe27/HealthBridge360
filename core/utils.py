import re

def sanitize_cache_key(key):
    """Sanitize cache key to remove invalid characters for memcached"""
    # Replace spaces and special characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(key))
    # Ensure it doesn't start with a number or contain consecutive underscores
    sanitized = re.sub(r'^[^a-zA-Z_]+', '', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'default'
    return sanitized
