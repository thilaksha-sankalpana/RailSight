# backend/schemas.py
"""
Pydantic schemas for request/response validation - Version 2.0
Updated to match the revised database schema (2025-11-10)
Enhanced with comprehensive validation rules
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import uuid

# =====================================================
# USER SCHEMAS
# =====================================================

class UserCreate(BaseModel):
    """Schema for creating new user"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2)
    contact_number: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    role: str = Field(default="operator", pattern="^(admin|operator|ticket_agent|manager)$")

class UserUpdate(BaseModel):
    """Schema for updating user"""
    full_name: Optional[str] = None
    contact_number: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """Schema for user response"""
    id: uuid.UUID
    email: str
    full_name: str
    contact_number: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v)
        }

    @classmethod
    def model_validate(cls, obj):
        if hasattr(obj, 'id') and isinstance(obj.id, uuid.UUID):
            obj_dict = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
            obj_dict['id'] = str(obj.id)
            return cls(**obj_dict)
        return super().model_validate(obj)

class ChangePassword(BaseModel):
    """Schema for password change"""
    old_password: str
    new_password: str = Field(..., min_length=8)

# =====================================================
# STATION SCHEMAS
# =====================================================

class StationCreate(BaseModel):
    """Schema for creating station"""
    station_id: str = Field(..., pattern="^[A-Z0-9]{1,10}$")
    station_name: str = Field(..., min_length=2, max_length=255)

class StationUpdate(BaseModel):
    """Schema for updating station"""
    station_name: Optional[str] = Field(None, min_length=2, max_length=255)

class StationResponse(BaseModel):
    """Schema for station response"""
    station_id: str
    station_name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# =====================================================
# ROUTE SCHEMAS
# =====================================================

class RouteCreate(BaseModel):
    """Schema for creating route"""
    route_id: str = Field(..., pattern="^[A-Z0-9]{1,10}$")
    route_name: str = Field(..., min_length=2, max_length=255)
    route: str = Field(..., min_length=5, max_length=500)

class RouteUpdate(BaseModel):
    """Schema for updating route"""
    route_name: Optional[str] = Field(None, min_length=2, max_length=255)
    route: Optional[str] = Field(None, min_length=5, max_length=500)

class RouteResponse(BaseModel):
    """Schema for route response"""
    route_id: str
    route_name: str
    route: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# =====================================================
# TRAIN MODEL SCHEMAS
# =====================================================

class TrainModelCreate(BaseModel):
    """Schema for creating train model"""
    model_id: str = Field(..., pattern="^[A-Z0-9]{1,10}$")
    model_name: str = Field(..., min_length=2, max_length=255)
    model_type: str = Field(..., min_length=2, max_length=100)
    manufacturer: str = Field(..., min_length=2, max_length=255)
    country_of_origin: str = Field(..., min_length=2, max_length=100)
    operational_units: int = Field(..., ge=0)
    compartments_per_unit: int = Field(..., gt=0)
    total_compartments_assigned_per_model: int = Field(..., ge=0)
    seating_passengers_per_compartment: int = Field(..., ge=0)
    standing_passengers_per_compartment: int = Field(..., ge=0)
    total_passengers_per_compartment: int = Field(..., ge=0)
    # Route assignments (R01-R09)
    r01: bool = False
    r02: bool = False
    r03: bool = False
    r04: bool = False
    r05: bool = False
    r06: bool = False
    r07: bool = False
    r08: bool = False
    r09: bool = False

class TrainModelUpdate(BaseModel):
    """Schema for updating train model"""
    model_name: Optional[str] = None
    operational_units: Optional[int] = Field(None, ge=0)
    # Route assignments (R01-R09)
    r01: Optional[bool] = None
    r02: Optional[bool] = None
    r03: Optional[bool] = None
    r04: Optional[bool] = None
    r05: Optional[bool] = None
    r06: Optional[bool] = None
    r07: Optional[bool] = None
    r08: Optional[bool] = None
    r09: Optional[bool] = None

class TrainModelResponse(BaseModel):
    """Schema for train model response"""
    model_id: str
    model_name: str
    model_type: str
    manufacturer: str
    country_of_origin: str
    operational_units: int
    compartments_per_unit: int
    seating_passengers_per_compartment: int
    standing_passengers_per_compartment: int
    total_passengers_per_compartment: int
    # Route assignments (R01-R09)
    r01: bool
    r02: bool
    r03: bool
    r04: bool
    r05: bool
    r06: bool
    r07: bool
    r08: bool
    r09: bool

    class Config:
        from_attributes = True

# =====================================================
# OPERATIONAL TRAIN SCHEMAS
# =====================================================

class OperationalTrainCreate(BaseModel):
    """Schema for creating operational train"""
    train_id: str = Field(..., pattern="^[A-Z0-9-]{3,20}$")
    model_id: str
    compartments_per_unit: int = Field(..., gt=0)
    status: str = Field(default="Active", pattern="^(Active|Inactive|Maintenance|Retired)$")

class OperationalTrainUpdate(BaseModel):
    """Schema for updating operational train"""
    status: Optional[str] = Field(None, pattern="^(Active|Inactive|Maintenance|Retired)$")

class OperationalTrainResponse(BaseModel):
    """Schema for operational train response"""
    train_id: str
    model_id: str
    compartments_per_unit: int
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# =====================================================
# SCHEDULE SCHEMAS
# =====================================================

class ScheduleCreate(BaseModel):
    """Schema for creating schedule"""
    train_schedule_id: str = Field(..., pattern="^[A-Z0-9]{3,20}$")
    route_id: str
    train_schedule: str = Field(..., min_length=2, max_length=255)
    origin_station_id: str
    origin_station: str
    origin_departure: time
    destination_station_id: str
    destination_station: str
    destination_departure: time
    monday: bool = False
    tuesday: bool = False
    wednesday: bool = False
    thursday: bool = False
    friday: bool = False
    saturday: bool = False
    sunday: bool = False
    poya_day: bool = False
    holiday: bool = False
    status: str = Field(default="Active", pattern="^(Active|Inactive|Cancelled|Delayed)$")

    @field_validator('origin_station_id', 'destination_station_id')
    @classmethod
    def validate_different_stations(cls, v, info):
        if 'origin_station_id' in info.data and info.field_name == 'destination_station_id':
            if v == info.data['origin_station_id']:
                raise ValueError('Origin and destination stations must be different')
        return v

    @field_validator('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'poya_day', 'holiday')
    @classmethod
    def validate_at_least_one_day(cls, v, info):
        # This will be checked after all fields are set
        if info.field_name == 'holiday':  # Last field
            days = [
                info.data.get('monday', False),
                info.data.get('tuesday', False),
                info.data.get('wednesday', False),
                info.data.get('thursday', False),
                info.data.get('friday', False),
                info.data.get('saturday', False),
                info.data.get('sunday', False),
                info.data.get('poya_day', False),
                v  # holiday
            ]
            if not any(days):
                raise ValueError('At least one operating day must be selected')
        return v

class ScheduleUpdate(BaseModel):
    """Schema for updating schedule"""
    origin_departure: Optional[time] = None
    destination_departure: Optional[time] = None
    status: Optional[str] = Field(None, pattern="^(Active|Inactive|Cancelled|Delayed)$")
    monday: Optional[bool] = None
    tuesday: Optional[bool] = None
    wednesday: Optional[bool] = None
    thursday: Optional[bool] = None
    friday: Optional[bool] = None
    saturday: Optional[bool] = None
    sunday: Optional[bool] = None
    poya_day: Optional[bool] = None
    holiday: Optional[bool] = None

class ScheduleResponse(BaseModel):
    """Schema for schedule response"""
    train_schedule_id: str
    route_id: str
    train_schedule: str
    origin_station: str
    destination_station: str
    origin_departure: time
    destination_departure: time
    status: str
    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool
    poya_day: bool
    holiday: bool

    class Config:
        from_attributes = True

# =====================================================
# SCHEDULE BY STATION SCHEMAS
# =====================================================

class ScheduleByStationCreate(BaseModel):
    """Schema for creating schedule by station"""
    train_schedule_id: str
    train_schedule: str
    origin_station_id: str
    origin_station: str
    origin_departure: time
    destination_station_id: str
    destination_station: str
    destination_departure: time
    duration: timedelta

class ScheduleByStationResponse(BaseModel):
    """Schema for schedule by station response"""
    id: int
    train_schedule_id: str
    train_schedule: str
    origin_station: str
    destination_station: str
    origin_departure: time
    destination_departure: time
    duration: timedelta

    class Config:
        from_attributes = True

# =====================================================
# TICKET PRICING SCHEMAS
# =====================================================

class PriceCreate(BaseModel):
    """Schema for creating ticket price"""
    origin_station_id: str
    destination_station_id: str
    distance: Decimal = Field(..., ge=0)
    first_class_fee: Decimal = Field(default=Decimal("0"), ge=0)
    second_class_fee: Decimal = Field(default=Decimal("0"), ge=0)
    third_class_fee: Decimal = Field(default=Decimal("0"), ge=0)
    effective_from: date = Field(default_factory=date.today)
    effective_to: Optional[date] = None

    @field_validator('destination_station_id')
    @classmethod
    def validate_different_stations(cls, v, info):
        if 'origin_station_id' in info.data and v == info.data['origin_station_id']:
            raise ValueError('Origin and destination stations must be different')
        return v

    @field_validator('effective_to')
    @classmethod
    def validate_effective_dates(cls, v, info):
        if v is not None and 'effective_from' in info.data:
            if v <= info.data['effective_from']:
                raise ValueError('effective_to must be after effective_from')
        return v

class PriceUpdate(BaseModel):
    """Schema for updating ticket price"""
    first_class_fee: Optional[Decimal] = Field(None, ge=0)
    second_class_fee: Optional[Decimal] = Field(None, ge=0)
    third_class_fee: Optional[Decimal] = Field(None, ge=0)
    effective_to: Optional[date] = None

class PriceResponse(BaseModel):
    """Schema for price response"""
    id: int
    origin_station_id: str
    destination_station_id: str
    origin_station_name: Optional[str] = None
    destination_station_name: Optional[str] = None
    distance: Decimal
    first_class_fee: Decimal
    second_class_fee: Decimal
    third_class_fee: Decimal
    effective_from: date
    effective_to: Optional[date] = None

    class Config:
        from_attributes = True

class PriceCalculationRequest(BaseModel):
    """Schema for price calculation request"""
    origin_station_id: str
    destination_station_id: str
    class_: str = Field(..., pattern="^(First|Second|Third)$", alias="class")
    passengers: int = Field(..., gt=0, le=10)
    is_child: bool = False

    class Config:
        populate_by_name = True

class PriceCalculationResponse(BaseModel):
    """Schema for price calculation response"""
    base_price: Decimal
    discount: Decimal
    passengers: int
    total: Decimal

# =====================================================
# TICKET SCHEMAS
# =====================================================

class TicketCreate(BaseModel):
    """Schema for creating ticket"""
    nic: Optional[str] = Field(None, min_length=8, max_length=20)
    passport: Optional[str] = Field(None, min_length=6, max_length=20)
    contact_number: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    is_child: bool = False

    schedule_id: str
    origin_station_id: str
    destination_station_id: str
    origin_departure: time
    destination_departure: time
    schedule_date: date

    class_: str = Field(..., pattern="^(First|Second|Third)$", alias="class")
    fee: Decimal = Field(..., ge=0)

    payment_method: str = Field(
        default="Cash",
        pattern="^(Cash|Card|Online Banking|Mobile Payment)$"
    )
    booking_platform: str = Field(
        default="Website",
        pattern="^(Website|Mobile App|Counter|Kiosk)$"
    )
    issue_date: date = Field(default_factory=date.today)

    @field_validator('nic', 'passport')
    @classmethod
    def validate_passenger_id(cls, v, info):
        # At least one of nic or passport must be provided
        if info.field_name == 'passport':
            if not v and not info.data.get('nic'):
                raise ValueError('Either NIC or Passport must be provided')
        return v

    @field_validator('schedule_date')
    @classmethod
    def validate_schedule_date(cls, v, info):
        if 'issue_date' in info.data and v < info.data['issue_date']:
            raise ValueError('Schedule date cannot be before issue date')
        return v

    class Config:
        populate_by_name = True

class TicketUpdate(BaseModel):
    """Schema for updating ticket"""
    status: Optional[str] = Field(None, pattern="^(Pending|Completed|Cancelled|Refunded|No-Show)$")
    payment_status: Optional[str] = Field(None, pattern="^(Paid|Pending|Refunded|Failed|Chargedbacked)$")

class TicketResponse(BaseModel):
    """Schema for ticket response"""
    ticket_id: str
    nic: Optional[str] = None
    passport: Optional[str] = None
    is_child: bool
    schedule_date: date
    schedule_id: str
    origin_station_id: str
    destination_station_id: str
    origin_departure: time
    destination_departure: time
    class_: str = Field(..., alias="class")
    fee: Decimal
    status: str
    payment_status: str
    issue_date: date
    contact_number: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

# =====================================================
# ANALYTICS SCHEMAS
# =====================================================

class AnalyticsSummary(BaseModel):
    """Schema for analytics summary"""
    total_tickets_today: int
    total_passengers_today: int
    trains_active_today: int
    trains_scheduled_today: int
    revenue_today: Decimal
    avg_utilization: str
    active_routes: int

class WeeklySales(BaseModel):
    """Schema for weekly sales data"""
    dates: List[str]
    passengers: List[int]
    revenue: List[Decimal]

class TopRoute(BaseModel):
    """Schema for top route"""
    route_name: str
    passengers: int
    revenue: Decimal

class DailyTicketSales(BaseModel):
    """Schema for daily ticket sales"""
    dates: List[str]
    tickets: List[int]

class ScheduleStatusToday(BaseModel):
    """Schema for schedule status today"""
    completed: int
    pending: int

class ClassDistributionToday(BaseModel):
    """Schema for class distribution today"""
    first_class: int
    second_class: int
    third_class: int

# =====================================================
# DEMAND HISTORY SCHEMAS
# =====================================================

class DemandHistoryCreate(BaseModel):
    """Schema for creating demand history"""
    date: date
    schedule_id: str
    route_id: str
    train_id: Optional[str] = None
    total_passengers: int = Field(..., ge=0)
    first_class_passengers: int = Field(default=0, ge=0)
    second_class_passengers: int = Field(default=0, ge=0)
    third_class_passengers: int = Field(default=0, ge=0)
    total_capacity: int = Field(..., gt=0)
    load_factor: Optional[Decimal] = Field(None, ge=0, le=100)
    revenue: Optional[Decimal] = Field(None, ge=0)

class DemandHistoryResponse(BaseModel):
    """Schema for demand history response"""
    id: int
    date: date
    schedule_id: str
    route_id: str
    total_passengers: int
    total_capacity: int
    load_factor: Optional[Decimal] = None
    revenue: Optional[Decimal] = None

    class Config:
        from_attributes = True

# =====================================================
# ALLOCATION & FORECASTING SCHEMAS
# =====================================================

class TrainAllocationRequest(BaseModel):
    """Schema for train allocation request"""
    schedule_id: str
    date: date
    force_reallocate: bool = False

class TrainAllocationResponse(BaseModel):
    """Schema for train allocation response"""
    train_id: str
    schedule_id: str
    date: date
    reason: str
    efficiency_score: float
    first_class_compartments: int
    second_class_compartments: int
    third_class_compartments: int

class CompartmentPredictionRequest(BaseModel):
    """Schema for compartment prediction request"""
    train_id: str
    schedule_id: str
    route_id: str
    date: date

class CompartmentPredictionResponse(BaseModel):
    """Schema for compartment prediction response"""
    first_class: int
    second_class: int
    third_class: int
    confidence: float
    reasoning: str

class AllocationHistoryResponse(BaseModel):
    """Schema for allocation history response"""
    id: int
    date: date
    schedule_id: str
    train_id: str
    model_id: str
    first_class_compartments: int
    second_class_compartments: int
    third_class_compartments: int
    allocation_reason: Optional[str] = None

    class Config:
        from_attributes = True

# =====================================================
# CAPACITY MANAGEMENT SCHEMAS
# =====================================================

class DefaultScheduleCapacityCreate(BaseModel):
    """Schema for creating default schedule capacity"""
    train_schedule_id: str
    route_id: Optional[str] = None

    # First Class Configuration
    first_class_compartments: int = Field(default=0, ge=0)
    seating_passengers_per_first_class: int = Field(default=0, ge=0)
    standing_passengers_per_first_class: int = Field(default=0, ge=0)

    # Second Class Configuration
    second_class_compartments: int = Field(default=0, ge=0)
    seating_passengers_per_second_class: int = Field(default=0, ge=0)
    standing_passengers_per_second_class: int = Field(default=0, ge=0)

    # Third Class Configuration
    third_class_compartments: int = Field(default=0, ge=0)
    seating_passengers_per_third_class: int = Field(default=0, ge=0)
    standing_passengers_per_third_class: int = Field(default=0, ge=0)

class DefaultScheduleCapacityUpdate(BaseModel):
    """Schema for updating default schedule capacity"""
    first_class_compartments: Optional[int] = Field(None, ge=0)
    seating_passengers_per_first_class: Optional[int] = Field(None, ge=0)
    standing_passengers_per_first_class: Optional[int] = Field(None, ge=0)
    second_class_compartments: Optional[int] = Field(None, ge=0)
    seating_passengers_per_second_class: Optional[int] = Field(None, ge=0)
    standing_passengers_per_second_class: Optional[int] = Field(None, ge=0)
    third_class_compartments: Optional[int] = Field(None, ge=0)
    seating_passengers_per_third_class: Optional[int] = Field(None, ge=0)
    standing_passengers_per_third_class: Optional[int] = Field(None, ge=0)

class DefaultScheduleCapacityResponse(BaseModel):
    """Schema for default schedule capacity response"""
    id: int
    train_schedule_id: str
    route_id: Optional[str] = None
    first_class_compartments: int
    seating_passengers_per_first_class: int
    standing_passengers_per_first_class: int
    second_class_compartments: int
    seating_passengers_per_second_class: int
    standing_passengers_per_second_class: int
    third_class_compartments: int
    seating_passengers_per_third_class: int
    standing_passengers_per_third_class: int

    class Config:
        from_attributes = True

class SegmentCapacityResponse(BaseModel):
    """Schema for segment capacity response"""
    id: int
    segment_order: int
    origin_station: str
    destination_station: str
    first_class_load: int
    second_class_load: int
    third_class_load: int
    total_load: int
    max_first_class: int
    max_second_class: int
    max_third_class: int
    max_total: int
    available_first_class: int
    available_second_class: int
    available_third_class: int
    available_total: int

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_availability(cls, obj):
        """Create response with calculated availability"""
        return cls(
            id=obj.id,
            segment_order=obj.segment_order,
            origin_station=obj.origin_station,
            destination_station=obj.destination_station,
            first_class_load=obj.first_class_load,
            second_class_load=obj.second_class_load,
            third_class_load=obj.third_class_load,
            total_load=obj.total_load,
            max_first_class=obj.max_first_class,
            max_second_class=obj.max_second_class,
            max_third_class=obj.max_third_class,
            max_total=obj.max_total,
            available_first_class=obj.max_first_class - obj.first_class_load,
            available_second_class=obj.max_second_class - obj.second_class_load,
            available_third_class=obj.max_third_class - obj.third_class_load,
            available_total=obj.max_total - obj.total_load
        )

class ScheduleCapacityResponse(BaseModel):
    """Schema for schedule capacity response"""
    id: int
    schedule_id: str
    schedule_date: date
    train_id: Optional[str] = None
    model_id: Optional[str] = None
    allocation_status: str

    # Planned capacity
    planned_first_class_seats: int
    planned_second_class_seats: int
    planned_third_class_seats: int

    # Allocated capacity (if confirmed)
    allocated_first_class_seats: int
    allocated_second_class_seats: int
    allocated_third_class_seats: int

    # Booking counters
    booked_first_class: int
    booked_second_class: int
    booked_third_class: int
    total_bookings: int

    # Availability
    available_first_class: int
    available_second_class: int
    available_third_class: int

    # Metadata
    confirmed_at: Optional[datetime] = None
    segments: Optional[List[SegmentCapacityResponse]] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_availability(cls, obj, include_segments: bool = False):
        """Create response with calculated availability"""
        # Determine which capacity to use (allocated if confirmed, planned otherwise)
        if obj.allocation_status.value == "Confirmed":
            first_capacity = obj.allocated_first_class_seats
            second_capacity = obj.allocated_second_class_seats
            third_capacity = obj.allocated_third_class_seats
        else:
            first_capacity = obj.planned_first_class_seats
            second_capacity = obj.planned_second_class_seats
            third_capacity = obj.planned_third_class_seats

        segments = None
        if include_segments and obj.segments:
            segments = [
                SegmentCapacityResponse.from_orm_with_availability(seg)
                for seg in obj.segments
            ]

        return cls(
            id=obj.id,
            schedule_id=obj.schedule_id,
            schedule_date=obj.schedule_date,
            train_id=obj.train_id,
            model_id=obj.model_id,
            allocation_status=obj.allocation_status.value,
            planned_first_class_seats=obj.planned_first_class_seats,
            planned_second_class_seats=obj.planned_second_class_seats,
            planned_third_class_seats=obj.planned_third_class_seats,
            allocated_first_class_seats=obj.allocated_first_class_seats,
            allocated_second_class_seats=obj.allocated_second_class_seats,
            allocated_third_class_seats=obj.allocated_third_class_seats,
            booked_first_class=obj.booked_first_class,
            booked_second_class=obj.booked_second_class,
            booked_third_class=obj.booked_third_class,
            total_bookings=obj.total_bookings,
            available_first_class=first_capacity - obj.booked_first_class,
            available_second_class=second_capacity - obj.booked_second_class,
            available_third_class=third_capacity - obj.booked_third_class,
            confirmed_at=obj.confirmed_at,
            segments=segments
        )

class CapacityCheckRequest(BaseModel):
    """Schema for capacity check request"""
    schedule_id: str
    schedule_date: date
    origin_station_id: str
    destination_station_id: str
    class_: str = Field(..., pattern="^(First|Second|Third)$", alias="class")
    num_passengers: int = Field(default=1, gt=0, le=10)

    class Config:
        populate_by_name = True

class CapacityCheckResponse(BaseModel):
    """Schema for capacity check response"""
    can_book: bool
    available_capacity: int
    requested_passengers: int
    reason: Optional[str] = None
    bottleneck_segment: Optional[str] = None

class RouteCapacityResponse(BaseModel):
    """Schema for route capacity availability"""
    first_class: int
    second_class: int
    third_class: int
    total: int
    schedule_operates: bool
    allocation_status: Optional[str] = None

class ConfirmScheduleCapacityRequest(BaseModel):
    """Schema for confirming schedule capacity"""
    schedule_capacity_id: int
    train_id: str

class ConfirmScheduleCapacityResponse(BaseModel):
    """Schema for confirm schedule capacity response"""
    success: bool
    schedule_capacity_id: int
    train_id: str
    message: str
