from django.core.cache import cache
from django.db.models import QuerySet
from django.conf import settings
import hashlib
import logging


# CHANGED: Added function to get applicable year labels based on wedding date
def get_applicable_year_labels(wedding_date):
    """
    Determine which year labels apply based on a wedding date.
    
    Year mapping:
    - 2026: 2026-2027
    - 2027: 2027-2028
    - 2028: 2028-2029
    - etc.
    
    Args:
        wedding_date: A date object representing the customer's wedding date
        
    Returns:
        A list of applicable label names (e.g., ['2026-2027'] or ['2027-2028'])
    """
    if not wedding_date:
        return []
    
    year = wedding_date.year
    
    # CHANGED: Dynamic year range mapping
    year_mapping = {
        2026: '2026-2027',
        2027: '2027-2028',
        2028: '2028-2029',
        2029: '2029-2030',
        2030: '2030-2031',
    }
    
    applicable_label = year_mapping.get(year)
    return [applicable_label] if applicable_label else []
