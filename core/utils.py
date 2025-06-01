from django.core.cache import cache
from django.db.models import QuerySet
from django.conf import settings
import hashlib
import logging

logger = logging.getLogger(__name__)

def get_cached_queryset(queryset, cache_key, timeout=300):
    """
    Get a cached queryset or execute the query and cache the results.
    
    Args:
        queryset: The queryset to execute and cache
        cache_key: The key to use for caching
        timeout: Cache timeout in seconds (default: 5 minutes)
        
    Returns:
        The queryset results, either from cache or freshly executed
    """
    if not settings.DEBUG:  # Only use caching in non-debug mode
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached_data
    
    # Execute the queryset
    if isinstance(queryset, QuerySet):
        result = list(queryset)
    else:
        result = queryset
        
    # Cache the result
    if not settings.DEBUG:
        cache.set(cache_key, result, timeout)
        logger.debug(f"Cached data with key: {cache_key}, timeout: {timeout}s")
    
    return result

def generate_cache_key(prefix, *args, **kwargs):
    """
    Generate a unique cache key based on the prefix and arguments.
    
    Args:
        prefix: A string prefix for the cache key
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
        
    Returns:
        A unique cache key string
    """
    key_parts = [prefix]
    
    # Add positional args
    for arg in args:
        key_parts.append(str(arg))
    
    # Add keyword args (sorted for consistency)
    for k in sorted(kwargs.keys()):
        key_parts.append(f"{k}={kwargs[k]}")
    
    # Join all parts and create a hash
    key_string = ":".join(key_parts)
    return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"

def invalidate_model_cache(model_name, instance_id=None):
    """
    Invalidate cache entries related to a specific model or instance.
    
    Args:
        model_name: The name of the model (e.g., 'service', 'order')
        instance_id: Optional ID of a specific instance to invalidate
    """
    if instance_id:
        # Invalidate specific instance cache
        pattern = f"{model_name}_{instance_id}_*"
    else:
        # Invalidate all caches for this model
        pattern = f"{model_name}_*"
    
    # Find and delete matching cache keys
    # Note: This is a simplified approach and may not work with all cache backends
    # For Redis, you would use the SCAN command to find matching keys
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)
    else:
        logger.warning(f"Cache backend does not support pattern deletion: {pattern}")
        # For backends that don't support pattern deletion, you would need
        # to maintain a registry of cache keys to invalidate

