# backend/utils/helpers.py
"""
Helper utility functions - Schema v2.0 Compatible
Updated: 2025-11-10
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
import uuid


def generate_ticket_id() -> str:
    """
    Generate unique ticket ID
    
    Format: TKT-YYYYMMDD-XXXX
    Example: TKT-20251110-A3F9
    
    Returns:
        Ticket ID string
    """
    today = date.today().strftime("%Y%m%d")
    unique = uuid.uuid4().hex[:4].upper()
    return f"TKT-{today}-{unique}"


def generate_schedule_id(route_id: str, departure_time: str) -> str:
    """
    Generate schedule ID from route and time
    
    Format: SCH-{ROUTE_ID}-{TIME}
    Example: SCH-R001-0630
    
    Args:
        route_id: Route identifier
        departure_time: Departure time (HH:MM format)
        
    Returns:
        Schedule ID string
    """
    time_str = departure_time.replace(":", "")
    return f"SCH-{route_id}-{time_str}"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    
    Args:
        lat1: Latitude of point 1
        lon1: Longitude of point 1
        lat2: Latitude of point 2
        lon2: Longitude of point 2
        
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def get_day_name(date_obj: date) -> str:
    """
    Get day name from date
    
    Args:
        date_obj: Date object
        
    Returns:
        Day name (e.g., "monday", "tuesday")
    """
    return date_obj.strftime("%A").lower()


def is_poya_day(date_obj: date) -> bool:
    """
    Check if date is a Poya (full moon) day
    
    Note: This is a simplified check. For production, use an accurate
    lunar calendar API or predefined list of Poya dates.
    
    Args:
        date_obj: Date to check
        
    Returns:
        True if Poya day, False otherwise
    """
    # TODO: Implement accurate Poya day checking
    # For now, return False
    return False


def get_date_range(start_date: date, end_date: date) -> List[date]:
    """
    Get list of dates between start and end (inclusive)
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of date objects
    """
    dates = []
    current = start_date
    
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    
    return dates


def calculate_child_discount(base_price: float, is_child: bool = False) -> float:
    """
    Calculate discount for child tickets
    
    Children get 50% discount
    
    Args:
        base_price: Base ticket price
        is_child: Whether passenger is a child
        
    Returns:
        Discount amount
    """
    if is_child:
        return base_price * 0.5
    return 0.0


def format_currency(amount: float, currency: str = "LKR") -> str:
    """
    Format amount as currency string
    
    Args:
        amount: Amount to format
        currency: Currency code (default: LKR)
        
    Returns:
        Formatted string (e.g., "LKR 1,234.50")
    """
    return f"{currency} {amount:,.2f}"


def paginate_results(
    items: List,
    page: int = 1,
    page_size: int = 50
) -> Dict:
    """
    Paginate a list of items
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Dictionary with pagination info
    """
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        "items": items[start_idx:end_idx],
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def sanitize_string(text: str) -> str:
    """
    Sanitize string for safe storage/display
    
    Args:
        text: String to sanitize
        
    Returns:
        Sanitized string
    """
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Replace multiple spaces with single space
    text = " ".join(text.split())
    
    return text


def parse_station_list(station_string: str) -> List[str]:
    """
    Parse comma-separated station list
    
    Args:
        station_string: Comma-separated station IDs
        
    Returns:
        List of station IDs
    """
    if not station_string:
        return []
    
    return [s.strip() for s in station_string.split(",") if s.strip()]


def build_station_string(station_ids: List[str]) -> str:
    """
    Build comma-separated station string from list
    
    Args:
        station_ids: List of station IDs
        
    Returns:
        Comma-separated string
    """
    return ",".join(station_ids)