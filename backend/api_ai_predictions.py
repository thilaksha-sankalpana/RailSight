"""
FastAPI endpoints for AI-powered compartment prediction
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel

from backend.db import get_db_session
from backend.models import TrainSchedule
from backend.services.ai_prediction_engine import CompartmentPredictionEngine
from backend.services.ollama_service import get_ollama_service
from backend.ai_models import CompartmentPrediction, PredictionLog

router = APIRouter(prefix="/api/ai", tags=["AI Predictions"])


# =====================================================
# REQUEST MODELS
# =====================================================

class SimplePredictionRequest(BaseModel):
    schedule_id: str
    prediction_date: str  # Format: YYYY-MM-DD


# =====================================================
# RESPONSE MODELS
# =====================================================

class PredictionResponse(BaseModel):
    success: bool
    prediction_id: Optional[int] = None
    schedule_id: str
    schedule_date: str
    predicted_first_class: int
    predicted_second_class: int
    predicted_third_class: int
    total_compartments: int
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None
    execution_time_ms: Optional[int] = None

class OllamaStatusResponse(BaseModel):
    is_running: bool
    models: List[str]
    current_model: str

class PredictionListResponse(BaseModel):
    predictions: List[dict]
    total: int


# =====================================================
# ENDPOINTS
# =====================================================

@router.get("/health", response_model=OllamaStatusResponse)
def check_ollama_health(db: Session = Depends(get_db_session)):
    """
    Check if Ollama service is running and list available models
    """
    ollama = get_ollama_service()
    is_running = ollama.check_health()
    models = ollama.list_models() if is_running else []
    
    return OllamaStatusResponse(
        is_running=is_running,
        models=models,
        current_model=ollama.model
    )


@router.post("/predict-simple", response_model=PredictionResponse)
def generate_prediction_simple(
    request: SimplePredictionRequest = Body(...),
    db: Session = Depends(get_db_session)
):
    """
    Generate AI-powered compartment prediction for a schedule (simplified endpoint)
    
    **Example:**
    ```
    POST /api/ai/predict-simple
    {
        "schedule_id": "SCH001",
        "prediction_date": "2025-11-20"
    }
    ```
    """
    try:
        # Parse date
        prediction_date = datetime.strptime(request.prediction_date, "%Y-%m-%d").date()
        
        # Get schedule to extract route_id
        schedule = db.query(TrainSchedule).filter(
            TrainSchedule.train_schedule_id == request.schedule_id
        ).first()
        
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail=f"Schedule {request.schedule_id} not found"
            )
        
        route_id = schedule.route_id
        
        # Use placeholder train_id since we don't track individual trains in schedules
        # The RAG system will look up historical data by schedule_id anyway
        train_id = "DEFAULT"
        
        # Check if Ollama is running
        ollama = get_ollama_service()
        if not ollama.check_health():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not running. Please start Ollama first."
            )
        
        # Generate prediction
        engine = CompartmentPredictionEngine(db)
        result = engine.predict(
            schedule_id=request.schedule_id,
            route_id=route_id,
            train_id=train_id,
            target_date=prediction_date,
            save_to_db=True
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {result.get('message', 'Unknown error')}"
            )
        
        pred = result["prediction"]
        
        return PredictionResponse(
            success=True,
            prediction_id=pred.get("prediction_id"),
            schedule_id=request.schedule_id,
            schedule_date=request.prediction_date,
            predicted_first_class=pred["predicted_first_class"],
            predicted_second_class=pred["predicted_second_class"],
            predicted_third_class=pred["predicted_third_class"],
            total_compartments=pred["predicted_first_class"] + pred["predicted_second_class"] + pred["predicted_third_class"],
            confidence_score=pred.get("confidence_score"),
            reasoning=pred.get("reasoning"),
            execution_time_ms=result.get("execution_time_ms")
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict", response_model=PredictionResponse)
def generate_prediction(
    schedule_id: str,
    route_id: str,
    train_id: str,
    target_date: str,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db_session)
):
    """
    Generate AI-powered compartment prediction for a schedule
    
    **Example:**
    ```
    POST /api/ai/predict
    {
        "schedule_id": "SCH001",
        "route_id": "R01",
        "train_id": "T001",
        "target_date": "2025-11-20"
    }
    ```
    """
    try:
        # Parse date
        prediction_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        
        # Check if Ollama is running
        ollama = get_ollama_service()
        if not ollama.check_health():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not running. Please start Ollama first."
            )
        
        # Generate prediction
        engine = CompartmentPredictionEngine(db)
        result = engine.predict(
            schedule_id=schedule_id,
            route_id=route_id,
            train_id=train_id,
            target_date=prediction_date,
            save_to_db=True
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {result.get('message', 'Unknown error')}"
            )
        
        pred = result["prediction"]
        
        return PredictionResponse(
            success=True,
            prediction_id=pred.get("prediction_id"),
            schedule_id=schedule_id,
            schedule_date=target_date,
            predicted_first_class=pred["predicted_first_class"],
            predicted_second_class=pred["predicted_second_class"],
            predicted_third_class=pred["predicted_third_class"],
            total_compartments=pred["predicted_first_class"] + pred["predicted_second_class"] + pred["predicted_third_class"],
            confidence_score=pred.get("confidence_score"),
            reasoning=pred.get("reasoning"),
            execution_time_ms=result.get("execution_time_ms")
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{schedule_id}", response_model=PredictionListResponse)
def get_predictions_for_schedule(
    schedule_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db_session)
):
    """
    Get AI predictions for a schedule
    
    **Example:**
    ```
    GET /api/ai/predictions/SCH001?start_date=2025-11-01&end_date=2025-11-30
    ```
    """
    query = db.query(CompartmentPrediction).filter(
        CompartmentPrediction.schedule_id == schedule_id,
        CompartmentPrediction.is_active == 1
    )
    
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(CompartmentPrediction.schedule_date >= start)
    
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(CompartmentPrediction.schedule_date <= end)
    
    predictions = query.order_by(CompartmentPrediction.schedule_date.desc()).limit(limit).all()
    
    return PredictionListResponse(
        predictions=[
            {
                "id": p.id,
                "schedule_id": p.schedule_id,
                "schedule_date": str(p.schedule_date),
                "predicted_first_class": p.predicted_first_class,
                "predicted_second_class": p.predicted_second_class,
                "predicted_third_class": p.predicted_third_class,
                "total_compartments": p.total_compartments,
                "confidence_score": p.confidence_score,
                "reasoning": p.reasoning,
                "expected_total_passengers": p.expected_total_passengers,
                "predicted_at": str(p.predicted_at)
            }
            for p in predictions
        ],
        total=len(predictions)
    )


@router.get("/prediction/{prediction_id}")
def get_prediction_detail(
    prediction_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Get detailed information about a specific prediction
    """
    prediction = db.query(CompartmentPrediction).filter(
        CompartmentPrediction.id == prediction_id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return {
        "id": prediction.id,
        "schedule_id": prediction.schedule_id,
        "schedule_date": str(prediction.schedule_date),
        "route_id": prediction.route_id,
        "predicted_allocation": {
            "first_class": prediction.predicted_first_class,
            "second_class": prediction.predicted_second_class,
            "third_class": prediction.predicted_third_class,
            "total": prediction.total_compartments
        },
        "predicted_capacity": {
            "first_class": prediction.predicted_first_class_capacity,
            "second_class": prediction.predicted_second_class_capacity,
            "third_class": prediction.predicted_third_class_capacity,
            "total": prediction.total_predicted_capacity
        },
        "expected_demand": {
            "total_passengers": prediction.expected_total_passengers,
            "first_class": prediction.expected_first_class_demand,
            "second_class": prediction.expected_second_class_demand,
            "third_class": prediction.expected_third_class_demand
        },
        "model_info": {
            "name": prediction.model_name,
            "confidence_score": prediction.confidence_score
        },
        "reasoning": prediction.reasoning,
        "factors_considered": prediction.factors_considered,
        "historical_context": prediction.historical_context,
        "actual_allocation": {
            "first_class": prediction.actual_first_class,
            "second_class": prediction.actual_second_class,
            "third_class": prediction.actual_third_class,
            "accuracy": prediction.prediction_accuracy
        } if prediction.actual_first_class else None,
        "predicted_at": str(prediction.predicted_at),
        "is_active": bool(prediction.is_active)
    }


@router.post("/predict-batch")
def generate_batch_predictions(
    schedule_ids: List[str],
    route_ids: List[str],
    train_ids: List[str],
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db_session)
):
    """
    Generate predictions for multiple schedules over a date range
    
    **Example:**
    ```
    POST /api/ai/predict-batch
    {
        "schedule_ids": ["SCH001", "SCH002"],
        "route_ids": ["R01", "R01"],
        "train_ids": ["T001", "T002"],
        "start_date": "2025-11-20",
        "end_date": "2025-11-25"
    }
    ```
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        if len(schedule_ids) != len(route_ids) or len(schedule_ids) != len(train_ids):
            raise HTTPException(
                status_code=400,
                detail="schedule_ids, route_ids, and train_ids must have the same length"
            )
        
        # Check Ollama
        ollama = get_ollama_service()
        if not ollama.check_health():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not running"
            )
        
        engine = CompartmentPredictionEngine(db)
        results = []
        
        # Generate date range
        current_date = start
        while current_date <= end:
            for schedule_id, route_id, train_id in zip(schedule_ids, route_ids, train_ids):
                result = engine.predict(
                    schedule_id=schedule_id,
                    route_id=route_id,
                    train_id=train_id,
                    target_date=current_date,
                    save_to_db=True
                )
                results.append({
                    "schedule_id": schedule_id,
                    "date": str(current_date),
                    "success": result["success"],
                    "prediction_id": result.get("prediction", {}).get("prediction_id") if result["success"] else None
                })
            
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "total_predictions": len(results),
            "results": results
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
def get_prediction_logs(
    schedule_id: Optional[str] = None,
    success_only: bool = False,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db_session)
):
    """
    Get prediction logs for debugging and monitoring
    """
    query = db.query(PredictionLog)
    
    if schedule_id:
        query = query.filter(PredictionLog.schedule_id == schedule_id)
    
    if success_only:
        query = query.filter(PredictionLog.success == 1)
    
    logs = query.order_by(PredictionLog.created_at.desc()).limit(limit).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "schedule_id": log.schedule_id,
                "schedule_date": str(log.schedule_date) if log.schedule_date else None,
                "success": bool(log.success),
                "error_message": log.error_message,
                "execution_time_ms": log.execution_time_ms,
                "model_name": log.model_name,
                "created_at": str(log.created_at)
            }
            for log in logs
        ],
        "total": len(logs)
    }
