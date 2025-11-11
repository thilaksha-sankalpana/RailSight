# backend/utils/validators.py
"""
Data validation utilities - Schema v2.0 Compatible
Updated: 2025-11-10
"""
import re
from datetime import date, time as time_type
from typing import Optional
from backend.utils.errors import ValidationError


def validate_nic(nic: str) -> bool:
    """
    Validate Sri Lankan NIC format
    
    Formats:
    - Old: 9 digits + V/X (e.g., 123456789V)
    - New: 12 digits (e.g., 200012345678)
    
    Args:
        nic: NIC string to validate
        
    Returns:
        True if valid, raises ValidationError if not
    """
    old_format = re.match(r'^\d{9}[VvXx]$', nic)
    new_format = re.match(r'^\d{12}$', nic)
    
    if not (old_format or new_format):
        raise ValidationError(
            "Invalid NIC format. Use format: 123456789V or 200012345678"
        )
    return True


def validate_passport(passport: str) -> bool:
    """
    Validate passport number format
    
    General format: 6-10 alphanumeric characters
    
    Args:
        passport: Passport string to validate
        
    Returns:
        True if valid, raises ValidationError if not
    """
    if not re.match(r'^[A-Z0-9]{6,10}$', passport):
        raise ValidationError(
            "Invalid passport format. Use 6-10 uppercase letters and numbers"
        )
    return True


def validate_nic_or_passport(identifier: str) -> bool:
    """
    Validate either NIC or Passport
    
    Args:
        identifier: NIC or Passport string
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If neither format is valid
    """
    try:
        validate_nic(identifier)
        return True
    except ValidationError:
        pass
    
    try:
        validate_passport(identifier)
        return True
    except ValidationError:
        raise ValidationError(
            "Invalid NIC/Passport. Must be Sri Lankan NIC or valid passport number"
        )


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format
    
    Accepts: +94712345678, 0712345678, 712345678
    
    Args:
        phone: Phone number string
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If format is invalid
    """
    # Remove spaces and hyphens
    cleaned = re.sub(r'[\s\-]', '', phone)
    
    # Check format
    if not re.match(r'^(\+94|0)?[1-9]\d{8}$', cleaned):
        raise ValidationError(
            "Invalid phone number. Use format: +94712345678 or 0712345678"
        )
    return True


def validate_station_id(station_id: str) -> bool:
    """
    Validate station ID format (3-10 uppercase letters)
    
    Args:
        station_id: Station ID string
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If format is invalid
    """
    if not re.match(r'^[A-Z]{3,10}$', station_id):
        raise ValidationError(
            "Invalid station ID. Use 3-10 uppercase letters (e.g., CMB, KDY)"
        )
    return True


def validate_train_id(train_id: str) -> bool:
    """
    Validate train ID format
    
    Args:
        train_id: Train ID string
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If format is invalid
    """
    if not re.match(r'^[A-Z0-9]{3,20}$', train_id):
        raise ValidationError(
            "Invalid train ID. Use 3-20 uppercase letters and numbers"
        )
    return True


def validate_time_range(start_time: time_type, end_time: time_type) -> bool:
    """
    Validate that end time is after start time
    
    Args:
        start_time: Start time
        end_time: End time
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If end time is not after start time
    """
    if end_time <= start_time:
        raise ValidationError("End time must be after start time")
    return True


def validate_compartment_distribution(
    first_class: int,
    second_class: int,
    third_class: int,
    total_cars: int
) -> bool:
    """
    Validate compartment class distribution
    
    Args:
        first_class: Number of 1st class compartments
        second_class: Number of 2nd class compartments
        third_class: Number of 3rd class compartments
        total_cars: Total cars in train
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If distribution is invalid
    """
    # Check non-negative
    if any(x < 0 for x in [first_class, second_class, third_class]):
        raise ValidationError("Compartment counts cannot be negative")
    
    # Check total matches
    total = first_class + second_class + third_class
    if total != total_cars:
        raise ValidationError(
            f"Total compartments ({total}) must equal total cars ({total_cars})"
        )
    
    # Ensure at least one 3rd class
    if third_class < 1:
        raise ValidationError("Must have at least one 3rd class compartment")
    
    return True


def validate_price_structure(
    first_class_fee: float,
    second_class_fee: float,
    third_class_fee: float
) -> bool:
    """
    Validate ticket price structure
    
    Ensures: 1st class > 2nd class > 3rd class
    
    Args:
        first_class_fee: 1st class price
        second_class_fee: 2nd class price
        third_class_fee: 3rd class price
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If price structure is invalid
    """
    if not (first_class_fee > second_class_fee > third_class_fee > 0):
        raise ValidationError(
            "Invalid price structure. Must be: 1st > 2nd > 3rd > 0"
        )
    return True