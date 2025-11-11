# backend/models.py
"""
SQLAlchemy ORM Models for TCDAFS - Version 2.0
Updated to match the revised database schema (2025-11-10)
Clean, efficient models based on actual operational requirements
"""
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Boolean,
    ForeignKey, DECIMAL, Text, Time, Enum as SQLEnum,
    CheckConstraint, Index, Interval
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from backend.db import Base
from datetime import datetime
from typing import Optional
import enum
import uuid

# =====================================================
# ENUMS
# =====================================================

class TrainStatus(enum.Enum):
    """Train operational status"""
    Active = "Active"
    Inactive = "Inactive"
    Maintenance = "Maintenance"
    Retired = "Retired"

class ScheduleStatus(enum.Enum):
    """Train schedule status"""
    Active = "Active"
    Inactive = "Inactive"
    Cancelled = "Cancelled"
    Delayed = "Delayed"

class TicketStatus(enum.Enum):
    """Ticket status"""
    Pending = "Pending"
    Completed = "Completed"
    Cancelled = "Cancelled"
    Refunded = "Refunded"
    NoShow = "No-Show"

class PaymentStatus(enum.Enum):
    """Payment status"""
    Paid = "Paid"
    Pending = "Pending"
    Refunded = "Refunded"
    Failed = "Failed"
    Chargedbacked = "Chargedbacked"

class PaymentMethod(enum.Enum):
    """Payment method"""
    Cash = "Cash"
    Card = "Card"
    OnlineBanking = "Online Banking"
    MobilePayment = "Mobile Payment"

class BookingPlatform(enum.Enum):
    """Booking platform"""
    Website = "Website"
    MobileApp = "Mobile App"
    Counter = "Counter"
    Kiosk = "Kiosk"

class TrainClass(enum.Enum):
    """Train class"""
    First = "First"
    Second = "Second"
    Third = "Third"

class UserRole(enum.Enum):
    """User role"""
    admin = "admin"
    operator = "operator"
    ticket_agent = "ticket_agent"
    manager = "manager"

class AllocationStatus(enum.Enum):
    """Schedule capacity allocation status"""
    Provisional = "Provisional"
    Confirmed = "Confirmed"
    Completed = "Completed"
    Cancelled = "Cancelled"

# =====================================================
# AUTHENTICATION & USER MANAGEMENT
# =====================================================

class UserProfile(Base):
    """User account profiles extending Supabase Auth"""
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_number: Mapped[Optional[str]] = mapped_column(String(20))
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.operator,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
    )

# =====================================================
# CORE RAILWAY INFRASTRUCTURE
# =====================================================

class TrainStation(Base):
    """All railway stations in the network"""
    __tablename__ = "train_stations"
    
    station_id = Column(String(10), primary_key=True)
    station_name = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    schedules_as_origin = relationship(
        "TrainSchedule",
        back_populates="origin_station_rel",
        foreign_keys="TrainSchedule.origin_station_id"
    )
    schedules_as_destination = relationship(
        "TrainSchedule",
        back_populates="destination_station_rel",
        foreign_keys="TrainSchedule.destination_station_id"
    )
    schedule_details_as_origin = relationship(
        "TrainScheduleByStation",
        back_populates="origin_station_rel",
        foreign_keys="TrainScheduleByStation.origin_station_id"
    )
    schedule_details_as_destination = relationship(
        "TrainScheduleByStation",
        back_populates="destination_station_rel",
        foreign_keys="TrainScheduleByStation.destination_station_id"
    )
    prices_as_origin = relationship(
        "TrainStationTicketPrice",
        back_populates="origin_station_rel",
        foreign_keys="TrainStationTicketPrice.origin_station_id"
    )
    prices_as_destination = relationship(
        "TrainStationTicketPrice",
        back_populates="destination_station_rel",
        foreign_keys="TrainStationTicketPrice.destination_station_id"
    )
    tickets_as_origin = relationship(
        "Ticket",
        back_populates="origin_station_rel",
        foreign_keys="Ticket.origin_station_id"
    )
    tickets_as_destination = relationship(
        "Ticket",
        back_populates="destination_station_rel",
        foreign_keys="Ticket.destination_station_id"
    )
    segments_as_origin = relationship(
        "SegmentCapacity",
        back_populates="origin_station_rel",
        foreign_keys="SegmentCapacity.origin_station_id"
    )
    segments_as_destination = relationship(
        "SegmentCapacity",
        back_populates="destination_station_rel",
        foreign_keys="SegmentCapacity.destination_station_id"
    )

class TrainRoute(Base):
    """Defined train routes with descriptions"""
    __tablename__ = "train_routes"
    
    route_id = Column(String(10), primary_key=True)
    route_name = Column(String(255), nullable=False, index=True)
    route = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    train_schedules = relationship("TrainSchedule", back_populates="route")
    demand_history = relationship("PassengerDemandHistory", back_populates="route")
    default_capacities = relationship("DefaultScheduleCapacity", back_populates="route")

# =====================================================
# TRAIN MODELS & FLEET MANAGEMENT
# =====================================================

class TrainModel(Base):
    """Train model specifications and configurations"""
    __tablename__ = "train_models"
    
    model_id = Column(String(10), primary_key=True)
    model_name = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(255), nullable=False)
    country_of_origin = Column(String(100), nullable=False)
    operational_units = Column(Integer, nullable=False)
    compartments_per_unit = Column(Integer, nullable=False)
    total_compartments_assigned_per_model = Column(Integer, nullable=False)
    seating_passengers_per_compartment = Column(Integer, nullable=False)
    standing_passengers_per_compartment = Column(Integer, nullable=False)
    total_passengers_per_compartment = Column(Integer, nullable=False)
    assigned_routes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    operational_trains = relationship("OperationalTrain", back_populates="model")
    allocation_history = relationship("TrainAllocationHistory", back_populates="model")
    schedule_capacities = relationship("ScheduleCapacity", back_populates="model")
    
    __table_args__ = (
        CheckConstraint("operational_units >= 0", name="chk_operational_units_non_negative"),
        CheckConstraint("compartments_per_unit > 0", name="chk_compartments_positive"),
        CheckConstraint("total_compartments_assigned_per_model >= 0", name="chk_total_compartments_non_negative"),
        CheckConstraint("seating_passengers_per_compartment >= 0", name="chk_seating_non_negative"),
        CheckConstraint("standing_passengers_per_compartment >= 0", name="chk_standing_non_negative"),
        CheckConstraint("total_passengers_per_compartment >= 0", name="chk_total_passengers_non_negative"),
        Index('idx_train_model_type_name', 'model_type', 'model_name'),
    )

class OperationalTrain(Base):
    """Individual train units in the operational fleet"""
    __tablename__ = "operational_trains"
    
    train_id = Column(String(20), primary_key=True)
    model_id = Column(
        String(10),
        ForeignKey("train_models.model_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    compartments_per_unit = Column(Integer, nullable=False)
    status = Column(
        SQLEnum(TrainStatus),
        default=TrainStatus.Active,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    model = relationship("TrainModel", back_populates="operational_trains")
    demand_history = relationship("PassengerDemandHistory", back_populates="train")
    allocation_history = relationship("TrainAllocationHistory", back_populates="train")
    schedule_capacities = relationship("ScheduleCapacity", back_populates="train")
    
    __table_args__ = (
        CheckConstraint("compartments_per_unit > 0", name="chk_compartments_positive"),
        Index('idx_operational_train_status_model', 'status', 'model_id'),
    )

# =====================================================
# SCHEDULING SYSTEM
# =====================================================

class TrainSchedule(Base):
    """Master schedule of train services with operational days"""
    __tablename__ = "train_schedules"
    
    train_schedule_id = Column(String(20), primary_key=True)
    route_id = Column(
        String(10),
        ForeignKey("train_routes.route_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    train_schedule = Column(String(255), nullable=False, index=True)
    origin_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    origin_station = Column(String(255), nullable=False)
    origin_departure = Column(Time, nullable=False)
    destination_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    destination_station = Column(String(255), nullable=False)
    destination_departure = Column(Time, nullable=False)
    monday = Column(Boolean, default=False)
    tuesday = Column(Boolean, default=False)
    wednesday = Column(Boolean, default=False)
    thursday = Column(Boolean, default=False)
    friday = Column(Boolean, default=False)
    saturday = Column(Boolean, default=False)
    sunday = Column(Boolean, default=False)
    poya_day = Column(Boolean, default=False)
    holiday = Column(Boolean, default=False)
    status = Column(
        SQLEnum(ScheduleStatus),
        default=ScheduleStatus.Active,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    route = relationship("TrainRoute", back_populates="train_schedules")
    origin_station_rel = relationship(
        "TrainStation",
        back_populates="schedules_as_origin",
        foreign_keys=[origin_station_id]
    )
    destination_station_rel = relationship(
        "TrainStation",
        back_populates="schedules_as_destination",
        foreign_keys=[destination_station_id]
    )
    schedule_by_station = relationship("TrainScheduleByStation", back_populates="schedule")
    tickets = relationship("Ticket", back_populates="schedule")
    demand_history = relationship("PassengerDemandHistory", back_populates="schedule")
    allocation_history = relationship("TrainAllocationHistory", back_populates="schedule")
    schedule_capacities = relationship("ScheduleCapacity", back_populates="schedule")
    segment_capacities = relationship("SegmentCapacity", back_populates="schedule")
    default_capacity = relationship("DefaultScheduleCapacity", back_populates="schedule", uselist=False)
    
    __table_args__ = (
        CheckConstraint("origin_station_id != destination_station_id", name="chk_different_stations"),
        CheckConstraint(
            "monday OR tuesday OR wednesday OR thursday OR friday OR saturday OR sunday OR poya_day OR holiday",
            name="chk_at_least_one_day"
        ),
        Index('idx_schedule_route_status', 'route_id', 'status'),
        Index('idx_schedule_origin_dest', 'origin_station_id', 'destination_station_id'),
    )

class TrainScheduleByStation(Base):
    """Detailed station-by-station timing for each schedule"""
    __tablename__ = "train_schedule_by_station"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    train_schedule_id = Column(
        String(20),
        ForeignKey("train_schedules.train_schedule_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    train_schedule = Column(String(255), nullable=False)
    origin_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    origin_station = Column(String(255), nullable=False)
    origin_departure = Column(Time, nullable=False)
    destination_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    destination_station = Column(String(255), nullable=False)
    destination_departure = Column(Time, nullable=False)
    duration = Column(Interval, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    schedule = relationship("TrainSchedule", back_populates="schedule_by_station")
    origin_station_rel = relationship(
        "TrainStation",
        back_populates="schedule_details_as_origin",
        foreign_keys=[origin_station_id]
    )
    destination_station_rel = relationship(
        "TrainStation",
        back_populates="schedule_details_as_destination",
        foreign_keys=[destination_station_id]
    )
    
    __table_args__ = (
        Index(
            'idx_unique_schedule_stations',
            'train_schedule_id',
            'origin_station_id',
            'destination_station_id',
            unique=True
        ),
        Index('idx_schedule_by_station_origin', 'origin_station_id'),
        Index('idx_schedule_by_station_dest', 'destination_station_id'),
    )

# =====================================================
# PRICING SYSTEM
# =====================================================

class TrainStationTicketPrice(Base):
    """Ticket pricing between stations by class"""
    __tablename__ = "train_station_ticket_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    origin_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    destination_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    distance = Column(DECIMAL(10, 2), nullable=False)
    first_class_fee = Column(DECIMAL(10, 2), default=0)
    second_class_fee = Column(DECIMAL(10, 2), default=0)
    third_class_fee = Column(DECIMAL(10, 2), default=0)
    effective_from = Column(Date, nullable=False, default=func.current_date())
    effective_to = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    origin_station_rel = relationship(
        "TrainStation",
        back_populates="prices_as_origin",
        foreign_keys=[origin_station_id]
    )
    destination_station_rel = relationship(
        "TrainStation",
        back_populates="prices_as_destination",
        foreign_keys=[destination_station_id]
    )
    
    __table_args__ = (
        CheckConstraint("origin_station_id != destination_station_id", name="chk_different_price_stations"),
        CheckConstraint("distance >= 0", name="chk_distance_non_negative"),
        CheckConstraint("first_class_fee >= 0", name="chk_first_class_fee_non_negative"),
        CheckConstraint("second_class_fee >= 0", name="chk_second_class_fee_non_negative"),
        CheckConstraint("third_class_fee >= 0", name="chk_third_class_fee_non_negative"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="chk_effective_dates"
        ),
        Index(
            'idx_unique_price_stations_date',
            'origin_station_id',
            'destination_station_id',
            'effective_from',
            unique=True
        ),
        Index('idx_price_effective', 'effective_from', 'effective_to'),
    )

# =====================================================
# TICKETING SYSTEM
# =====================================================

class Ticket(Base):
    """Issued passenger tickets"""
    __tablename__ = "tickets"
    
    ticket_id = Column(String(20), primary_key=True)
    # Passenger Information
    nic = Column(String(20), index=True)
    passport = Column(String(20), index=True)
    is_child = Column(Boolean, default=False)
    contact_number = Column(String(20))
    # Journey Details
    schedule_id = Column(
        String(20),
        ForeignKey("train_schedules.train_schedule_id", ondelete="SET NULL"),
        index=True
    )
    origin_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="SET NULL"),
        index=True
    )
    destination_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="SET NULL"),
        index=True
    )
    origin_departure = Column(Time)
    destination_departure = Column(Time)
    schedule_date = Column(Date, index=True)
    # Ticket Details
    class_ = Column("class", SQLEnum(TrainClass))
    fee = Column(DECIMAL(10, 2))
    # Payment Information
    payment_method = Column(SQLEnum(PaymentMethod))
    payment_status = Column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.Pending,
        nullable=False,
        index=True
    )
    # Booking Information
    issue_date = Column(Date, index=True)
    status = Column(
        SQLEnum(TicketStatus),
        default=TicketStatus.Pending,
        nullable=False,
        index=True
    )
    booking_platform = Column(SQLEnum(BookingPlatform))
    issued_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    schedule = relationship("TrainSchedule", back_populates="tickets")
    origin_station_rel = relationship(
        "TrainStation",
        back_populates="tickets_as_origin",
        foreign_keys=[origin_station_id]
    )
    destination_station_rel = relationship(
        "TrainStation",
        back_populates="tickets_as_destination",
        foreign_keys=[destination_station_id]
    )
    
    __table_args__ = (
        CheckConstraint("nic IS NOT NULL OR passport IS NOT NULL", name="chk_passenger_id"),
        CheckConstraint(
            "schedule_date IS NULL OR issue_date IS NULL OR schedule_date >= issue_date",
            name="chk_schedule_date_after_issue"
        ),
        CheckConstraint("fee IS NULL OR fee >= 0", name="chk_fee_non_negative"),
        Index('idx_ticket_schedule_date', 'schedule_date', 'schedule_id'),
        Index('idx_ticket_nic_date', 'nic', 'schedule_date'),
        Index('idx_ticket_passport_date', 'passport', 'schedule_date'),
    )

# =====================================================
# ANALYTICS & REPORTING
# =====================================================

class PassengerDemandHistory(Base):
    """Historical passenger demand data for forecasting and analytics"""
    __tablename__ = "passenger_demand_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    schedule_id = Column(
        String(20),
        ForeignKey("train_schedules.train_schedule_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    route_id = Column(
        String(10),
        ForeignKey("train_routes.route_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    train_id = Column(
        String(20),
        ForeignKey("operational_trains.train_id", ondelete="SET NULL"),
        index=True
    )
    # Passenger Counts
    total_passengers = Column(Integer, nullable=False)
    first_class_passengers = Column(Integer, default=0)
    second_class_passengers = Column(Integer, default=0)
    third_class_passengers = Column(Integer, default=0)
    # Capacity & Utilization
    total_capacity = Column(Integer, nullable=False)
    load_factor = Column(DECIMAL(5, 2))
    # Revenue
    revenue = Column(DECIMAL(12, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    schedule = relationship("TrainSchedule", back_populates="demand_history")
    route = relationship("TrainRoute", back_populates="demand_history")
    train = relationship("OperationalTrain", back_populates="demand_history")
    
    __table_args__ = (
        CheckConstraint("total_passengers >= 0", name="chk_total_passengers_non_negative"),
        CheckConstraint("first_class_passengers >= 0", name="chk_first_class_pass_non_negative"),
        CheckConstraint("second_class_passengers >= 0", name="chk_second_class_pass_non_negative"),
        CheckConstraint("third_class_passengers >= 0", name="chk_third_class_pass_non_negative"),
        CheckConstraint("total_capacity > 0", name="chk_total_capacity_positive"),
        CheckConstraint(
            "load_factor IS NULL OR (load_factor >= 0 AND load_factor <= 100)",
            name="chk_load_factor_valid"
        ),
        CheckConstraint("revenue IS NULL OR revenue >= 0", name="chk_revenue_non_negative"),
        Index('idx_demand_date_schedule', 'date', 'schedule_id', unique=True),
        Index('idx_demand_route_date', 'route_id', 'date'),
    )

class TrainAllocationHistory(Base):
    """Historical train allocation decisions for optimization tracking"""
    __tablename__ = "train_allocation_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    schedule_id = Column(
        String(20),
        ForeignKey("train_schedules.train_schedule_id", ondelete="CASCADE"),
        nullable=False
    )
    train_id = Column(
        String(20),
        ForeignKey("operational_trains.train_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    model_id = Column(
        String(10),
        ForeignKey("train_models.model_id", ondelete="CASCADE"),
        nullable=False
    )
    first_class_compartments = Column(Integer, nullable=False)
    second_class_compartments = Column(Integer, nullable=False)
    third_class_compartments = Column(Integer, nullable=False)
    allocation_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    schedule = relationship("TrainSchedule", back_populates="allocation_history")
    train = relationship("OperationalTrain", back_populates="allocation_history")
    model = relationship("TrainModel", back_populates="allocation_history")
    
    __table_args__ = (
        CheckConstraint("first_class_compartments >= 0", name="chk_alloc_first_non_negative"),
        CheckConstraint("second_class_compartments >= 0", name="chk_alloc_second_non_negative"),
        CheckConstraint("third_class_compartments >= 0", name="chk_alloc_third_non_negative"),
        Index('idx_allocation_date_train', 'date', 'train_id'),
        Index('idx_allocation_schedule_date', 'schedule_id', 'date'),
    )

# =====================================================
# CAPACITY MANAGEMENT SYSTEM
# =====================================================

class ScheduleCapacity(Base):
    """Capacity tracking for advance bookings and train allocation management"""
    __tablename__ = "schedule_capacity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(
        String(20),
        ForeignKey("train_schedules.train_schedule_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    schedule_date = Column(Date, nullable=False, index=True)

    # Train Assignment (NULL until confirmed 24-48h before departure)
    train_id = Column(
        String(20),
        ForeignKey("operational_trains.train_id", ondelete="SET NULL"),
        index=True
    )
    model_id = Column(
        String(10),
        ForeignKey("train_models.model_id", ondelete="SET NULL")
    )

    # Allocation Status
    allocation_status = Column(
        SQLEnum(AllocationStatus),
        default=AllocationStatus.Provisional,
        nullable=False,
        index=True
    )

    # Planned Capacity (estimated/default - used for advance bookings)
    planned_first_class_seats = Column(Integer, default=0)
    planned_second_class_seats = Column(Integer, default=0)
    planned_third_class_seats = Column(Integer, default=0)

    # Planned Compartments (estimated/default)
    planned_first_class_compartments = Column(Integer, default=0)
    planned_second_class_compartments = Column(Integer, default=0)
    planned_third_class_compartments = Column(Integer, default=0)

    # Actual Allocated Capacity (set when status = 'Confirmed')
    allocated_first_class_compartments = Column(Integer, default=0)
    allocated_second_class_compartments = Column(Integer, default=0)
    allocated_third_class_compartments = Column(Integer, default=0)

    allocated_first_class_seats = Column(Integer, default=0)
    allocated_second_class_seats = Column(Integer, default=0)
    allocated_third_class_seats = Column(Integer, default=0)

    # Booking Counters (real-time tracking - total across all segments)
    booked_first_class = Column(Integer, default=0)
    booked_second_class = Column(Integer, default=0)
    booked_third_class = Column(Integer, default=0)
    total_bookings = Column(Integer, default=0)

    # Metadata
    confirmed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    schedule = relationship("TrainSchedule", back_populates="schedule_capacities")
    train = relationship("OperationalTrain", back_populates="schedule_capacities")
    model = relationship("TrainModel", back_populates="schedule_capacities")
    segments = relationship(
        "SegmentCapacity",
        back_populates="schedule_capacity",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("planned_first_class_seats >= 0", name="chk_planned_first_seats_non_neg"),
        CheckConstraint("planned_second_class_seats >= 0", name="chk_planned_second_seats_non_neg"),
        CheckConstraint("planned_third_class_seats >= 0", name="chk_planned_third_seats_non_neg"),
        CheckConstraint("allocated_first_class_seats >= 0", name="chk_allocated_first_seats_non_neg"),
        CheckConstraint("allocated_second_class_seats >= 0", name="chk_allocated_second_seats_non_neg"),
        CheckConstraint("allocated_third_class_seats >= 0", name="chk_allocated_third_seats_non_neg"),
        CheckConstraint("booked_first_class >= 0", name="chk_booked_first_non_neg"),
        CheckConstraint("booked_second_class >= 0", name="chk_booked_second_non_neg"),
        CheckConstraint("booked_third_class >= 0", name="chk_booked_third_non_neg"),
        Index('idx_schedule_capacity_schedule_date', 'schedule_id', 'schedule_date', unique=True),
        Index('idx_schedule_capacity_date_status', 'schedule_date', 'allocation_status'),
    )


class SegmentCapacity(Base):
    """Track passenger load per route segment (station-to-station)"""
    __tablename__ = "segment_capacity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_capacity_id = Column(
        Integer,
        ForeignKey("schedule_capacity.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    schedule_id = Column(
        String(20),
        ForeignKey("train_schedules.train_schedule_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    schedule_date = Column(Date, nullable=False, index=True)

    # Segment Definition (consecutive station pairs)
    segment_order = Column(Integer, nullable=False)
    origin_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    origin_station = Column(String(255), nullable=False)
    destination_station_id = Column(
        String(10),
        ForeignKey("train_stations.station_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    destination_station = Column(String(255), nullable=False)

    # Current Load (passengers ON the train during this segment)
    first_class_load = Column(Integer, default=0)
    second_class_load = Column(Integer, default=0)
    third_class_load = Column(Integer, default=0)
    total_load = Column(Integer, default=0)

    # Maximum Capacity (from assigned train)
    max_first_class = Column(Integer, nullable=False, default=0)
    max_second_class = Column(Integer, nullable=False, default=0)
    max_third_class = Column(Integer, nullable=False, default=0)
    max_total = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    schedule_capacity = relationship("ScheduleCapacity", back_populates="segments")
    schedule = relationship("TrainSchedule", back_populates="segment_capacities")
    origin_station_rel = relationship(
        "TrainStation",
        back_populates="segments_as_origin",
        foreign_keys=[origin_station_id]
    )
    destination_station_rel = relationship(
        "TrainStation",
        back_populates="segments_as_destination",
        foreign_keys=[destination_station_id]
    )

    __table_args__ = (
        CheckConstraint("origin_station_id != destination_station_id", name="chk_seg_different_stations"),
        CheckConstraint("segment_order > 0", name="chk_seg_order_positive"),
        CheckConstraint("first_class_load >= 0", name="chk_seg_first_load_non_neg"),
        CheckConstraint("second_class_load >= 0", name="chk_seg_second_load_non_neg"),
        CheckConstraint("third_class_load >= 0", name="chk_seg_third_load_non_neg"),
        CheckConstraint("total_load >= 0", name="chk_seg_total_load_non_neg"),
        CheckConstraint("max_first_class >= 0", name="chk_seg_max_first_non_neg"),
        CheckConstraint("max_second_class >= 0", name="chk_seg_max_second_non_neg"),
        CheckConstraint("max_third_class >= 0", name="chk_seg_max_third_non_neg"),
        CheckConstraint("max_total >= 0", name="chk_seg_max_total_non_neg"),
        CheckConstraint("first_class_load <= max_first_class", name="chk_seg_first_load_not_exceed"),
        CheckConstraint("second_class_load <= max_second_class", name="chk_seg_second_load_not_exceed"),
        CheckConstraint("third_class_load <= max_third_class", name="chk_seg_third_load_not_exceed"),
        CheckConstraint("total_load <= max_total", name="chk_seg_total_load_not_exceed"),
        CheckConstraint(
            "total_load = first_class_load + second_class_load + third_class_load",
            name="chk_seg_total_matches_sum"
        ),
        Index('idx_segment_capacity_schedule_cap_order', 'schedule_capacity_id', 'segment_order', unique=True),
        Index('idx_segment_capacity_schedule_date', 'schedule_id', 'schedule_date'),
        Index('idx_segment_capacity_stations', 'origin_station_id', 'destination_station_id'),
    )


class DefaultScheduleCapacity(Base):
    """Default capacity configuration for each train schedule"""
    __tablename__ = "default_schedule_capacity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    train_schedule_id = Column(
        String(20),
        ForeignKey("train_schedules.train_schedule_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    route_id = Column(
        String(10),
        ForeignKey("train_routes.route_id", ondelete="SET NULL"),
        index=True
    )

    # First Class Configuration
    first_class_compartments = Column(Integer, default=0)
    seating_passengers_per_first_class = Column(Integer, default=0)
    standing_passengers_per_first_class = Column(Integer, default=0)

    # Second Class Configuration
    second_class_compartments = Column(Integer, default=0)
    seating_passengers_per_second_class = Column(Integer, default=0)
    standing_passengers_per_second_class = Column(Integer, default=0)

    # Third Class Configuration
    third_class_compartments = Column(Integer, default=0)
    seating_passengers_per_third_class = Column(Integer, default=0)
    standing_passengers_per_third_class = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    schedule = relationship("TrainSchedule", back_populates="default_capacity")
    route = relationship("TrainRoute", back_populates="default_capacities")

    __table_args__ = (
        CheckConstraint("first_class_compartments >= 0", name="chk_def_first_comp_non_neg"),
        CheckConstraint("second_class_compartments >= 0", name="chk_def_second_comp_non_neg"),
        CheckConstraint("third_class_compartments >= 0", name="chk_def_third_comp_non_neg"),
        CheckConstraint("seating_passengers_per_first_class >= 0", name="chk_def_first_seat_non_neg"),
        CheckConstraint("seating_passengers_per_second_class >= 0", name="chk_def_second_seat_non_neg"),
        CheckConstraint("seating_passengers_per_third_class >= 0", name="chk_def_third_seat_non_neg"),
        CheckConstraint("standing_passengers_per_first_class >= 0", name="chk_def_first_stand_non_neg"),
        CheckConstraint("standing_passengers_per_second_class >= 0", name="chk_def_second_stand_non_neg"),
        CheckConstraint("standing_passengers_per_third_class >= 0", name="chk_def_third_stand_non_neg"),
    )

# =====================================================
# AUDIT & LOGGING
# =====================================================

class AuditLog(Base):
    """System audit trail"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="SET NULL"))
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(String(50))
    action = Column(String(20), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(INET)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        CheckConstraint("action IN ('INSERT', 'UPDATE', 'DELETE')", name="chk_valid_action"),
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_table_created', 'table_name', 'created_at'),
    )