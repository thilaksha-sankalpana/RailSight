# backend/compartment_predictor.py
"""
Compartment Class Allocation Predictor - Version 2.0
Updated for revised database schema (2025-11-10)

Forecasts optimal 1st/2nd/3rd class distribution based on:
- Route characteristics
- Historical demand
- Pricing dynamics
- Train model specifications
"""
from datetime import date, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import math

class CompartmentClassPredictor:
    """
    Predicts optimal compartment class distribution for train schedules
    """

    def __init__(self, db: Session):
        self.db = db

    def predict_distribution(
        self,
        schedule_id: str,
        route_id: str,
        train_id: str,
        target_date: date
    ) -> Dict[str, int]:
        """
        Main prediction method

        Returns:
            Dict with keys: first, second, third (compartment counts)
        """
        from backend.models import (
            TrainRoute, OperationalTrain, TrainModel,
            PassengerDemandHistory, TrainStationTicketPrice
        )

        # Get train details (updated model name)
        train = self.db.query(OperationalTrain).filter(
            OperationalTrain.train_id == train_id
        ).first()

        if not train:
            return {"first": 1, "second": 2, "third": 5}

        model = self.db.query(TrainModel).filter(
            TrainModel.model_id == train.model_id
        ).first()

        if not model:
            return {"first": 1, "second": 2, "third": train.compartments_per_unit - 3}

        # Updated field name
        total_compartments = train.compartments_per_unit

        # Get route information
        route = self.db.query(TrainRoute).filter(
            TrainRoute.route_id == route_id
        ).first()

        if not route:
            return self._default_distribution(total_compartments, "regional")

        # Step 1: Determine route type (using route description)
        route_type = self._classify_route(route)

        # Step 2: Get base configuration
        base_config = self._get_base_config(model.model_type, route_type, total_compartments)

        # Step 3: Analyze pricing dynamics
        pricing_weights = self._analyze_pricing(route_id)

        # Step 4: Check historical demand
        demand_adjustment = self._check_demand_history(schedule_id, target_date)

        # Step 5: Apply adjustments
        final_config = self._apply_adjustments(
            base_config,
            pricing_weights,
            demand_adjustment,
            total_compartments
        )

        # Step 6: Validate and normalize
        final_config = self._validate_distribution(final_config, total_compartments)

        return final_config

    def _classify_route(self, route) -> str:
        """
        Classify route by analyzing route description
        Since v2.0 schema doesn't have approx_distance_km, we estimate from route description
        """
        # Analyze route description for keywords
        route_desc = route.route.lower() if route.route else ""
        route_name = route.route_name.lower() if route.route_name else ""

        # Common long-distance routes
        long_distance_keywords = ['colombo', 'badulla', 'trincomalee', 'batticaloa', 'matara', 'beliatta']
        intercity_keywords = ['express', 'intercity', 'podi menike', 'udarata menike']
        suburban_keywords = ['commuter', 'kelani', 'puttalam', 'panadura']

        # Check route name and description
        combined = f"{route_name} {route_desc}"

        if any(keyword in combined for keyword in suburban_keywords):
            return "suburban"
        elif any(keyword in combined for keyword in intercity_keywords):
            return "intercity"
        elif any(keyword in combined for keyword in long_distance_keywords):
            return "long_distance"
        else:
            return "regional"

    def _get_base_config(self, model_type: str, route_type: str, total_compartments: int) -> Dict[str, int]:
        """
        Get base compartment configuration based on model and route
        """
        # Configuration matrix
        configs = {
            "suburban": {
                "default": {"first": 0, "second": 1, "third": total_compartments - 1}
            },
            "regional": {
                "default": {"first": 0, "second": 2, "third": total_compartments - 2}
            },
            "intercity": {
                "default": {"first": 1, "second": 2, "third": total_compartments - 3},
                "Express": {"first": 1, "second": 3, "third": total_compartments - 4}
            },
            "long_distance": {
                "default": {"first": 1, "second": 3, "third": total_compartments - 4},
                "Express": {"first": 2, "second": 3, "third": total_compartments - 5}
            }
        }

        route_configs = configs.get(route_type, configs["regional"])

        # Check if model type matches any specific config
        for key in route_configs:
            if key.lower() in model_type.lower():
                return route_configs[key].copy()

        return route_configs["default"].copy()

    def _analyze_pricing(self, route_id: str) -> Dict[str, float]:
        """
        Analyze ticket pricing to determine expected demand weights
        Updated for v2.0 schema (no train_route_id field)
        """
        from backend.models import TrainStationTicketPrice

        # Get average pricing for routes (sample from active prices)
        prices = self.db.query(TrainStationTicketPrice).filter(
            TrainStationTicketPrice.effective_to.is_(None)
        ).limit(10).all()

        if not prices:
            # Default weights (equal preference)
            return {"first": 0.2, "second": 0.3, "third": 0.5}

        # Calculate average prices
        first_prices = [float(p.first_class_fee) for p in prices if p.first_class_fee and p.first_class_fee > 0]
        second_prices = [float(p.second_class_fee) for p in prices if p.second_class_fee and p.second_class_fee > 0]
        third_prices = [float(p.third_class_fee) for p in prices if p.third_class_fee and p.third_class_fee > 0]

        # Use averages or defaults
        first_price = sum(first_prices) / len(first_prices) if first_prices else 500
        second_price = sum(second_prices) / len(second_prices) if second_prices else 300
        third_price = sum(third_prices) / len(third_prices) if third_prices else 150

        # Avoid division by zero
        first_price = max(first_price, 100)
        second_price = max(second_price, 50)
        third_price = max(third_price, 20)

        # Affordability (inverse of price, normalized)
        total_affordability = (1/first_price) + (1/second_price) + (1/third_price)

        weights = {
            "first": (1/first_price) / total_affordability,
            "second": (1/second_price) / total_affordability,
            "third": (1/third_price) / total_affordability
        }

        return weights

    def _check_demand_history(self, schedule_id: str, target_date: date) -> str:
        """
        Check historical demand to determine if adjustment needed
        Returns: 'high', 'low', or 'normal'
        """
        from backend.models import PassengerDemandHistory

        # Look back 30 days
        start_date = target_date - timedelta(days=30)

        history = self.db.query(PassengerDemandHistory).filter(
            and_(
                PassengerDemandHistory.schedule_id == schedule_id,
                PassengerDemandHistory.date >= start_date,
                PassengerDemandHistory.date < target_date
            )
        ).all()

        if not history:
            return "normal"

        # Calculate average load factor
        load_factors = [float(h.load_factor) for h in history if h.load_factor]

        if not load_factors:
            return "normal"

        avg_load = sum(load_factors) / len(load_factors)

        if avg_load >= 95:
            return "high"
        elif avg_load <= 70:
            return "low"
        else:
            return "normal"

    def _apply_adjustments(
        self,
        base_config: Dict[str, int],
        pricing_weights: Dict[str, float],
        demand_level: str,
        total_compartments: int
    ) -> Dict[str, int]:
        """
        Apply pricing and demand adjustments to base configuration
        """
        config = base_config.copy()

        # Demand-based adjustment
        if demand_level == "high":
            # Add capacity to most affordable class (typically 3rd)
            if config["third"] < total_compartments - 2:
                config["third"] += 1
                if config["second"] > 1:
                    config["second"] -= 1
                elif config["first"] > 0:
                    config["first"] -= 1

        elif demand_level == "low":
            # Reduce lowest value class, add to premium
            if config["third"] > 1:
                config["third"] -= 1
                if config["first"] < 2:
                    config["first"] += 1
                else:
                    config["second"] += 1

        # Pricing-based fine-tuning
        # If 3rd class is significantly more affordable, ensure adequate allocation
        if pricing_weights["third"] > 0.6 and config["third"] < total_compartments * 0.6:
            needed = math.ceil(total_compartments * 0.6) - config["third"]
            config["third"] += needed

            # Take from other classes
            if config["second"] > needed:
                config["second"] -= needed
            else:
                reduction = needed
                if config["second"] > 0:
                    reduction -= config["second"]
                    config["second"] = 0
                config["first"] = max(0, config["first"] - reduction)

        return config

    def _validate_distribution(self, config: Dict[str, int], total_compartments: int) -> Dict[str, int]:
        """
        Ensure distribution is valid and sums to total_compartments
        """
        # Ensure non-negative
        config["first"] = max(0, config["first"])
        config["second"] = max(0, config["second"])
        config["third"] = max(1, config["third"])  # Always at least 1 third class

        # Normalize to total_compartments
        current_total = config["first"] + config["second"] + config["third"]

        if current_total != total_compartments:
            diff = total_compartments - current_total

            if diff > 0:
                # Add to third class
                config["third"] += diff
            else:
                # Remove from third class (if possible)
                if config["third"] + diff >= 1:
                    config["third"] += diff
                else:
                    # Remove from second, then first
                    if config["second"] + diff >= 0:
                        config["second"] += diff
                    else:
                        config["first"] = max(0, config["first"] + diff)

        return config

    def _default_distribution(self, total_compartments: int, route_type: str = "regional") -> Dict[str, int]:
        """
        Return safe default distribution
        """
        if total_compartments < 3:
            return {"first": 0, "second": 0, "third": total_compartments}

        if route_type == "suburban":
            return {"first": 0, "second": 1, "third": total_compartments - 1}
        elif route_type == "intercity":
            return {"first": 1, "second": 2, "third": total_compartments - 3}
        else:  # regional or unknown
            return {"first": 0, "second": 2, "third": total_compartments - 2}


def predict_for_schedule(
    db: Session,
    schedule_id: str,
    route_id: str,
    train_id: str,
    target_date: date
) -> Dict[str, int]:
    """
    Convenience function for external use

    Args:
        db: Database session
        schedule_id: Train schedule ID
        route_id: Route ID
        train_id: Operational train ID
        target_date: Date to predict for

    Returns:
        Dict with first, second, third compartment counts
    """
    predictor = CompartmentClassPredictor(db)
    return predictor.predict_distribution(schedule_id, route_id, train_id, target_date)
