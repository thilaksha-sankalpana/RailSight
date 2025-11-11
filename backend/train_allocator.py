# backend/train_allocator.py
"""
Intelligent Train Allocation System - Version 2.0
Updated for revised database schema (2025-11-10)

Automatically assigns trains to daily schedules with conflict prevention and optimization
"""
from datetime import datetime, time, timedelta, date
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

logger = logging.getLogger(__name__)

class TrainAllocationOptimizer:
    """
    Optimizes train allocation across schedules
    - Prevents conflicts (same train on overlapping schedules)
    - Enforces 20-minute buffer between assignments
    - Maximizes train utilization through smart sequencing
    - Respects route-model compatibility
    """

    BUFFER_MINUTES = 20

    def __init__(self, db: Session):
        self.db = db

    def allocate_trains_for_date(self, target_date: date) -> Dict[str, any]:
        """
        Main entry point: Allocate trains for all schedules on a given date

        Returns:
            Dict with allocation results and statistics
        """
        from backend.models import (
            TrainSchedule, DailySchedule, OperationalTrain,
            TrainModel, TrainRoute, ScheduleStatus, TrainStatus
        )

        logger.info(f"Starting train allocation for {target_date}")

        # Get active schedules for this date
        day_name = target_date.strftime("%A").lower()
        day_column = getattr(TrainSchedule, day_name)

        schedules = self.db.query(TrainSchedule).filter(
            TrainSchedule.status == ScheduleStatus.Active,
            day_column == True
        ).order_by(TrainSchedule.origin_departure).all()

        if not schedules:
            logger.warning(f"No active schedules found for {target_date}")
            return {"success": False, "message": "No schedules for this date"}

        logger.info(f"Found {len(schedules)} active schedules")

        # Build schedule requirements
        schedule_requirements = []
        for schedule in schedules:
            route = self.db.query(TrainRoute).filter(
                TrainRoute.route_id == schedule.route_id
            ).first()

            if not route:
                logger.warning(f"Route {schedule.route_id} not found for schedule {schedule.train_schedule_id}")
                continue

            schedule_requirements.append({
                "schedule_id": schedule.train_schedule_id,
                "route_id": schedule.route_id,
                "origin_station_id": schedule.origin_station_id,
                "origin": schedule.origin_station,
                "destination_station_id": schedule.destination_station_id,
                "destination": schedule.destination_station,
                "departure_time": schedule.origin_departure,
                "arrival_time": schedule.destination_departure,
                "route_info": route.route_name
            })

        # Get available trains
        available_trains = self.db.query(OperationalTrain).filter(
            OperationalTrain.status == TrainStatus.Active
        ).all()

        if not available_trains:
            logger.error("No active trains available")
            return {"success": False, "message": "No trains available"}

        logger.info(f"Found {len(available_trains)} available trains")

        # Perform allocation
        allocations = self._optimize_allocations(
            schedule_requirements,
            available_trains,
            target_date
        )

        # Save allocations to database
        saved_count = 0
        for allocation in allocations:
            # Calculate total capacity
            total_capacity = (
                allocation.get("first_class", 0) * allocation.get("seating_per_first", 0) +
                allocation.get("second_class", 0) * (allocation.get("seating_per_second", 0) + allocation.get("standing_per_second", 0)) +
                allocation.get("third_class", 0) * (allocation.get("seating_per_third", 0) + allocation.get("standing_per_third", 0))
            )

            # Ensure at least 1 passenger capacity
            total_capacity = max(1, total_capacity)

            daily_schedule = DailySchedule(
                date=target_date,
                schedule_id=allocation["schedule_id"],
                origin_station_id=allocation["origin_station_id"],
                origin_departure=allocation["departure_time"],
                destination_station_id=allocation["destination_station_id"],
                destination_departure=allocation["arrival_time"],
                train_id=allocation["train_id"],

                # First Class
                first_class_compartments=allocation.get("first_class", 0),
                seating_passengers_per_first_class=allocation.get("seating_per_first", 0),
                total_passengers_per_first_class=allocation.get("seating_per_first", 0),

                # Second Class
                second_class_compartments=allocation.get("second_class", 0),
                seating_passengers_per_second_class=allocation.get("seating_per_second", 0),
                standing_passengers_per_second_class=allocation.get("standing_per_second", 0),
                total_passengers_per_second_class=(
                    allocation.get("seating_per_second", 0) + allocation.get("standing_per_second", 0)
                ),

                # Third Class
                third_class_compartments=allocation.get("third_class", 0),
                seating_passengers_per_third_class=allocation.get("seating_per_third", 0),
                standing_passengers_per_third_class=allocation.get("standing_per_third", 0),
                total_passengers_per_third_class=(
                    allocation.get("seating_per_third", 0) + allocation.get("standing_per_third", 0)
                ),

                # Total
                total_passengers_per_train=total_capacity
            )

            # Check if already exists
            existing = self.db.query(DailySchedule).filter(
                and_(
                    DailySchedule.date == target_date,
                    DailySchedule.schedule_id == allocation["schedule_id"]
                )
            ).first()

            if existing:
                # Update existing
                existing.train_id = allocation["train_id"]
                existing.first_class_compartments = allocation.get("first_class", 0)
                existing.second_class_compartments = allocation.get("second_class", 0)
                existing.third_class_compartments = allocation.get("third_class", 0)
                existing.total_passengers_per_train = total_capacity
            else:
                self.db.add(daily_schedule)

            saved_count += 1

        self.db.commit()

        logger.info(f"Successfully allocated {saved_count} schedules")

        return {
            "success": True,
            "date": str(target_date),
            "schedules_allocated": saved_count,
            "trains_used": len(set(a["train_id"] for a in allocations)),
            "allocations": allocations
        }

    def _optimize_allocations(
        self,
        schedule_requirements: List[Dict],
        available_trains: List,
        target_date: date
    ) -> List[Dict]:
        """
        Core allocation algorithm with conflict prevention
        """
        from backend.models import TrainModel

        allocations = []
        train_schedule_map = {}  # train_id -> list of (departure, arrival) tuples

        for req in schedule_requirements:
            schedule_id = req["schedule_id"]
            route_id = req["route_id"]
            departure = req["departure_time"]
            arrival = req["arrival_time"]

            # Find compatible trains for this route
            compatible_trains = []
            for train in available_trains:
                model = self.db.query(TrainModel).filter(
                    TrainModel.model_id == train.model_id
                ).first()

                if model and self._is_route_compatible(route_id, model.assigned_routes):
                    compatible_trains.append(train)

            if not compatible_trains:
                logger.warning(f"No compatible trains for schedule {schedule_id}")
                # Use all trains as fallback
                compatible_trains = available_trains

            # Find best train (minimizing idle time, respecting conflicts)
            best_train = None
            min_idle_time = float('inf')

            for train in compatible_trains:
                if train.train_id not in train_schedule_map:
                    train_schedule_map[train.train_id] = []

                # Check for conflicts
                if self._has_conflict(train.train_id, departure, arrival, train_schedule_map):
                    continue

                # Calculate idle time (time since last assignment)
                idle_time = self._calculate_idle_time(
                    train.train_id, departure, train_schedule_map
                )

                if idle_time < min_idle_time:
                    min_idle_time = idle_time
                    best_train = train

            if best_train:
                # Allocate this train
                train_schedule_map[best_train.train_id].append((departure, arrival))

                # Get train model for capacity info
                model = self.db.query(TrainModel).filter(
                    TrainModel.model_id == best_train.model_id
                ).first()

                # Predict compartment distribution
                compartments = self._predict_compartments(
                    schedule_id, route_id, target_date, best_train
                )

                # Get capacity per compartment from model
                seating_per_comp = model.seating_passengers_per_compartment if model else 50
                standing_per_comp = model.standing_passengers_per_compartment if model else 30

                allocations.append({
                    "schedule_id": schedule_id,
                    "train_id": best_train.train_id,
                    "origin_station_id": req["origin_station_id"],
                    "origin": req["origin"],
                    "destination_station_id": req["destination_station_id"],
                    "destination": req["destination"],
                    "departure_time": departure,
                    "arrival_time": arrival,
                    "first_class": compartments["first"],
                    "second_class": compartments["second"],
                    "third_class": compartments["third"],
                    "seating_per_first": seating_per_comp,
                    "seating_per_second": seating_per_comp,
                    "standing_per_second": standing_per_comp,
                    "seating_per_third": seating_per_comp,
                    "standing_per_third": standing_per_comp
                })

                logger.info(f"Allocated train {best_train.train_id} to schedule {schedule_id}")
            else:
                logger.warning(f"Could not allocate train for schedule {schedule_id}")

        return allocations

    def _has_conflict(
        self,
        train_id: str,
        new_departure: time,
        new_arrival: time,
        schedule_map: Dict
    ) -> bool:
        """
        Check if assigning this train creates a time conflict
        Includes 20-minute buffer
        """
        if train_id not in schedule_map:
            return False

        new_dep_mins = new_departure.hour * 60 + new_departure.minute
        new_arr_mins = new_arrival.hour * 60 + new_arrival.minute

        for existing_dep, existing_arr in schedule_map[train_id]:
            exist_dep_mins = existing_dep.hour * 60 + existing_dep.minute
            exist_arr_mins = existing_arr.hour * 60 + existing_arr.minute

            # Check for overlap with buffer
            if not (new_arr_mins + self.BUFFER_MINUTES <= exist_dep_mins or
                    new_dep_mins >= exist_arr_mins + self.BUFFER_MINUTES):
                return True

        return False

    def _calculate_idle_time(
        self,
        train_id: str,
        new_departure: time,
        schedule_map: Dict
    ) -> float:
        """
        Calculate idle time before this assignment (lower is better for efficiency)
        """
        if train_id not in schedule_map or not schedule_map[train_id]:
            return 0.0  # First assignment

        # Find most recent assignment
        last_arrival = max(schedule_map[train_id], key=lambda x: x[1])[1]

        last_mins = last_arrival.hour * 60 + last_arrival.minute
        new_mins = new_departure.hour * 60 + new_departure.minute

        idle = new_mins - (last_mins + self.BUFFER_MINUTES)
        return max(0.0, idle)

    def _is_route_compatible(self, route_id: str, assigned_routes: Optional[str]) -> bool:
        """
        Check if train model is suitable for this route
        """
        if not assigned_routes:
            return True  # No restrictions

        # Parse assigned_routes (comma-separated or contains route_id)
        return route_id in assigned_routes or "all" in assigned_routes.lower()

    def _predict_compartments(
        self,
        schedule_id: str,
        route_id: str,
        target_date: date,
        train
    ) -> Dict[str, int]:
        """
        Predict compartment class distribution
        Uses simplified heuristic based on route classification
        """
        from backend.models import TrainRoute

        route = self.db.query(TrainRoute).filter(
            TrainRoute.route_id == route_id
        ).first()

        total_compartments = train.compartments_per_unit

        if not route:
            # Default distribution
            return {"first": 1, "second": 2, "third": max(1, total_compartments - 3)}

        # Classify route by analyzing description
        route_desc = route.route.lower() if route.route else ""
        route_name = route.route_name.lower() if route.route_name else ""
        combined = f"{route_name} {route_desc}"

        # Route type classification based on keywords
        if any(kw in combined for kw in ['commuter', 'kelani', 'panadura']):
            route_type = "suburban"
        elif any(kw in combined for kw in ['express', 'intercity', 'menike']):
            route_type = "intercity"
        elif any(kw in combined for kw in ['colombo', 'badulla', 'trincomalee', 'matara']):
            route_type = "long_distance"
        else:
            route_type = "regional"

        # Default distributions by route type
        distributions = {
            "suburban": {"first": 0, "second": 1, "third": total_compartments - 1},
            "regional": {"first": 0, "second": 2, "third": total_compartments - 2},
            "intercity": {"first": 1, "second": 2, "third": total_compartments - 3},
            "long_distance": {"first": 1, "second": 3, "third": total_compartments - 4}
        }

        distribution = distributions.get(route_type, distributions["regional"])

        # Ensure at least one compartment of each type for intercity+
        if route_type in ["intercity", "long_distance"]:
            if distribution["first"] < 1:
                distribution["first"] = 1
                distribution["third"] -= 1

        # Ensure third class always has at least 1
        distribution["third"] = max(1, distribution["third"])

        # Ensure total equals train compartments
        total = distribution["first"] + distribution["second"] + distribution["third"]
        if total != total_compartments:
            diff = total_compartments - total
            distribution["third"] += diff
            distribution["third"] = max(1, distribution["third"])

        return distribution


def allocate_trains_for_week(db: Session, start_date: date) -> Dict:
    """
    Convenience function to allocate trains for a full week

    Args:
        db: Database session
        start_date: Starting date of the week

    Returns:
        Dict with weekly allocation results
    """
    allocator = TrainAllocationOptimizer(db)
    results = []

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        result = allocator.allocate_trains_for_date(current_date)
        results.append(result)

    return {
        "success": all(r["success"] for r in results),
        "week_start": str(start_date),
        "daily_results": results,
        "total_allocations": sum(r.get("schedules_allocated", 0) for r in results)
    }
