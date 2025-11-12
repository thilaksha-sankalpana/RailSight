"""
RAG Data Retrieval Service
Queries historical data and formats it for LLM context
This is the "Retrieval" part of RAG (Retrieval-Augmented Generation)
"""
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from backend.models import (
    PassengerDemandHistory,
    TrainSchedule,
    TrainRoute,
    Ticket,
    ScheduleCapacity,
    SegmentCapacity,
    TrainStationTicketPrice,
    OperationalTrain,
    TrainModel
)

logger = logging.getLogger(__name__)


class RAGDataRetrieval:
    """
    Retrieves and formats historical data for RAG-based predictions
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_historical_demand(
        self,
        schedule_id: str,
        target_date: date,
        lookback_days: int = 90
    ) -> Dict[str, Any]:
        """
        Get historical passenger demand for this schedule
        
        Args:
            schedule_id: Train schedule ID
            target_date: Date to predict for
            lookback_days: How many days back to look
        
        Returns:
            Dict with demand statistics
        """
        start_date = target_date - timedelta(days=lookback_days)
        
        history = self.db.query(PassengerDemandHistory).filter(
            and_(
                PassengerDemandHistory.schedule_id == schedule_id,
                PassengerDemandHistory.date >= start_date,
                PassengerDemandHistory.date < target_date
            )
        ).order_by(desc(PassengerDemandHistory.date)).all()
        
        if not history:
            return {"error": "No historical data found"}
        
        # Calculate statistics
        total_records = len(history)
        avg_passengers = sum(h.total_passengers for h in history) / total_records
        avg_load_factor = sum(float(h.load_factor or 0) for h in history) / total_records
        
        # Class distribution
        avg_first = sum(h.first_class_passengers or 0 for h in history) / total_records
        avg_second = sum(h.second_class_passengers or 0 for h in history) / total_records
        avg_third = sum(h.third_class_passengers or 0 for h in history) / total_records
        
        # Recent trend (last 30 days)
        recent_history = [h for h in history if h.date >= target_date - timedelta(days=30)]
        recent_avg = sum(h.total_passengers for h in recent_history) / len(recent_history) if recent_history else avg_passengers
        
        return {
            "total_records": total_records,
            "date_range": f"{start_date} to {target_date}",
            "avg_total_passengers": round(avg_passengers, 1),
            "avg_load_factor": round(avg_load_factor, 1),
            "avg_first_class": round(avg_first, 1),
            "avg_second_class": round(avg_second, 1),
            "avg_third_class": round(avg_third, 1),
            "recent_trend": "increasing" if recent_avg > avg_passengers else "decreasing",
            "recent_avg_passengers": round(recent_avg, 1),
            "peak_passengers": max(h.total_passengers for h in history),
            "min_passengers": min(h.total_passengers for h in history)
        }
    
    def get_similar_dates(
        self,
        schedule_id: str,
        target_date: date,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical dates (same day of week, month)
        
        Args:
            schedule_id: Train schedule ID
            target_date: Date to predict for
            limit: Number of similar dates to return
        
        Returns:
            List of similar date records
        """
        # Get same day of week from past year
        day_of_week = target_date.weekday()
        month = target_date.month
        
        one_year_ago = target_date - timedelta(days=365)
        
        similar_dates = self.db.query(PassengerDemandHistory).filter(
            and_(
                PassengerDemandHistory.schedule_id == schedule_id,
                PassengerDemandHistory.date >= one_year_ago,
                PassengerDemandHistory.date < target_date,
                func.extract('dow', PassengerDemandHistory.date) == day_of_week,
                func.extract('month', PassengerDemandHistory.date) == month
            )
        ).order_by(desc(PassengerDemandHistory.date)).limit(limit).all()
        
        return [
            {
                "date": str(d.date),
                "total_passengers": d.total_passengers,
                "load_factor": float(d.load_factor) if d.load_factor else None,
                "first_class": d.first_class_passengers or 0,
                "second_class": d.second_class_passengers or 0,
                "third_class": d.third_class_passengers or 0
            }
            for d in similar_dates
        ]
    
    def get_route_characteristics(self, route_id: str) -> Dict[str, Any]:
        """
        Get route characteristics (distance, type, stations)
        
        Args:
            route_id: Route ID
        
        Returns:
            Dict with route info
        """
        route = self.db.query(TrainRoute).filter(TrainRoute.route_id == route_id).first()
        
        if not route:
            return {"error": "Route not found"}
        
        # Count stations in route
        station_count = route.route.count("->") + 1 if route.route else 0
        
        # Classify route type based on description
        route_desc = route.route_name.lower()
        if any(word in route_desc for word in ["express", "intercity"]):
            route_type = "intercity"
        elif any(word in route_desc for word in ["commuter", "suburban"]):
            route_type = "suburban"
        else:
            route_type = "regional"
        
        return {
            "route_id": route.route_id,
            "route_name": route.route_name,
            "route_description": route.route,
            "station_count": station_count,
            "route_type": route_type
        }
    
    def get_pricing_info(
        self,
        schedule_id: str
    ) -> Dict[str, Any]:
        """
        Get pricing information for the schedule
        
        Args:
            schedule_id: Train schedule ID
        
        Returns:
            Dict with pricing info
        """
        schedule = self.db.query(TrainSchedule).filter(
            TrainSchedule.train_schedule_id == schedule_id
        ).first()
        
        if not schedule:
            return {"error": "Schedule not found"}
        
        # Get origin-destination pricing
        pricing = self.db.query(TrainStationTicketPrice).filter(
            and_(
                TrainStationTicketPrice.origin_station_id == schedule.origin_station_id,
                TrainStationTicketPrice.destination_station_id == schedule.destination_station_id,
                TrainStationTicketPrice.effective_to.is_(None)
            )
        ).first()
        
        if not pricing:
            return {"error": "No pricing found"}
        
        return {
            "origin": schedule.origin_station,
            "destination": schedule.destination_station,
            "first_class_fee": float(pricing.first_class_fee) if pricing.first_class_fee else 0,
            "second_class_fee": float(pricing.second_class_fee) if pricing.second_class_fee else 0,
            "third_class_fee": float(pricing.third_class_fee) if pricing.third_class_fee else 0,
            "distance_km": float(pricing.distance) if pricing.distance else 0
        }
    
    def get_train_model_info(self, train_id: str) -> Dict[str, Any]:
        """
        Get train model specifications
        
        Args:
            train_id: Operational train ID
        
        Returns:
            Dict with train model info
        """
        train = self.db.query(OperationalTrain).filter(
            OperationalTrain.train_id == train_id
        ).first()
        
        if not train:
            return {"error": "Train not found"}
        
        model = self.db.query(TrainModel).filter(
            TrainModel.model_id == train.model_id
        ).first()
        
        if not model:
            return {"error": "Model not found"}
        
        return {
            "train_id": train.train_id,
            "model_name": model.model_name,
            "model_type": model.model_type,
            "total_compartments": train.compartments_per_unit,
            "seats_per_compartment": model.seating_passengers_per_compartment,
            "standing_per_compartment": model.standing_passengers_per_compartment,
            "total_capacity_per_compartment": model.total_passengers_per_compartment
        }
    
    def get_schedule_info(self, schedule_id: str) -> Dict[str, Any]:
        """
        Get schedule details
        
        Args:
            schedule_id: Train schedule ID
        
        Returns:
            Dict with schedule info
        """
        schedule = self.db.query(TrainSchedule).filter(
            TrainSchedule.train_schedule_id == schedule_id
        ).first()
        
        if not schedule:
            return {"error": "Schedule not found"}
        
        return {
            "schedule_id": schedule.train_schedule_id,
            "schedule_name": schedule.train_schedule,
            "route_id": schedule.route_id,
            "origin": schedule.origin_station,
            "destination": schedule.destination_station,
            "departure_time": str(schedule.origin_departure),
            "arrival_time": str(schedule.destination_departure),
            "operates_on": {
                "monday": schedule.monday,
                "tuesday": schedule.tuesday,
                "wednesday": schedule.wednesday,
                "thursday": schedule.thursday,
                "friday": schedule.friday,
                "saturday": schedule.saturday,
                "sunday": schedule.sunday,
                "poya_day": schedule.poya_day,
                "holiday": schedule.holiday
            }
        }
    
    def get_complete_context(
        self,
        schedule_id: str,
        route_id: str,
        train_id: str,
        target_date: date
    ) -> Dict[str, Any]:
        """
        Get all relevant context for prediction
        This is the main method used by the prediction engine
        
        Args:
            schedule_id: Train schedule ID
            route_id: Route ID
            train_id: Operational train ID
            target_date: Date to predict for
        
        Returns:
            Dict with all context data
        """
        logger.info(f"📊 Retrieving complete context for {schedule_id} on {target_date}")
        
        context = {
            "target_date": str(target_date),
            "day_of_week": target_date.strftime("%A"),
            "schedule": self.get_schedule_info(schedule_id),
            "route": self.get_route_characteristics(route_id),
            "train_model": self.get_train_model_info(train_id),
            "pricing": self.get_pricing_info(schedule_id),
            "historical_demand": self.get_historical_demand(schedule_id, target_date),
            "similar_dates": self.get_similar_dates(schedule_id, target_date)
        }
        
        logger.info(f"✅ Context retrieved successfully")
        return context
