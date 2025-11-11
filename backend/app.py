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
from datetime import datetime, timedelta, date, time as time_type
from typing import Optional, List
from decimal import Decimal
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
    PaymentStatus, ScheduleCapacity, SegmentCapacity
)

# Import schemas (updated for v2.0)
from backend.schemas import (
    UserCreate, UserResponse, UserUpdate,
    StationCreate, StationResponse, StationUpdate,
    OperationalTrainCreate, OperationalTrainResponse, OperationalTrainUpdate,
    TrainModelCreate, TrainModelResponse,
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
    model_data: TrainModelCreate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Update train model"""
    model = db.query(TrainModel).filter(TrainModel.model_id == model_id).first()
    if not model:
        raise ResourceNotFoundError(f"Train model {model_id} not found")

    # Update fields
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
    limit: int = Query(100, le=500),
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

    trains = query.offset(skip).limit(limit).all()
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
    train = db.query(OperationalTrain).filter(
        OperationalTrain.train_id == train_id
    ).first()
    validate_resource_exists(train, "Train", train_id)

    if train_update.status:
        train.status = TrainStatus[train_update.status]

    db.commit()
    db.refresh(train)

    logger.info(f"✅ Train updated: {train.train_id}")
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

    schedules = query.offset(skip).limit(limit).all()
    return schedules

@app.get("/schedules/available")
async def get_available_schedules(
    origin_station_id: str = Query(...),
    destination_station_id: str = Query(...),
    travel_date: date = Query(...),
    db: Session = Depends(get_db)
):
    """Find available schedules for booking"""
    logger.info(f"Finding schedules: {origin_station_id} → {destination_station_id} on {travel_date}")

    # Get day type information from Calendarific API (with timeout protection)
    try:
        day_info = get_day_type(travel_date)
        is_poya = day_info.get("is_poya_day", False)
        is_holiday = day_info.get("is_public_holiday", False)
        day_name = day_info.get("day_of_week", travel_date.strftime("%A").lower())
    except Exception as e:
        logger.warning(f"Calendarific API error: {e}. Using fallback.")
        # Fallback to basic day calculation
        day_name = travel_date.strftime("%A").lower()
        is_poya = False
        is_holiday = False

    logger.info(f"Date analysis: {travel_date} - Day: {day_name}, Poya: {is_poya}, Holiday: {is_holiday}")

    # Get schedules for the specific day of week
    if not hasattr(TrainSchedule, day_name):
        return []

    day_column = getattr(TrainSchedule, day_name)

    # Find schedules that operate on this day and have both stations
    schedule_ids_with_origin = db.query(TrainScheduleByStation.train_schedule_id).filter(
        TrainScheduleByStation.origin_station_id == origin_station_id
    ).distinct()

    schedule_ids_with_dest = db.query(TrainScheduleByStation.train_schedule_id).filter(
        TrainScheduleByStation.destination_station_id == destination_station_id
    ).distinct()

    # Get intersection
    common_schedule_ids = set(s[0] for s in schedule_ids_with_origin).intersection(
        set(s[0] for s in schedule_ids_with_dest)
    )

    if not common_schedule_ids:
        return []

    # Build schedule filter conditions
    # A schedule should be included if:
    # 1. It runs on this day of the week (day_column == True), OR
    # 2. It's configured to run on Poya days and today is a Poya day, OR
    # 3. It's configured to run on holidays and today is a holiday
    schedule_filters = [day_column == True]

    if is_poya:
        schedule_filters.append(TrainSchedule.poya_day == True)

    if is_holiday:
        schedule_filters.append(TrainSchedule.holiday == True)

    # Get active schedules matching any of the conditions
    schedules = db.query(TrainSchedule).filter(
        and_(
            TrainSchedule.train_schedule_id.in_(common_schedule_ids),
            TrainSchedule.status == ScheduleStatus.Active,
            or_(*schedule_filters)  # Match any condition: regular day, poya day, or holiday
        )
    ).order_by(TrainSchedule.origin_departure).all()

    # Build response
    results = []
    for schedule in schedules:
        # Get timing details
        segment = db.query(TrainScheduleByStation).filter(
            and_(
                TrainScheduleByStation.train_schedule_id == schedule.train_schedule_id,
                TrainScheduleByStation.origin_station_id == origin_station_id,
                TrainScheduleByStation.destination_station_id == destination_station_id
            )
        ).first()

        if segment:
            # Get capacity information for this route
            from backend.services.capacity_service import get_available_capacity

            capacity_info = get_available_capacity(
                db,
                schedule.train_schedule_id,
                travel_date,
                origin_station_id,
                destination_station_id
            )

            # Build available classes with capacity
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
                "origin_station": segment.origin_station,
                "origin_departure": segment.origin_departure.strftime("%H:%M"),
                "destination_station": segment.destination_station,
                "destination_departure": segment.destination_departure.strftime("%H:%M"),
                "duration": str(segment.duration),
                "available_classes": available_classes,
                "total_available_capacity": capacity_info.get("total", 0),
                "capacity_status": "available" if capacity_info.get("total", 0) > 0 else "full",
                "is_poya_day": is_poya,
                "is_holiday": is_holiday,
                "holiday_info": day_info.get("holiday_info", [])
            })

    logger.info(f"Returning {len(results)} available schedules (Poya: {is_poya}, Holiday: {is_holiday})")
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
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """Get ticket prices"""
    query = db.query(TrainStationTicketPrice)

    if origin:
        query = query.filter(TrainStationTicketPrice.origin_station_id == origin)
    if destination:
        query = query.filter(TrainStationTicketPrice.destination_station_id == destination)

    prices = query.filter(
        TrainStationTicketPrice.effective_to.is_(None)
    ).offset(skip).limit(limit).all()

    return prices

@app.post("/tickets/calculate-price", response_model=PriceCalculationResponse)
async def calculate_ticket_price(
    request: PriceCalculationRequest,
    db: Session = Depends(get_db)
):
    """Calculate ticket price"""
    pricing = db.query(TrainStationTicketPrice).filter(
        and_(
            TrainStationTicketPrice.origin_station_id == request.origin_station_id,
            TrainStationTicketPrice.destination_station_id == request.destination_station_id,
            TrainStationTicketPrice.effective_to.is_(None)
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
    price = db.query(TrainStationTicketPrice).filter(
        TrainStationTicketPrice.price_id == price_id
    ).first()
    if not price:
        raise ResourceNotFoundError(f"Price {price_id} not found")
    return price

@app.patch("/prices/{price_id}", response_model=PriceResponse)
async def update_price(
    price_id: int,
    price_data: PriceUpdate,
    current_user: UserProfile = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """Update ticket pricing"""
    price = db.query(TrainStationTicketPrice).filter(
        TrainStationTicketPrice.price_id == price_id
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
    return price

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
    """Update ticket status"""
    logger.info(f"Updating ticket {ticket_id}")

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        raise ResourceNotFoundError("Ticket", ticket_id)

    if ticket_update.status:
        ticket.status = TicketStatus[ticket_update.status]

    if ticket_update.payment_status:
        ticket.payment_status = PaymentStatus[ticket_update.payment_status]

    db.commit()
    db.refresh(ticket)

    logger.info(f"✅ Ticket {ticket_id} updated")

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
    """Get daily schedules for a specific date or range"""
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
    day_type = get_day_type(target_date)
    is_poya = day_type == "poya_day"
    is_holiday = day_type == "holiday"

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

    # Build response with additional date context
    return {
        "date": target_date,
        "day_of_week": target_date.strftime("%A"),
        "is_poya_day": is_poya,
        "is_holiday": is_holiday,
        "total_schedules": len(schedules),
        "schedules": [
            {
                "train_schedule_id": s.train_schedule_id,
                "train_id": s.train_id,
                "route_id": s.route_id,
                "origin_departure": s.origin_departure.strftime("%H:%M") if s.origin_departure else None,
                "destination_arrival": s.destination_arrival.strftime("%H:%M") if s.destination_arrival else None,
                "status": s.status.name,
                "available_classes": {
                    "first": s.first_class_available,
                    "second": s.second_class_available,
                    "third": s.third_class_available
                }
            }
            for s in schedules
        ]
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
    """Get dashboard analytics"""
    today = date.today()
    day_name = today.strftime("%A").lower()

    # Tickets booked today
    tickets_today = db.query(func.count(Ticket.ticket_id)).filter(
        Ticket.issue_date == today
    ).scalar() or 0

    passengers_today = tickets_today

    # Revenue today (from all tickets booked today)
    revenue_today = db.query(func.sum(Ticket.fee)).filter(
        Ticket.issue_date == today
    ).scalar() or Decimal("0")

    # Trains scheduled to run today
    if hasattr(TrainSchedule, day_name):
        day_column = getattr(TrainSchedule, day_name)
        trains_scheduled_today = db.query(func.count(TrainSchedule.train_schedule_id)).filter(
            and_(
                day_column == True,
                TrainSchedule.status == ScheduleStatus.Active
            )
        ).scalar() or 0
    else:
        trains_scheduled_today = 0

    # Trains active today (schedules that have capacity entries for today)
    trains_active_today = db.query(func.count(func.distinct(ScheduleCapacity.schedule_id))).filter(
        ScheduleCapacity.schedule_date == today
    ).scalar() or 0

    # If no schedule capacities exist, assume all scheduled trains are active
    if trains_active_today == 0:
        trains_active_today = trains_scheduled_today

    avg_utilization = "75%"
    active_routes = db.query(func.count(TrainRoute.route_id)).scalar() or 0

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
    """Get daily ticket sales for the last N days"""
    dates = [(date.today() - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]
    tickets = []

    for d in dates:
        count = db.query(func.count(Ticket.ticket_id)).filter(
            Ticket.issue_date == d
        ).scalar() or 0
        tickets.append(count)

    return DailyTicketSales(dates=dates, tickets=tickets)

@app.get("/analytics/schedule-status-today", response_model=ScheduleStatusToday)
async def get_schedule_status_today(db: Session = Depends(get_db)):
    """Get completed vs pending train schedules for today"""
    today = date.today()
    day_name = today.strftime("%A").lower()

    # Get all schedules that should run today
    if not hasattr(TrainSchedule, day_name):
        return ScheduleStatusToday(completed=0, pending=0)

    day_column = getattr(TrainSchedule, day_name)

    total_scheduled = db.query(func.count(TrainSchedule.train_schedule_id)).filter(
        and_(
            day_column == True,
            TrainSchedule.status == ScheduleStatus.Active
        )
    ).scalar() or 0

    # Count completed schedules (those with schedule capacity entries for today with assigned trains)
    completed = db.query(func.count(ScheduleCapacity.id)).filter(
        and_(
            ScheduleCapacity.schedule_date == today,
            ScheduleCapacity.train_id.isnot(None)
        )
    ).scalar() or 0

    # Pending = total scheduled - completed
    pending = max(0, total_scheduled - completed)

    return ScheduleStatusToday(completed=completed, pending=pending)

@app.get("/analytics/class-distribution-today", response_model=ClassDistributionToday)
async def get_class_distribution_today(db: Session = Depends(get_db)):
    """Get ticket class distribution for today"""
    today = date.today()

    # Updated to use new enum values
    first_class = db.query(func.count(Ticket.ticket_id)).filter(
        and_(
            Ticket.issue_date == today,
            Ticket.class_ == TrainClass.First
        )
    ).scalar() or 0

    second_class = db.query(func.count(Ticket.ticket_id)).filter(
        and_(
            Ticket.issue_date == today,
            Ticket.class_ == TrainClass.Second
        )
    ).scalar() or 0

    third_class = db.query(func.count(Ticket.ticket_id)).filter(
        and_(
            Ticket.issue_date == today,
            Ticket.class_ == TrainClass.Third
        )
    ).scalar() or 0

    return ClassDistributionToday(
        first_class=first_class,
        second_class=second_class,
        third_class=third_class
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
