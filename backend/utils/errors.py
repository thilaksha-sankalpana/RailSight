# backend/utils/errors.py
"""
Custom exception classes and error handlers - Schema v2.0 Compatible
Updated: 2025-11-10
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

logger = logging.getLogger(__name__)


# ============= CUSTOM EXCEPTIONS =============

class TCDAFSException(Exception):
    """Base exception for TCDAFS application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundError(TCDAFSException):
    """Exception raised when a resource is not found"""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationError(TCDAFSException):
    """Exception raised for validation errors"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ConflictError(TCDAFSException):
    """Exception raised for resource conflicts"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_409_CONFLICT)


class UnauthorizedError(TCDAFSException):
    """Exception raised for unauthorized access"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(TCDAFSException):
    """Exception raised for forbidden access"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


# ============= ERROR HANDLERS =============

async def tcdafs_exception_handler(request: Request, exc: TCDAFSException):
    """Handler for custom TCDAFS exceptions"""
    logger.error(f"TCDAFS Error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "path": str(request.url)
        }
    )


async def validation_exception_handler(request: Request, exc: HTTPException):
    """Handler for validation exceptions"""
    logger.warning(f"Validation Error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "ValidationError",
            "message": exc.detail,
            "path": str(request.url)
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler for SQLAlchemy database errors"""
    logger.error(f"Database Error: {str(exc)}")
    
    # Handle integrity errors (unique constraint, foreign key, etc.)
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "IntegrityError",
                "message": "Database constraint violation",
                "path": str(request.url)
            }
        )
    
    # Generic database error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DatabaseError",
            "message": "An error occurred while processing your request",
            "path": str(request.url)
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler for unexpected exceptions"""
    logger.critical(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "path": str(request.url)
        }
    )


# ============= VALIDATION HELPERS =============

def validate_resource_exists(resource, resource_name: str, identifier: str):
    """
    Validate that a resource exists, raise exception if not
    
    Args:
        resource: The queried resource (can be None)
        resource_name: Name of the resource type (e.g., "Train", "Station")
        identifier: The identifier used to query (e.g., ID)
        
    Raises:
        ResourceNotFoundError: If resource is None
    """
    if resource is None:
        raise ResourceNotFoundError(resource_name, identifier)
    return resource


def validate_date_range(start_date, end_date):
    """
    Validate that date range is valid
    
    Args:
        start_date: Start date
        end_date: End date
        
    Raises:
        ValidationError: If dates are invalid
    """
    if end_date and start_date > end_date:
        raise ValidationError("Start date must be before or equal to end date")