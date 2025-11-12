# backend/utils/calendar_service.py
"""
Calendarific API Integration for Holiday and Poya Day Detection
Handles fetching and caching of Sri Lankan holidays and Poya days
"""
import requests
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Set
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

# Calendarific API Configuration
CALENDARIFIC_API_KEY = "0MIR1HOzNIDSGlnih06PG6QffEMb4O4r"
CALENDARIFIC_BASE_URL = "https://calendarific.com/api/v2"
COUNTRY_CODE = "LK"  # Sri Lanka

# Cache for holiday data (in-memory cache)
_holiday_cache: Dict[int, Dict[str, any]] = {}

class CalendarService:
    """Service for handling calendar operations including holidays and Poya days"""

    @staticmethod
    def fetch_holidays_for_year(year: int) -> Optional[Dict]:
        """
        Fetch all holidays for a given year from Calendarific API

        Args:
            year: The year to fetch holidays for

        Returns:
            Dictionary containing holiday data or None if request fails
        """
        url = f"{CALENDARIFIC_BASE_URL}/holidays"
        params = {
            "api_key": CALENDARIFIC_API_KEY,
            "country": COUNTRY_CODE,
            "year": year
        }

        try:
            logger.info(f"Fetching holidays for year {year} from Calendarific API")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("meta", {}).get("code") == 200:
                logger.info(f"Successfully fetched {len(data.get('response', {}).get('holidays', []))} holidays for {year}")
                return data.get("response", {})
            else:
                logger.error(f"Calendarific API error: {data.get('meta', {}).get('error_detail')}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch holidays from Calendarific: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching holidays: {e}")
            return None

    @staticmethod
    def get_holidays_for_year(year: int, force_refresh: bool = False) -> Dict[str, any]:
        """
        Get holidays for a year with caching

        Args:
            year: The year to get holidays for
            force_refresh: If True, bypass cache and fetch fresh data

        Returns:
            Dictionary with holiday information
        """
        # Check cache first
        if not force_refresh and year in _holiday_cache:
            logger.debug(f"Returning cached holidays for {year}")
            return _holiday_cache[year]

        # Fetch from API
        holiday_data = CalendarService.fetch_holidays_for_year(year)

        if holiday_data:
            # Process and cache the data
            processed_data = {
                "holidays": {},
                "poya_days": set(),
                "public_holidays": set()
            }

            for holiday in holiday_data.get("holidays", []):
                holiday_date = holiday.get("date", {}).get("iso")
                if holiday_date:
                    date_obj = datetime.fromisoformat(holiday_date).date()
                    date_str = date_obj.isoformat()

                    # Store holiday info
                    if date_str not in processed_data["holidays"]:
                        processed_data["holidays"][date_str] = []

                    processed_data["holidays"][date_str].append({
                        "name": holiday.get("name"),
                        "description": holiday.get("description"),
                        "type": holiday.get("type", []),
                        "primary_type": holiday.get("primary_type")
                    })

                    # Check if it's a Poya day (Full Moon Poya Day)
                    name_lower = holiday.get("name", "").lower()
                    if "poya" in name_lower or "full moon" in name_lower:
                        processed_data["poya_days"].add(date_str)
                        logger.debug(f"Found Poya day: {date_str} - {holiday.get('name')}")

                    # Check if it's a public holiday
                    holiday_types = holiday.get("type", [])
                    if "National holiday" in holiday_types or "Public holiday" in holiday_types:
                        processed_data["public_holidays"].add(date_str)

            # Cache the processed data
            _holiday_cache[year] = processed_data
            logger.info(f"Cached {len(processed_data['holidays'])} holidays, "
                       f"{len(processed_data['poya_days'])} Poya days, "
                       f"{len(processed_data['public_holidays'])} public holidays for {year}")

            return processed_data

        return {"holidays": {}, "poya_days": set(), "public_holidays": set()}

    @staticmethod
    def is_poya_day(check_date: date) -> bool:
        """
        Check if a given date is a Poya day (Full Moon day)

        Args:
            check_date: Date to check

        Returns:
            True if the date is a Poya day, False otherwise
        """
        year = check_date.year
        holidays = CalendarService.get_holidays_for_year(year)
        date_str = check_date.isoformat()

        is_poya = date_str in holidays.get("poya_days", set())
        if is_poya:
            logger.debug(f"{check_date} is a Poya day")

        return is_poya

    @staticmethod
    def is_public_holiday(check_date: date) -> bool:
        """
        Check if a given date is a public holiday

        Args:
            check_date: Date to check

        Returns:
            True if the date is a public holiday, False otherwise
        """
        year = check_date.year
        holidays = CalendarService.get_holidays_for_year(year)
        date_str = check_date.isoformat()

        is_holiday = date_str in holidays.get("public_holidays", set())
        if is_holiday:
            logger.debug(f"{check_date} is a public holiday")

        return is_holiday

    @staticmethod
    def get_holiday_info(check_date: date) -> List[Dict]:
        """
        Get detailed information about holidays on a given date

        Args:
            check_date: Date to get holiday info for

        Returns:
            List of holiday information dictionaries
        """
        year = check_date.year
        holidays = CalendarService.get_holidays_for_year(year)
        date_str = check_date.isoformat()

        return holidays.get("holidays", {}).get(date_str, [])

    @staticmethod
    def get_day_type(check_date: date) -> Dict[str, bool]:
        """
        Get comprehensive day type information

        Args:
            check_date: Date to check

        Returns:
            Dictionary with day type flags
        """
        return {
            "is_poya_day": CalendarService.is_poya_day(check_date),
            "is_public_holiday": CalendarService.is_public_holiday(check_date),
            "day_of_week": check_date.strftime("%A").lower(),
            "holiday_info": CalendarService.get_holiday_info(check_date)
        }

    @staticmethod
    def preload_current_year():
        """
        Preload holidays for the current year to improve performance
        Should be called at application startup
        """
        current_year = datetime.now().year
        CalendarService.get_holidays_for_year(current_year)
        logger.info(f"Preloaded holidays for {current_year}")

    @staticmethod
    def clear_cache():
        """Clear the holiday cache"""
        global _holiday_cache
        _holiday_cache = {}
        logger.info("Holiday cache cleared")


# Convenience functions for easy imports
def is_poya_day(check_date: date) -> bool:
    """Check if date is a Poya day"""
    return CalendarService.is_poya_day(check_date)


def is_holiday(check_date: date) -> bool:
    """Check if date is a public holiday"""
    return CalendarService.is_public_holiday(check_date)


def get_day_type(check_date: date) -> Dict[str, bool]:
    """Get day type information"""
    return CalendarService.get_day_type(check_date)


def preload_holidays():
    """Preload holidays for current year"""
    CalendarService.preload_current_year()
