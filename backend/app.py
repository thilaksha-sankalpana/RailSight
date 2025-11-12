# backend/app.py - COMPLETE UPDATED VERSION v6.0
"""
TCDAFS Backend API - v6.0
Updated for revised database schema v2.0 (2025-11-10)
Fully updated for Supabase PostgreSQL integration
No CSV dependencies - Pure database operations
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta, date, time as time_type, timezone
from typing import Optional, List
from decimal import Decimal
from contextlib import asynccontextmanager

# Add project root to path FIRST
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc, text
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from backend.api_ai_predictions import router as ai_router

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import auth functions
from backend.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    require_admin,
    require_role,
    Token,
    get_password_hash,
    create_user
)

# Import database
from backend import db

# Import models (updated for v2.0)
from backend.models import (
    UserProfile, TrainStation, TrainRoute, TrainModel, OperationalTrain,
    TrainSchedule, TrainScheduleByStation,
    TrainStationTicketPrice, Ticket, PassengerDemandHistory,
    TrainAllocationHistory, UserRole, TrainStatus, ScheduleStatus,
    TicketStatus, TrainClass, PaymentMethod, BookingPlatform,
    PaymentStatus, ScheduleCapacity, SegmentCapacity, DefaultScheduleCapacity
)

# Import schemas (updated for v2.0)
from backend.schemas import (
    UserCreate, UserResponse, UserUpdate,
    StationCreate, StationResponse, StationUpdate,
    OperationalTrainCreate, OperationalTrainResponse, OperationalTrainUpdate,
    TrainModelCreate, TrainModelResponse, TrainModelUpdate,
    RouteCreate, RouteResponse, RouteUpdate,
    ScheduleCreate, ScheduleResponse, ScheduleUpdate,
    TicketCreate, TicketResponse, TicketUpdate,
    PriceCreate, PriceResponse, PriceUpdate, PriceCalculationRequest, PriceCalculationResponse,
    AnalyticsSummary, WeeklySales, TopRoute,
    DailyTicketSales, ScheduleStatusToday, ClassDistributionToday,
    TrainAllocationRequest, TrainAllocationResponse,
    CompartmentPredictionRequest, CompartmentPredictionResponse
)

# Import utilities
from backend.utils.errors import (
    TCDAFSException, ResourceNotFoundError, ValidationError,
    ConflictError, tcdafs_exception_handler, validation_exception_handler,
    sqlalchemy_exception_handler, general_exception_handler,
    validate_resource_exists
)
from backend.utils.validators import (
    validate_nic_or_passport, validate_phone_number,
    validate_compartment_distribution, validate_price_structure
)
from backend.utils.helpers import (
    generate_ticket_id, calculate_child_discount,
    format_currency, paginate_results
)
from backend.middleware.logging_middleware import (
    LoggingMiddleware, PerformanceMonitorMiddleware
)
from backend.utils.calendar_service import get_day_type

# Import optimizers
from backend.train_allocator import TrainAllocationOptimizer
from backend.compartment_predictor import predict_for_schedule

# Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8050,http://127.0.0.1:8050").split(",")

# ============= LIFESPAN CONTEXT =============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    logger.info("🚂 Starting TCDAFS API v6.0...")

    if db.check_db_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed")
        raise RuntimeError("Cannot connect to database")

    # Initialize database tables
    logger.info("🔧 Initializing database tables...")
    db.init_db()

    # Preload holiday data for current year
    logger.info("📅 Preloading holiday data...")
    try:
        from backend.utils.calendar_service import CalendarService
        CalendarService.preload_current_year()
        logger.info("✅ Holiday data preloaded")
    except Exception as e:
        logger.warning(f"⚠️ Could not preload holidays: {e}")

    logger.info("✅ TCDAFS API started successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down TCDAFS API...")

# Initialize FastAPI
app = FastAPI(
    title="TCDAFS API",
    description="Train Compartment Demand Analysis & Forecasting System - v6.0 (Schema v2.0)",
    version="6.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(PerformanceMonitorMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(TCDAFSException, tcdafs_exception_handler)
app.add_exception_handler(HTTPException, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(ai_router)

# ============= DATABASE DEPENDENCY =============
def get_db():
    """Get database session"""
    db_session = db.SessionLocal()
    try:
        yield db_session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()

# ============= ROOT ENDPOINT =============
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "TCDAFS API v6.0 (Schema v2.0)",
        "status": "operational",
        "database": "PostgreSQL (Supabase)",
        "schema_version": "2.0",
        "docs": "/docs",
        "version": "6.0.0",
        "endpoints": {
            "authentication": "/token",
            "users": "/users",
            "stations": "/stations",
            "routes": "/routes",
            "trains": "/trains",
            "train_models": "/train-models",
            "schedules": "/schedules",
            "tickets": "/tickets",
            "pricing": "/prices",
            "analytics": "/analytics",
            "allocation": "/allocate-train"
        }
    }

# ============= AUTHENTICATION =============
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """LOGIN ENDPOINT - OAuth2 compatible"""
    logger.info(f"🔐 Login request: {form_data.username}")

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        logger.warning(f"❌ Auth failed: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user_role},
        expires_delta=access_token_expires
    )

    logger.info(f"✅ Token generated: {user.email}")

    return {"access_token": access_token, "token_type": "bearer"}

# ============= USER MANAGEMENT =============
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_data: UserCreate,
    current_user: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new user (Admin only)"""
    logger.info(f"Creating user: {user_data.email}")

    try:
        new_user = create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
            contact_number=user_data.contact_number,
            db=db
        )
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserProfile = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users (Admin only)"""
    users = db.query(UserProfile).offset(skip).limit(limit).all()
    return users

# ============= STATIONS =============
@app.get("/stations", response_model=List[StationResponse])
async def get_stations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all train stations"""
    query = db.query(TrainStation)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                TrainStation.station_name.ilike(search_term),
                TrainStation.station_id.ilike(search_term)
            )
        )

    stations = query.offset(skip).limit(limit).all()
    return stations

@app.get("/stations/{station_id}", response_model=StationResponse)
async def get_station(station_id: str, db: Session = Depends(get_db)):
    """Get specific station"""
    station = db.query(TrainStation).filter(
        TrainStation.station_id == station_id
    ).first()
    validate_resource_exists(station, "Station", station_id)
    return station

@app.post("/stations", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
async def create_station(
    station_data: StationCreate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Create new station"""
    existing = db.query(TrainStation).filter(
        TrainStation.station_id == station_data.station_id
    ).first()

    if existing:
        raise ConflictError(f"Station {station_data.station_id} already exists")

    station = TrainStation(
        station_id=station_data.station_id,
        station_name=station_data.station_name
    )

    db.add(station)
    db.commit()
    db.refresh(station)

    logger.info(f"✅ Station created: {station.station_id}")
    return station

# ============= TRAIN MODELS =============
@app.get("/train-models", response_model=List[TrainModelResponse])
async def get_train_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get all train models"""
    models = db.query(TrainModel).offset(skip).limit(limit).all()
    return models

@app.post("/train-models", response_model=TrainModelResponse, status_code=status.HTTP_201_CREATED)
async def create_train_model(
    model_data: TrainModelCreate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Create new train model"""
    existing = db.query(TrainModel).filter(
        TrainModel.model_id == model_data.model_id
    ).first()

    if existing:
        raise ConflictError(f"Model {model_data.model_id} already exists")

    model = TrainModel(**model_data.model_dump())

    db.add(model)
    db.commit()
    db.refresh(model)

    logger.info(f"✅ Train model created: {model.model_id}")
    return model

@app.get("/train-models/{model_id}", response_model=TrainModelResponse)
async def get_train_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get specific train model by ID"""
    model = db.query(TrainModel).filter(TrainModel.model_id == model_id).first()
    if not model:
        raise ResourceNotFoundError(f"Train model {model_id} not found")
    return model

@app.patch("/train-models/{model_id}", response_model=TrainModelResponse)
async def update_train_model(
    model_id: str,
    model_data: TrainModelUpdate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Update train model"""
    model = db.query(TrainModel).filter(TrainModel.model_id == model_id).first()
    if not model:
        raise ResourceNotFoundError(f"Train model {model_id} not found")

    # Update fields (only update fields that are provided)
    for key, value in model_data.model_dump(exclude_unset=True).items():
        setattr(model, key, value)

    db.commit()
    db.refresh(model)

    logger.info(f"✅ Train model updated: {model_id}")
    return model

@app.delete("/train-models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_train_model(
    model_id: str,
    current_user: UserProfile = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete train model"""
    model = db.query(TrainModel).filter(TrainModel.model_id == model_id).first()
    if not model:
        raise ResourceNotFoundError(f"Train model {model_id} not found")

    # Check if model is used by operational trains
    trains_using_model = db.query(OperationalTrain).filter(
        OperationalTrain.model_id == model_id
    ).first()

    if trains_using_model:
        raise ConflictError(f"Cannot delete model {model_id} - it is used by operational trains")

    db.delete(model)
    db.commit()

    logger.info(f"✅ Train model deleted: {model_id}")
    return None

# ============= OPERATIONAL TRAINS =============
@app.get("/trains", response_model=List[OperationalTrainResponse])
async def get_trains(
    status: Optional[str] = Query(None),
    model_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, le=1000),
    db: Session = Depends(get_db)
):
    """Get all operational trains"""
    query = db.query(OperationalTrain)

    if status:
        try:
            status_enum = TrainStatus[status]
            query = query.filter(OperationalTrain.status == status_enum)
        except KeyError:
            raise ValidationError(f"Invalid status: {status}")

    if model_id:
        query = query.filter(OperationalTrain.model_id == model_id)

    # Order by train_id to show trains in consistent order
    trains = query.order_by(OperationalTrain.train_id).offset(skip).limit(limit).all()
    return trains

@app.get("/trains/{train_id}", response_model=OperationalTrainResponse)
async def get_train(train_id: str, db: Session = Depends(get_db)):
    """Get specific train"""
    train = db.query(OperationalTrain).filter(
        OperationalTrain.train_id == train_id
    ).first()
    validate_resource_exists(train, "Train", train_id)
    return train

@app.post("/trains", response_model=OperationalTrainResponse, status_code=status.HTTP_201_CREATED)
async def create_train(
    train_data: OperationalTrainCreate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Create new operational train"""
    existing = db.query(OperationalTrain).filter(
        OperationalTrain.train_id == train_data.train_id
    ).first()

    if existing:
        raise ConflictError(f"Train {train_data.train_id} already exists")

    model = db.query(TrainModel).filter(
        TrainModel.model_id == train_data.model_id
    ).first()
    validate_resource_exists(model, "TrainModel", train_data.model_id)

    train = OperationalTrain(
        train_id=train_data.train_id,
        model_id=train_data.model_id,
        compartments_per_unit=train_data.compartments_per_unit,
        status=TrainStatus[train_data.status]
    )

    db.add(train)
    db.commit()
    db.refresh(train)

    logger.info(f"✅ Train created: {train.train_id}")
    return train

@app.patch("/trains/{train_id}", response_model=OperationalTrainResponse)
async def update_train(
    train_id: str,
    train_update: OperationalTrainUpdate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Update train status"""
    logger.info(f"🔧 PATCH /trains/{train_id} - Received update: {train_update.model_dump()}")
    
    train = db.query(OperationalTrain).filter(
        OperationalTrain.train_id == train_id
    ).first()
    validate_resource_exists(train, "Train", train_id)

    logger.info(f"📊 Current status: {train.status} (type: {type(train.status)})")
    
    if train_update.status:
        logger.info(f"🔄 Updating status to: {train_update.status}")
        train.status = TrainStatus[train_update.status]
        logger.info(f"✓ Status set to: {train.status} (type: {type(train.status)})")
    else:
        logger.warning(f"⚠️ No status in update data!")

    db.commit()
    db.refresh(train)

    logger.info(f"✅ Train updated: {train.train_id}, Final status: {train.status}")
    return train

@app.delete("/trains/{train_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_train(
    train_id: str,
    current_user: UserProfile = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete operational train"""
    train = db.query(OperationalTrain).filter(
        OperationalTrain.train_id == train_id
    ).first()
    if not train:
        raise ResourceNotFoundError(f"Train {train_id} not found")

    # Check if train is used in schedules
    schedules_using_train = db.query(TrainSchedule).filter(
        TrainSchedule.train_id == train_id
    ).first()

    if schedules_using_train:
        raise ConflictError(f"Cannot delete train {train_id} - it is used in schedules")

    db.delete(train)
    db.commit()

    logger.info(f"✅ Train deleted: {train_id}")
    return None

# ============= ROUTES =============
@app.get("/routes", response_model=List[RouteResponse])
async def get_routes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get all routes"""
    routes = db.query(TrainRoute).offset(skip).limit(limit).all()
    return routes

@app.post("/routes", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_data: RouteCreate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Create new route"""
    existing = db.query(TrainRoute).filter(
        TrainRoute.route_id == route_data.route_id
    ).first()

    if existing:
        raise ConflictError(f"Route {route_data.route_id} already exists")

    route = TrainRoute(**route_data.model_dump())

    db.add(route)
    db.commit()
    db.refresh(route)

    logger.info(f"✅ Route created: {route.route_id}")
    return route

@app.get("/routes/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: str,
    db: Session = Depends(get_db)
):
    """Get specific route by ID"""
    route = db.query(TrainRoute).filter(TrainRoute.route_id == route_id).first()
    if not route:
        raise ResourceNotFoundError(f"Route {route_id} not found")
    return route

@app.patch("/routes/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: str,
    route_data: RouteUpdate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Update route"""
    route = db.query(TrainRoute).filter(TrainRoute.route_id == route_id).first()
    if not route:
        raise ResourceNotFoundError(f"Route {route_id} not found")

    # Update fields
    for key, value in route_data.model_dump(exclude_unset=True).items():
        setattr(route, key, value)

    db.commit()
    db.refresh(route)

    logger.info(f"✅ Route updated: {route_id}")
    return route

@app.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(
    route_id: str,
    current_user: UserProfile = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete route"""
    route = db.query(TrainRoute).filter(TrainRoute.route_id == route_id).first()
    if not route:
        raise ResourceNotFoundError(f"Route {route_id} not found")

    # Check if route is used in schedules
    schedules_using_route = db.query(TrainSchedule).filter(
        TrainSchedule.route_id == route_id
    ).first()

    if schedules_using_route:
        raise ConflictError(f"Cannot delete route {route_id} - it is used in schedules")

    db.delete(route)
    db.commit()

    logger.info(f"✅ Route deleted: {route_id}")
    return None

# ============= SCHEDULES =============
@app.get("/schedules", response_model=List[ScheduleResponse])
async def get_schedules(
    date: Optional[date] = Query(None),
    route_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get train schedules"""
    query = db.query(TrainSchedule)

    if status:
        try:
            status_enum = ScheduleStatus[status]
            query = query.filter(TrainSchedule.status == status_enum)
        except KeyError:
            raise ValidationError(f"Invalid status: {status}")

    if route_id:
        query = query.filter(TrainSchedule.route_id == route_id)

    if date:
        day_name = date.strftime("%A").lower()
        if not hasattr(TrainSchedule, day_name):
            raise ValidationError(f"Invalid day: {day_name}")
        day_column = getattr(TrainSchedule, day_name)
        query = query.filter(day_column == True)

    schedules = query.order_by(TrainSchedule.train_schedule_id).offset(skip).limit(limit).all()
    return schedules

@app.get("/schedules/available")
async def get_available_schedules(
    origin_station_id: str = Query(...),
    destination_station_id: str = Query(...),
    travel_date: date = Query(...),
    limit: int = Query(200, le=500, description="Maximum number of schedules to return"),
    db: Session = Depends(get_db)
):
    """
    Find available schedules for booking - OPTIMIZED VERSION
    Uses direct query on train_schedule_by_station for 20-30x faster performance
    """
    logger.info(f"Finding schedules: {origin_station_id} → {destination_station_id} on {travel_date}")

    # Get current time in Sri Lanka timezone (UTC+5:30)
    sri_lanka_tz = timezone(timedelta(hours=5, minutes=30))
    current_datetime_sl = datetime.now(sri_lanka_tz)
    current_time_sl = current_datetime_sl.time()
    today_date = current_datetime_sl.date()

    # Get day type information
    try:
        day_info = get_day_type(travel_date)
        is_poya = day_info.get("is_poya_day", False)
        is_holiday = day_info.get("is_public_holiday", False)
        day_name = day_info.get("day_of_week", travel_date.strftime("%A").lower())
    except Exception as e:
        logger.warning(f"Calendarific API error: {e}. Using fallback.")
        day_name = travel_date.strftime("%A").lower()
        is_poya = False
        is_holiday = False

    logger.info(f"Travel date: {travel_date} ({day_name}), Poya: {is_poya}, Holiday: {is_holiday}")

    # Validate day column exists
    if not hasattr(TrainSchedule, day_name):
        logger.warning(f"Invalid day name: {day_name}")
        return []

    day_column = getattr(TrainSchedule, day_name)

    # Build day filter conditions
    day_filters = [day_column == True]
    if is_poya:
        day_filters.append(TrainSchedule.poya_day == True)
    if is_holiday:
        day_filters.append(TrainSchedule.holiday == True)

    # OPTIMIZED QUERY: Get direct connections from train_schedule_by_station
    # This table already has all station-to-station segments with times
    direct_segments = db.query(
        TrainScheduleByStation,
        TrainSchedule
    ).join(
        TrainSchedule,
        TrainScheduleByStation.train_schedule_id == TrainSchedule.train_schedule_id
    ).filter(
        and_(
            TrainScheduleByStation.origin_station_id == origin_station_id,
            TrainScheduleByStation.destination_station_id == destination_station_id,
            TrainSchedule.status == ScheduleStatus.Active,
            or_(*day_filters)
        )
    ).order_by(
        TrainScheduleByStation.origin_departure
    ).limit(limit).all()

    logger.info(f"Found {len(direct_segments)} direct connections")

    if not direct_segments:
        return []

    # Get station names
    station_cache = {}
    for station_id in [origin_station_id, destination_station_id]:
        station_obj = db.query(TrainStation).filter(TrainStation.station_id == station_id).first()
        station_cache[station_id] = station_obj.station_name if station_obj else station_id

    # Get schedule IDs for capacity lookup
    schedule_ids = list(set([seg.train_schedule_id for seg, _ in direct_segments]))

    # Prefetch schedule capacities
    schedule_capacities = db.query(ScheduleCapacity).filter(
        and_(
            ScheduleCapacity.schedule_id.in_(schedule_ids),
            ScheduleCapacity.schedule_date == travel_date
        )
    ).all()
    capacity_by_schedule = {sc.schedule_id: sc for sc in schedule_capacities}

    # Prefetch segment capacities
    capacity_ids = [sc.id for sc in schedule_capacities]
    all_segment_capacities = []
    if capacity_ids:
        all_segment_capacities = db.query(SegmentCapacity).filter(
            SegmentCapacity.schedule_capacity_id.in_(capacity_ids)
        ).all()

    segment_capacities_by_schedule = {}
    for seg_cap in all_segment_capacities:
        if seg_cap.schedule_capacity_id not in segment_capacities_by_schedule:
            segment_capacities_by_schedule[seg_cap.schedule_capacity_id] = []
        segment_capacities_by_schedule[seg_cap.schedule_capacity_id].append(seg_cap)

    # Prefetch default capacities
    schedules_without_capacity = [sid for sid in schedule_ids if sid not in capacity_by_schedule]
    default_capacities = {}
    if schedules_without_capacity:
        default_caps = db.query(DefaultScheduleCapacity).filter(
            DefaultScheduleCapacity.train_schedule_id.in_(schedules_without_capacity)
        ).all()
        default_capacities = {dc.train_schedule_id: dc for dc in default_caps}

    # Build results
    results = []
    
    for segment, schedule in direct_segments:
        origin_departure_time = segment.origin_departure
        destination_arrival_time = segment.destination_departure
        
        # Skip past trains if booking for today
        if travel_date == today_date:
            buffer_time = (datetime.combine(today_date, current_time_sl) + timedelta(minutes=2)).time()
            if origin_departure_time < buffer_time:
                continue

        # Calculate duration
        temp_date = datetime.today().date()
        origin_dt = datetime.combine(temp_date, origin_departure_time)
        dest_dt = datetime.combine(temp_date, destination_arrival_time)
        if dest_dt < origin_dt:
            dest_dt += timedelta(days=1)
        journey_duration = dest_dt - origin_dt

        # Calculate capacity
        capacity_info = {"first_class": 0, "second_class": 0, "third_class": 0, "total": 0}
        schedule_capacity = capacity_by_schedule.get(schedule.train_schedule_id)

        if schedule_capacity:
            seg_caps = segment_capacities_by_schedule.get(schedule_capacity.id, [])
            
            # Find the specific segment capacity for this origin-destination pair
            matching_seg_cap = None
            for seg_cap in seg_caps:
                if (seg_cap.origin_station_id == origin_station_id and 
                    seg_cap.destination_station_id == destination_station_id):
                    matching_seg_cap = seg_cap
                    break
            
            if matching_seg_cap:
                capacity_info = {
                    "first_class": max(0, matching_seg_cap.max_first_class - matching_seg_cap.first_class_load),
                    "second_class": max(0, matching_seg_cap.max_second_class - matching_seg_cap.second_class_load),
                    "third_class": max(0, matching_seg_cap.max_third_class - matching_seg_cap.third_class_load),
                    "total": max(0, (matching_seg_cap.max_first_class - matching_seg_cap.first_class_load) +
                                   (matching_seg_cap.max_second_class - matching_seg_cap.second_class_load) +
                                   (matching_seg_cap.max_third_class - matching_seg_cap.third_class_load))
                }
        else:
            # Use default capacity
            default_cap = default_capacities.get(schedule.train_schedule_id)
            if default_cap:
                first_cap = default_cap.first_class_compartments * (
                    default_cap.seating_passengers_per_first_class + 
                    default_cap.standing_passengers_per_first_class
                )
                second_cap = default_cap.second_class_compartments * (
                    default_cap.seating_passengers_per_second_class + 
                    default_cap.standing_passengers_per_second_class
                )
                third_cap = default_cap.third_class_compartments * (
                    default_cap.seating_passengers_per_third_class + 
                    default_cap.standing_passengers_per_third_class
                )
                
                capacity_info = {
                    "first_class": first_cap,
                    "second_class": second_cap,
                    "third_class": third_cap,
                    "total": first_cap + second_cap + third_cap
                }

        # Build available classes
        available_classes = []
        if capacity_info.get("first_class", 0) > 0:
            available_classes.append({
                "class": "First",
                "available_seats": capacity_info.get("first_class", 0)
            })
        if capacity_info.get("second_class", 0) > 0:
            available_classes.append({
                "class": "Second",
                "available_seats": capacity_info.get("second_class", 0)
            })
        if capacity_info.get("third_class", 0) > 0:
            available_classes.append({
                "class": "Third",
                "available_seats": capacity_info.get("third_class", 0)
            })

        results.append({
            "train_schedule_id": schedule.train_schedule_id,
            "train_schedule": schedule.train_schedule,
            "route_id": schedule.route_id,
            "origin_station": station_cache.get(origin_station_id, origin_station_id),
            "origin_departure": origin_departure_time.strftime("%H:%M"),
            "destination_station": station_cache.get(destination_station_id, destination_station_id),
            "destination_departure": destination_arrival_time.strftime("%H:%M"),
            "duration": str(journey_duration),
            "available_classes": available_classes,
            "total_available_capacity": capacity_info.get("total", 0),
            "capacity_status": "available" if capacity_info.get("total", 0) > 0 else "full",
            "is_poya_day": is_poya,
            "is_holiday": is_holiday,
            "holiday_info": day_info.get("holiday_info", [])
        })

    logger.info(f"Returning {len(results)} available schedules")
    return results


@app.post("/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Create new schedule"""
    existing = db.query(TrainSchedule).filter(
        TrainSchedule.train_schedule_id == schedule_data.train_schedule_id
    ).first()

    if existing:
        raise ConflictError(f"Schedule {schedule_data.train_schedule_id} already exists")

    schedule = TrainSchedule(**schedule_data.model_dump())

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    logger.info(f"✅ Schedule created: {schedule.train_schedule_id}")
    return schedule

@app.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """Get specific schedule by ID"""
    schedule = db.query(TrainSchedule).filter(
        TrainSchedule.train_schedule_id == schedule_id
    ).first()
    if not schedule:
        raise ResourceNotFoundError(f"Schedule {schedule_id} not found")
    return schedule

@app.get("/schedule-by-station")
async def get_schedule_by_station(
    origin_station_id: str = Query(..., description="Origin station ID"),
    destination_station_id: Optional[str] = Query(None, description="Destination station ID (optional)"),
    travel_date: Optional[date] = Query(None, description="Travel date to filter by day of week"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get schedule segments by origin and optionally destination station, with day filtering"""
    
    # Build base query with JOIN to get schedule details including day columns
    query = db.query(
        TrainScheduleByStation,
        TrainSchedule.monday,
        TrainSchedule.tuesday,
        TrainSchedule.wednesday,
        TrainSchedule.thursday,
        TrainSchedule.friday,
        TrainSchedule.saturday,
        TrainSchedule.sunday,
        TrainSchedule.poya_day,
        TrainSchedule.holiday,
        TrainSchedule.status
    ).join(
        TrainSchedule,
        TrainScheduleByStation.train_schedule_id == TrainSchedule.train_schedule_id
    )
    
    # Filter by active schedules only
    query = query.filter(TrainSchedule.status == ScheduleStatus.Active)
    
    # Filter by origin station
    query = query.filter(TrainScheduleByStation.origin_station_id == origin_station_id)
    
    # Filter by destination station if provided
    if destination_station_id:
        query = query.filter(TrainScheduleByStation.destination_station_id == destination_station_id)
    
    # Filter by day of week if travel_date is provided
    if travel_date:
        # Get day type information
        try:
            day_info = get_day_type(travel_date)
            is_poya = day_info.get("is_poya_day", False)
            is_holiday = day_info.get("is_public_holiday", False)
            day_name = day_info.get("day_of_week", travel_date.strftime("%A").lower())
        except Exception as e:
            logger.warning(f"Calendar API error: {e}. Using fallback.")
            day_name = travel_date.strftime("%A").lower()
            is_poya = False
            is_holiday = False
        
        # Build day filter conditions
        day_filters = []
        if hasattr(TrainSchedule, day_name):
            day_column = getattr(TrainSchedule, day_name)
            day_filters.append(day_column == True)
        
        if is_poya:
            day_filters.append(TrainSchedule.poya_day == True)
        
        if is_holiday:
            day_filters.append(TrainSchedule.holiday == True)
        
        if day_filters:
            query = query.filter(or_(*day_filters))
    
    # Order by departure time
    query = query.order_by(TrainScheduleByStation.origin_departure)
    
    # Get results
    results_data = query.offset(skip).limit(limit).all()
    
    # Convert to response format
    results = []
    for row in results_data:
        seg = row[0]  # TrainScheduleByStation object
        results.append({
            "id": seg.id,
            "train_schedule_id": seg.train_schedule_id,
            "train_schedule": seg.train_schedule,
            "origin_station_id": seg.origin_station_id,
            "origin_station": seg.origin_station,
            "origin_departure": seg.origin_departure.strftime("%H:%M") if seg.origin_departure else None,
            "destination_station_id": seg.destination_station_id,
            "destination_station": seg.destination_station,
            "destination_departure": seg.destination_departure.strftime("%H:%M") if seg.destination_departure else None,
            "duration": str(seg.duration) if seg.duration else None,
            # Include day information
            "monday": row[1],
            "tuesday": row[2],
            "wednesday": row[3],
            "thursday": row[4],
            "friday": row[5],
            "saturday": row[6],
            "sunday": row[7],
            "poya_day": row[8],
            "holiday": row[9],
            "status": row[10].name if row[10] else "Active"
        })
    
    return results


@app.get("/schedule-by-station/{segment_id}")
async def get_schedule_segment(
    segment_id: int,
    db: Session = Depends(get_db)
):
    """Get a single schedule segment by ID"""
    segment = db.query(TrainScheduleByStation).filter(
        TrainScheduleByStation.id == segment_id
    ).first()
    
    if not segment:
        raise ResourceNotFoundError(f"Schedule segment {segment_id} not found")
    
    return {
        "id": segment.id,
        "train_schedule_id": segment.train_schedule_id,
        "train_schedule": segment.train_schedule,
        "origin_station_id": segment.origin_station_id,
        "origin_station": segment.origin_station,
        "origin_departure": segment.origin_departure.strftime("%H:%M") if segment.origin_departure else None,
        "destination_station_id": segment.destination_station_id,
        "destination_station": segment.destination_station,
        "destination_departure": segment.destination_departure.strftime("%H:%M") if segment.destination_departure else None,
        "duration": str(segment.duration) if segment.duration else None
    }


@app.put("/schedule-by-station/{segment_id}")
async def update_schedule_segment(
    segment_id: int,
    update_data: dict,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Update origin_departure and destination_departure times for a schedule segment"""
    segment = db.query(TrainScheduleByStation).filter(
        TrainScheduleByStation.id == segment_id
    ).first()
    
    if not segment:
        raise ResourceNotFoundError(f"Schedule segment {segment_id} not found")
    
    # Update times
    if "origin_departure" in update_data:
        from datetime import datetime, time
        time_str = update_data["origin_departure"]
        # Parse time string (HH:MM format)
        if isinstance(time_str, str):
            hours, minutes = map(int, time_str.split(':'))
            segment.origin_departure = time(hours, minutes)
    
    if "destination_departure" in update_data:
        from datetime import datetime, time
        time_str = update_data["destination_departure"]
        # Parse time string (HH:MM format)
        if isinstance(time_str, str):
            hours, minutes = map(int, time_str.split(':'))
            segment.destination_departure = time(hours, minutes)
    
    # Recalculate duration if both times are present
    if segment.origin_departure and segment.destination_departure:
        from datetime import datetime, timedelta
        origin_dt = datetime.combine(datetime.today(), segment.origin_departure)
        dest_dt = datetime.combine(datetime.today(), segment.destination_departure)
        
        # Handle overnight journeys
        if dest_dt < origin_dt:
            dest_dt += timedelta(days=1)
        
        segment.duration = dest_dt - origin_dt
    
    db.commit()
    db.refresh(segment)
    
    logger.info(f"✅ Schedule segment updated: {segment_id}")
    
    return {
        "id": segment.id,
        "train_schedule_id": segment.train_schedule_id,
        "origin_departure": segment.origin_departure.strftime("%H:%M") if segment.origin_departure else None,
        "destination_departure": segment.destination_departure.strftime("%H:%M") if segment.destination_departure else None,
        "duration": str(segment.duration) if segment.duration else None
    }


@app.patch("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Update schedule"""
    schedule = db.query(TrainSchedule).filter(
        TrainSchedule.train_schedule_id == schedule_id
    ).first()
    if not schedule:
        raise ResourceNotFoundError(f"Schedule {schedule_id} not found")

    # Update fields
    for key, value in schedule_data.model_dump(exclude_unset=True).items():
        if key == "status" and value:
            schedule.status = ScheduleStatus[value]
        else:
            setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)

    logger.info(f"✅ Schedule updated: {schedule_id}")
    return schedule

@app.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: str,
    current_user: UserProfile = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete schedule"""
    schedule = db.query(TrainSchedule).filter(
        TrainSchedule.train_schedule_id == schedule_id
    ).first()
    if not schedule:
        raise ResourceNotFoundError(f"Schedule {schedule_id} not found")

    # Check if schedule has active tickets
    tickets_for_schedule = db.query(Ticket).filter(
        Ticket.schedule_id == schedule_id,
        Ticket.booking_status.in_([TicketStatus.Confirmed, TicketStatus.Pending])
    ).first()

    if tickets_for_schedule:
        raise ConflictError(f"Cannot delete schedule {schedule_id} - it has active tickets")

    db.delete(schedule)
    db.commit()

    logger.info(f"✅ Schedule deleted: {schedule_id}")
    return None

# ============= TICKET PRICING =============
@app.get("/prices", response_model=List[PriceResponse])
async def get_prices(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get ticket prices"""
    today = date.today()
    query = db.query(TrainStationTicketPrice).options(
        joinedload(TrainStationTicketPrice.origin_station_rel),
        joinedload(TrainStationTicketPrice.destination_station_rel)
    )

    if origin:
        query = query.filter(TrainStationTicketPrice.origin_station_id == origin)
    if destination:
        query = query.filter(TrainStationTicketPrice.destination_station_id == destination)

    # Get currently active prices (started and not yet expired)
    prices = query.filter(
        and_(
            TrainStationTicketPrice.effective_from <= today,
            or_(
                TrainStationTicketPrice.effective_to.is_(None),
                TrainStationTicketPrice.effective_to >= today
            )
        )
    ).all()

    # Add station names to each price
    result = []
    for price in prices:
        price_dict = {
            "id": price.id,
            "origin_station_id": price.origin_station_id,
            "destination_station_id": price.destination_station_id,
            "origin_station_name": price.origin_station_rel.station_name if price.origin_station_rel else None,
            "destination_station_name": price.destination_station_rel.station_name if price.destination_station_rel else None,
            "distance": price.distance,
            "first_class_fee": price.first_class_fee,
            "second_class_fee": price.second_class_fee,
            "third_class_fee": price.third_class_fee,
            "effective_from": price.effective_from,
            "effective_to": price.effective_to
        }
        result.append(price_dict)

    return result

@app.post("/tickets/calculate-price", response_model=PriceCalculationResponse)
async def calculate_ticket_price(
    request: PriceCalculationRequest,
    db: Session = Depends(get_db)
):
    """Calculate ticket price"""
    today = date.today()
    
    # Query for active pricing: either no end date OR current date is within validity period
    pricing = db.query(TrainStationTicketPrice).filter(
        and_(
            TrainStationTicketPrice.origin_station_id == request.origin_station_id,
            TrainStationTicketPrice.destination_station_id == request.destination_station_id,
            TrainStationTicketPrice.effective_from <= today,
            or_(
                TrainStationTicketPrice.effective_to.is_(None),
                TrainStationTicketPrice.effective_to >= today
            )
        )
    ).first()

    if not pricing:
        raise ResourceNotFoundError("Pricing", f"{request.origin_station_id} → {request.destination_station_id}")

    # Updated class mapping for new enum values
    class_prices = {
        "First": float(pricing.first_class_fee),
        "Second": float(pricing.second_class_fee),
        "Third": float(pricing.third_class_fee)
    }

    base_price = class_prices.get(request.class_, class_prices["Third"])
    discount = calculate_child_discount(base_price, request.is_child)
    price_per_ticket = base_price - discount
    total = price_per_ticket * request.passengers

    return PriceCalculationResponse(
        base_price=Decimal(str(base_price)),
        discount=Decimal(str(discount)),
        passengers=request.passengers,
        total=Decimal(str(total))
    )

@app.post("/prices", response_model=PriceResponse, status_code=status.HTTP_201_CREATED)
async def create_price(
    price_data: PriceCreate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Create ticket pricing"""
    validate_price_structure(
        float(price_data.first_class_fee),
        float(price_data.second_class_fee),
        float(price_data.third_class_fee)
    )

    # Expire old pricing
    db.query(TrainStationTicketPrice).filter(
        and_(
            TrainStationTicketPrice.origin_station_id == price_data.origin_station_id,
            TrainStationTicketPrice.destination_station_id == price_data.destination_station_id,
            TrainStationTicketPrice.effective_to.is_(None)
        )
    ).update({"effective_to": date.today()})

    pricing = TrainStationTicketPrice(**price_data.model_dump())

    db.add(pricing)
    db.commit()
    db.refresh(pricing)

    logger.info(f"✅ Pricing created: {price_data.origin_station_id} → {price_data.destination_station_id}")
    return pricing

@app.get("/prices/{price_id}", response_model=PriceResponse)
async def get_price(
    price_id: int,
    db: Session = Depends(get_db)
):
    """Get specific price by ID"""
    price = db.query(TrainStationTicketPrice).options(
        joinedload(TrainStationTicketPrice.origin_station_rel),
        joinedload(TrainStationTicketPrice.destination_station_rel)
    ).filter(
        TrainStationTicketPrice.id == price_id
    ).first()
    if not price:
        raise ResourceNotFoundError(f"Price {price_id} not found")
    
    # Add station names
    price_dict = {
        "id": price.id,
        "origin_station_id": price.origin_station_id,
        "destination_station_id": price.destination_station_id,
        "origin_station_name": price.origin_station_rel.station_name if price.origin_station_rel else None,
        "destination_station_name": price.destination_station_rel.station_name if price.destination_station_rel else None,
        "distance": price.distance,
        "first_class_fee": price.first_class_fee,
        "second_class_fee": price.second_class_fee,
        "third_class_fee": price.third_class_fee,
        "effective_from": price.effective_from,
        "effective_to": price.effective_to
    }
    return price_dict

@app.patch("/prices/{price_id}", response_model=PriceResponse)
async def update_price(
    price_id: int,
    price_data: PriceUpdate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Update ticket pricing"""
    price = db.query(TrainStationTicketPrice).options(
        joinedload(TrainStationTicketPrice.origin_station_rel),
        joinedload(TrainStationTicketPrice.destination_station_rel)
    ).filter(
        TrainStationTicketPrice.id == price_id
    ).first()
    if not price:
        raise ResourceNotFoundError(f"Price {price_id} not found")

    # Validate price structure if any price fields are being updated
    update_dict = price_data.model_dump(exclude_unset=True)
    if any(key in update_dict for key in ['first_class_fee', 'second_class_fee', 'third_class_fee']):
        validate_price_structure(
            float(update_dict.get('first_class_fee', price.first_class_fee)),
            float(update_dict.get('second_class_fee', price.second_class_fee)),
            float(update_dict.get('third_class_fee', price.third_class_fee))
        )

    # Update fields
    for key, value in update_dict.items():
        setattr(price, key, value)

    db.commit()
    db.refresh(price)

    logger.info(f"✅ Pricing updated: {price_id}")
    
    # Return with station names
    price_dict = {
        "id": price.id,
        "origin_station_id": price.origin_station_id,
        "destination_station_id": price.destination_station_id,
        "origin_station_name": price.origin_station_rel.station_name if price.origin_station_rel else None,
        "destination_station_name": price.destination_station_rel.station_name if price.destination_station_rel else None,
        "distance": price.distance,
        "first_class_fee": price.first_class_fee,
        "second_class_fee": price.second_class_fee,
        "third_class_fee": price.third_class_fee,
        "effective_from": price.effective_from,
        "effective_to": price.effective_to
    }
    return price_dict

@app.delete("/prices/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price(
    price_id: int,
    current_user: UserProfile = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete or expire ticket pricing"""
    price = db.query(TrainStationTicketPrice).filter(
        TrainStationTicketPrice.price_id == price_id
    ).first()
    if not price:
        raise ResourceNotFoundError(f"Price {price_id} not found")

    # Instead of hard delete, expire the pricing
    price.effective_to = date.today()
    db.commit()

    logger.info(f"✅ Pricing expired: {price_id}")
    return None

# ============= TICKETS =============
@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db)
):
    """Create ticket"""
    logger.info(f"🎫 Creating ticket for NIC:{ticket_data.nic} Passport:{ticket_data.passport}")

    # Validate passenger ID
    if not ticket_data.nic and not ticket_data.passport:
        raise ValidationError("Either NIC or Passport is required")

    # Validate schedule
    schedule = db.query(TrainSchedule).filter(
        TrainSchedule.train_schedule_id == ticket_data.schedule_id,
        TrainSchedule.status == ScheduleStatus.Active
    ).first()

    if not schedule:
        raise ResourceNotFoundError("Schedule", ticket_data.schedule_id)

    # Map class enum
    class_map = {
        "First": TrainClass.First,
        "Second": TrainClass.Second,
        "Third": TrainClass.Third
    }

    # Check capacity availability
    from backend.services.capacity_service import can_book_ticket, get_or_create_schedule_capacity, increment_segment_loads

    train_class = class_map[ticket_data.class_]
    can_book, reason, bottleneck = can_book_ticket(
        db,
        ticket_data.schedule_id,
        ticket_data.schedule_date,
        ticket_data.origin_station_id,
        ticket_data.destination_station_id,
        train_class,
        num_passengers=1
    )

    if not can_book:
        logger.warning(f"⚠️ Booking rejected: {reason}")
        raise ValidationError(f"Cannot book ticket: {reason}")

    # Get schedule capacity ID for load increment
    schedule_capacity = get_or_create_schedule_capacity(
        db,
        ticket_data.schedule_id,
        ticket_data.schedule_date
    )

    if not schedule_capacity:
        raise ValidationError("Schedule does not operate on this date")

    ticket_id = generate_ticket_id()

    ticket = Ticket(
        ticket_id=ticket_id,
        nic=ticket_data.nic,
        passport=ticket_data.passport,
        contact_number=ticket_data.contact_number,
        is_child=ticket_data.is_child,
        schedule_id=ticket_data.schedule_id,
        origin_station_id=ticket_data.origin_station_id,
        destination_station_id=ticket_data.destination_station_id,
        origin_departure=ticket_data.origin_departure,
        destination_departure=ticket_data.destination_departure,
        schedule_date=ticket_data.schedule_date,
        class_=train_class,
        fee=ticket_data.fee,
        payment_method=PaymentMethod[ticket_data.payment_method],
        payment_status=PaymentStatus.Pending,
        booking_platform=BookingPlatform[ticket_data.booking_platform],
        issue_date=ticket_data.issue_date,
        status=TicketStatus.Pending
    )

    db.add(ticket)
    db.flush()  # Flush to get ticket ID before incrementing loads

    # Increment segment loads
    increment_segment_loads(
        db,
        schedule_capacity.id,
        ticket_data.origin_station_id,
        ticket_data.destination_station_id,
        train_class,
        num_passengers=1
    )

    db.commit()
    db.refresh(ticket)

    logger.info(f"✅ Ticket created: {ticket.ticket_id}")

    return ticket

@app.get("/tickets", response_model=List[TicketResponse])
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    schedule_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get tickets"""
    query = db.query(Ticket).order_by(Ticket.created_at.desc())

    if schedule_date:
        query = query.filter(Ticket.schedule_date == schedule_date)

    if status:
        try:
            status_enum = TicketStatus[status]
            query = query.filter(Ticket.status == status_enum)
        except KeyError:
            raise ValidationError(f"Invalid status: {status}")

    tickets = query.offset(skip).limit(limit).all()
    return tickets

@app.get("/tickets/recent", response_model=List[TicketResponse])
async def get_recent_tickets(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get recent tickets"""
    tickets = db.query(Ticket).order_by(
        Ticket.created_at.desc()
    ).limit(limit).all()
    return tickets

@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket_by_id(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """Get specific ticket by ID"""
    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        raise ResourceNotFoundError("Ticket", ticket_id)

    return ticket

@app.patch("/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    ticket_update: TicketUpdate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update ticket status and release capacity if cancelled/refunded"""
    logger.info(f"Updating ticket {ticket_id}")

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        raise ResourceNotFoundError("Ticket", ticket_id)

    # Store old status to detect changes
    old_status = ticket.status

    # Update status if provided
    if ticket_update.status:
        new_status = TicketStatus[ticket_update.status]
        ticket.status = new_status

        # Release capacity if ticket is being cancelled/refunded/no-show
        # and it was previously in a state that held capacity (Pending or Completed)
        should_release_capacity = (
            new_status in [TicketStatus.Cancelled, TicketStatus.Refunded, TicketStatus.NoShow] and
            old_status in [TicketStatus.Pending, TicketStatus.Completed]
        )

        if should_release_capacity:
            try:
                from backend.services.capacity_service import decrement_segment_loads, get_or_create_schedule_capacity
                from backend.models import TrainClass

                # Get schedule capacity
                schedule_capacity = get_or_create_schedule_capacity(
                    db,
                    ticket.schedule_id,
                    ticket.travel_date
                )

                if schedule_capacity:
                    # Map class name to TrainClass enum
                    train_class = TrainClass[ticket.class_.replace(" ", "")]

                    # Release capacity on all segments
                    decrement_segment_loads(
                        db=db,
                        schedule_capacity_id=schedule_capacity.id,
                        origin_station_id=ticket.origin_station_id,
                        destination_station_id=ticket.destination_station_id,
                        train_class=train_class,
                        num_passengers=ticket.number_of_passengers
                    )

                    logger.info(
                        f"✅ Released capacity for ticket {ticket_id}: "
                        f"{ticket.number_of_passengers} passengers in {ticket.class_} class"
                    )
                else:
                    logger.warning(f"Could not find schedule capacity for ticket {ticket_id}")

            except Exception as e:
                logger.error(f"Failed to release capacity for ticket {ticket_id}: {e}")
                # Don't fail the whole request if capacity release fails
                # Status update will still proceed

    if ticket_update.payment_status:
        ticket.payment_status = PaymentStatus[ticket_update.payment_status]

    db.commit()
    db.refresh(ticket)

    logger.info(f"✅ Ticket {ticket_id} updated (status: {ticket.status})")

    return ticket

# ============= DAILY SCHEDULES =============
@app.get("/daily-schedules")
async def get_daily_schedules(
    schedule_date: Optional[date] = Query(None, description="Filter by specific date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    train_id: Optional[str] = Query(None, description="Filter by train"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get daily schedules for a specific date or range with AI predictions"""
    from backend.ai_models import CompartmentPrediction
    
    target_date = schedule_date or date.today()

    # Get day of week column name
    day_columns = {
        0: TrainSchedule.monday,
        1: TrainSchedule.tuesday,
        2: TrainSchedule.wednesday,
        3: TrainSchedule.thursday,
        4: TrainSchedule.friday,
        5: TrainSchedule.saturday,
        6: TrainSchedule.sunday
    }
    day_column = day_columns[target_date.weekday()]

    # Check if it's a special day
    day_info = get_day_type(target_date)
    is_poya = day_info.get("is_poya_day", False)
    is_holiday = day_info.get("is_public_holiday", False)

    # Build filters
    schedule_filters = [day_column == True]
    if is_poya:
        schedule_filters.append(TrainSchedule.poya_day == True)
    if is_holiday:
        schedule_filters.append(TrainSchedule.holiday == True)

    # Query schedules
    query = db.query(TrainSchedule).filter(
        and_(
            TrainSchedule.status == ScheduleStatus.Active,
            or_(*schedule_filters)
        )
    )

    # Apply additional filters
    if status:
        query = query.filter(TrainSchedule.status == ScheduleStatus[status])
    if train_id:
        query = query.filter(TrainSchedule.train_id == train_id)

    schedules = query.order_by(TrainSchedule.origin_departure).offset(skip).limit(limit).all()

    # Build response with additional date context and AI predictions
    schedules_with_predictions = []
    for s in schedules:
        # Get AI prediction for this schedule and date
        prediction = db.query(CompartmentPrediction).filter(
            CompartmentPrediction.schedule_id == s.train_schedule_id,
            CompartmentPrediction.schedule_date == target_date,
            CompartmentPrediction.is_active == 1
        ).first()
        
        schedule_data = {
            "train_schedule_id": s.train_schedule_id,
            "train_schedule": s.train_schedule,
            "route_id": s.route_id,
            "origin_station_id": s.origin_station_id,
            "origin_station": s.origin_station,
            "origin_departure": s.origin_departure.strftime("%H:%M") if s.origin_departure else None,
            "destination_station_id": s.destination_station_id,
            "destination_station": s.destination_station,
            "destination_departure": s.destination_departure.strftime("%H:%M") if s.destination_departure else None,
            "status": s.status.name,
            "prediction": None
        }
        
        if prediction:
            schedule_data["prediction"] = {
                "prediction_id": prediction.id,
                "predicted_first_class": prediction.predicted_first_class,
                "predicted_second_class": prediction.predicted_second_class,
                "predicted_third_class": prediction.predicted_third_class,
                "total_compartments": prediction.total_compartments,
                "expected_total_passengers": prediction.expected_total_passengers,
                "confidence_score": float(prediction.confidence_score) if prediction.confidence_score else None,
                "reasoning": prediction.reasoning,
                "predicted_at": prediction.predicted_at.strftime("%Y-%m-%d %H:%M:%S") if prediction.predicted_at else None
            }
        
        schedules_with_predictions.append(schedule_data)
    
    return {
        "date": target_date.isoformat(),
        "day_of_week": target_date.strftime("%A"),
        "is_poya_day": is_poya,
        "is_holiday": is_holiday,
        "total_schedules": len(schedules),
        "schedules": schedules_with_predictions
    }

@app.patch("/daily-schedules/{schedule_id}/status")
async def update_daily_schedule_status(
    schedule_id: str,
    status: str = Query(..., description="New status (Scheduled, In Progress, Completed, Cancelled, Delayed)"),
    current_user: UserProfile = Depends(require_role("admin", "manager", "operator")),
    db: Session = Depends(get_db)
):
    """Update the status of a daily schedule"""
    schedule = db.query(TrainSchedule).filter(
        TrainSchedule.train_schedule_id == schedule_id
    ).first()

    if not schedule:
        raise ResourceNotFoundError(f"Schedule {schedule_id} not found")

    # Validate status
    try:
        new_status = ScheduleStatus[status]
    except KeyError:
        raise ValidationError(f"Invalid status: {status}")

    schedule.status = new_status
    db.commit()
    db.refresh(schedule)

    logger.info(f"✅ Schedule {schedule_id} status updated to {status}")
    return {
        "train_schedule_id": schedule.train_schedule_id,
        "status": schedule.status.name,
        "message": f"Schedule status updated to {status}"
    }

# ============= ANALYTICS =============
@app.get("/analytics/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get dashboard analytics - OPTIMIZED with single-query aggregations"""
    today = date.today()
    
    # Get day type information (Poya day, holiday, day of week)
    try:
        day_info = get_day_type(today)
        is_poya = day_info.get("is_poya_day", False)
        is_holiday = day_info.get("is_public_holiday", False)
        day_name = day_info.get("day_of_week", today.strftime("%A").lower())
    except Exception as e:
        logger.warning(f"Calendarific API error: {e}. Using fallback.")
        day_name = today.strftime("%A").lower()
        is_poya = False
        is_holiday = False
    
    logger.info(f"Analytics for {today}: {day_name}, Poya: {is_poya}, Holiday: {is_holiday}")

    # OPTIMIZED: Single query for ticket metrics (count + revenue in one DB call)
    # Only count valid tickets (exclude Cancelled, Refunded, NoShow)
    # Revenue from tickets with Paid OR Pending status (expected revenue)
    from sqlalchemy import case
    
    ticket_metrics = db.query(
        func.count(Ticket.ticket_id).label('ticket_count'),
        func.coalesce(
            func.sum(
                case(
                    (Ticket.payment_status.in_([PaymentStatus.Paid, PaymentStatus.Pending]), Ticket.fee),
                    else_=0
                )
            ), 
            0
        ).label('total_revenue')
    ).filter(
        and_(
            Ticket.issue_date == today,
            # Only count active tickets (exclude cancelled, refunded, no-show)
            Ticket.status.in_([TicketStatus.Pending, TicketStatus.Completed])
        )
    ).first()
    
    tickets_today = ticket_metrics.ticket_count if ticket_metrics else 0
    passengers_today = tickets_today
    revenue_today = Decimal(str(ticket_metrics.total_revenue)) if ticket_metrics else Decimal("0")

    # Trains scheduled to run today - SERVER-SIDE counting with day/poya/holiday filters
    trains_scheduled_today = 0
    if hasattr(TrainSchedule, day_name):
        day_column = getattr(TrainSchedule, day_name)
        
        # Build day filter conditions (evaluated on database server)
        day_filters = [day_column == True]
        if is_poya:
            day_filters.append(TrainSchedule.poya_day == True)
        if is_holiday:
            day_filters.append(TrainSchedule.holiday == True)
        
        # Single COUNT query executed on database server
        trains_scheduled_today = db.query(func.count(TrainSchedule.train_schedule_id)).filter(
            and_(
                TrainSchedule.status == ScheduleStatus.Active,
                or_(*day_filters)
            )
        ).scalar() or 0
    else:
        logger.warning(f"Invalid day name: {day_name}")
        trains_scheduled_today = 0

    # OPTIMIZED: Single query for active trains count (distinct count on server)
    trains_active_today = db.query(
        func.count(func.distinct(ScheduleCapacity.schedule_id))
    ).filter(
        ScheduleCapacity.schedule_date == today
    ).scalar() or 0

    # If no schedule capacities exist, assume all scheduled trains are active
    if trains_active_today == 0:
        trains_active_today = trains_scheduled_today

    # Route count (simple server-side count)
    active_routes = db.query(func.count(TrainRoute.route_id)).scalar() or 0
    
    avg_utilization = "75%"

    return AnalyticsSummary(
        total_tickets_today=tickets_today,
        total_passengers_today=passengers_today,
        trains_active_today=trains_active_today,
        trains_scheduled_today=trains_scheduled_today,
        revenue_today=revenue_today,
        avg_utilization=avg_utilization,
        active_routes=active_routes
    )

@app.get("/analytics/weekly-sales", response_model=WeeklySales)
async def get_weekly_sales(db: Session = Depends(get_db)):
    """Get weekly sales data"""
    dates = [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

    passengers = []
    revenue = []

    for d in dates:
        count = db.query(func.count(Ticket.ticket_id)).filter(
            Ticket.issue_date == d
        ).scalar() or 0
        passengers.append(count)

        rev = db.query(func.sum(Ticket.fee)).filter(
            and_(
                Ticket.issue_date == d,
                Ticket.payment_status == PaymentStatus.Paid
            )
        ).scalar() or Decimal("0")
        revenue.append(rev)

    return WeeklySales(
        dates=dates,
        passengers=passengers,
        revenue=revenue
    )

@app.get("/analytics/top-routes", response_model=List[TopRoute])
async def get_top_routes(
    limit: int = Query(5, le=10),
    db: Session = Depends(get_db)
):
    """Get top routes by ticket sales"""
    today = date.today()

    # Use origin and destination station IDs to group
    route_stats = db.query(
        TrainStation.station_name.label('origin_name'),
        func.count(Ticket.ticket_id).label('count'),
        func.sum(Ticket.fee).label('revenue')
    ).join(
        TrainStation,
        TrainStation.station_id == Ticket.origin_station_id
    ).filter(
        Ticket.issue_date == today
    ).group_by(
        TrainStation.station_name
    ).order_by(
        desc('count')
    ).limit(limit).all()

    results = []
    for origin_name, count, revenue in route_stats:
        results.append(TopRoute(
            route_name=origin_name,
            passengers=count,
            revenue=revenue or Decimal("0")
        ))

    return results

@app.get("/analytics/daily-ticket-sales", response_model=DailyTicketSales)
async def get_daily_ticket_sales(
    days: int = Query(30, le=90),
    db: Session = Depends(get_db)
):
    """Get daily ticket sales for the last N days - OPTIMIZED with single GROUP BY query"""
    today = date.today()
    start_date = today - timedelta(days=days - 1)
    
    # SINGLE SERVER-SIDE QUERY: Group by date and count tickets
    results = db.query(
        Ticket.issue_date,
        func.count(Ticket.ticket_id).label('ticket_count')
    ).filter(
        and_(
            Ticket.issue_date >= start_date,
            Ticket.issue_date <= today
        )
    ).group_by(
        Ticket.issue_date
    ).order_by(
        Ticket.issue_date
    ).all()
    
    # Create a dictionary for fast lookup
    ticket_counts = {row.issue_date: row.ticket_count for row in results}
    
    # Generate complete date range and fill in counts (0 for days with no tickets)
    dates = []
    tickets = []
    
    for i in range(days - 1, -1, -1):
        current_date = today - timedelta(days=i)
        dates.append(current_date.isoformat())
        tickets.append(ticket_counts.get(current_date, 0))

    return DailyTicketSales(dates=dates, tickets=tickets)

@app.get("/analytics/schedule-status-today", response_model=ScheduleStatusToday)
async def get_schedule_status_today(db: Session = Depends(get_db)):
    """Get completed vs pending train schedules for today - SERVER-SIDE time comparison"""
    today = date.today()
    
    # Get current time in Sri Lanka timezone (UTC+5:30)
    sri_lanka_tz = timezone(timedelta(hours=5, minutes=30))
    current_datetime_sl = datetime.now(sri_lanka_tz)
    current_time_sl = current_datetime_sl.time()
    
    # Get day type information (Poya day, holiday, day of week)
    try:
        day_info = get_day_type(today)
        is_poya = day_info.get("is_poya_day", False)
        is_holiday = day_info.get("is_public_holiday", False)
        day_name = day_info.get("day_of_week", today.strftime("%A").lower())
    except Exception as e:
        logger.warning(f"Calendarific API error: {e}. Using fallback.")
        day_name = today.strftime("%A").lower()
        is_poya = False
        is_holiday = False

    # Get all schedules that should run today
    if not hasattr(TrainSchedule, day_name):
        return ScheduleStatusToday(completed=0, pending=0)

    day_column = getattr(TrainSchedule, day_name)
    
    # Build day filter conditions
    day_filters = [day_column == True]
    if is_poya:
        day_filters.append(TrainSchedule.poya_day == True)
    if is_holiday:
        day_filters.append(TrainSchedule.holiday == True)

    # SERVER-SIDE query: Count completed trains (destination_departure < current_time)
    # Use CASE to count based on time comparison directly in SQL
    from sqlalchemy import case as sql_case
    
    completed = db.query(
        func.count(
            sql_case(
                (TrainSchedule.destination_departure < current_time_sl, 1),
                else_=None
            )
        )
    ).filter(
        and_(
            TrainSchedule.status == ScheduleStatus.Active,
            or_(*day_filters)
        )
    ).scalar() or 0

    # SERVER-SIDE query: Count pending trains (destination_departure >= current_time)
    pending = db.query(
        func.count(
            sql_case(
                (TrainSchedule.destination_departure >= current_time_sl, 1),
                else_=None
            )
        )
    ).filter(
        and_(
            TrainSchedule.status == ScheduleStatus.Active,
            or_(*day_filters)
        )
    ).scalar() or 0

    logger.info(f"Schedule status for {today} at {current_time_sl}: Completed={completed}, Pending={pending}")

    return ScheduleStatusToday(completed=completed, pending=pending)

@app.get("/analytics/class-distribution-today", response_model=ClassDistributionToday)
async def get_class_distribution_today(db: Session = Depends(get_db)):
    """Get ticket class distribution for today - OPTIMIZED single query"""
    today = date.today()

    # OPTIMIZED: Single query with CASE to count all classes at once
    # Only count active tickets (exclude Cancelled, Refunded, NoShow)
    from sqlalchemy import case as sql_case
    
    results = db.query(
        func.count(
            sql_case(
                (Ticket.class_ == TrainClass.First, 1),
                else_=None
            )
        ).label('first_class'),
        func.count(
            sql_case(
                (Ticket.class_ == TrainClass.Second, 1),
                else_=None
            )
        ).label('second_class'),
        func.count(
            sql_case(
                (Ticket.class_ == TrainClass.Third, 1),
                else_=None
            )
        ).label('third_class')
    ).filter(
        and_(
            Ticket.issue_date == today,
            # Only count active tickets (exclude cancelled, refunded, no-show)
            Ticket.status.in_([TicketStatus.Pending, TicketStatus.Completed])
        )
    ).first()

    return ClassDistributionToday(
        first_class=results.first_class if results else 0,
        second_class=results.second_class if results else 0,
        third_class=results.third_class if results else 0
    )

# ============= TRAIN ALLOCATION =============
@app.post("/allocate-train", response_model=TrainAllocationResponse)
async def allocate_train(
    request: TrainAllocationRequest,
    current_user: UserProfile = Depends(require_role("admin", "manager", "operator")),
    db: Session = Depends(get_db)
):
    """Smart train allocation"""
    logger.info(f"🚂 Allocating train for {request.schedule_id} on {request.date}")

    try:
        allocator = TrainAllocationOptimizer(db)
        result = allocator.allocate_trains_for_date(request.date)

        if not result["success"]:
            raise ValidationError(result.get("message", "Allocation failed"))

        allocation = next(
            (a for a in result["allocations"] if a["schedule_id"] == request.schedule_id),
            None
        )

        if not allocation:
            raise ResourceNotFoundError("Allocation", request.schedule_id)

        return TrainAllocationResponse(
            train_id=allocation["train_id"],
            schedule_id=allocation["schedule_id"],
            date=request.date,
            reason=allocation.get("reason", "Optimal allocation"),
            efficiency_score=allocation.get("efficiency_score", 0.0),
            first_class_compartments=allocation["first_class"],
            second_class_compartments=allocation["second_class"],
            third_class_compartments=allocation["third_class"]
        )

    except Exception as e:
        logger.error(f"Allocation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= COMPARTMENT FORECASTING =============
@app.post("/predict-compartments", response_model=CompartmentPredictionResponse)
async def predict_compartments(
    request: CompartmentPredictionRequest,
    current_user: UserProfile = Depends(require_role("admin", "manager", "operator")),
    db: Session = Depends(get_db)
):
    """Compartment class prediction"""
    logger.info(f"🔮 Predicting compartments for {request.schedule_id}")

    try:
        prediction = predict_for_schedule(
            db=db,
            schedule_id=request.schedule_id,
            route_id=request.route_id,
            train_id=request.train_id,
            target_date=request.date
        )

        return CompartmentPredictionResponse(
            first_class=prediction["first"],
            second_class=prediction["second"],
            third_class=prediction["third"],
            confidence=0.85,
            reasoning="Based on route type, pricing, and historical demand"
        )

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= HEALTH CHECK =============
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "version": "6.0.0",
            "schema_version": "2.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
