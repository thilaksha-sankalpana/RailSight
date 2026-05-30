"""
AI-Powered Compartment Prediction Engine
Combines RAG data retrieval with Ollama LLM to predict optimal compartment allocation
"""
import json
import logging
from datetime import date, datetime
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from backend.services.ollama_service import get_ollama_service
from backend.services.rag_data_service import RAGDataRetrieval
from backend.ai_models import CompartmentPrediction, PredictionLog

logger = logging.getLogger(__name__)


class CompartmentPredictionEngine:
    """
    Main prediction engine that uses RAG + LLM to predict compartment allocation
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ollama = get_ollama_service()
        self.rag_service = RAGDataRetrieval(db)
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that instructs the LLM on its role
        """
        return """You are an expert railway operations analyst specializing in train compartment allocation optimization.

Your task is to predict the optimal distribution of First Class, Second Class, and Third Class compartments for a train schedule based on historical data, passenger demand patterns, and operational constraints.

You must respond ONLY with a valid JSON object containing:
{
    "predicted_first_class": <integer>,
    "predicted_second_class": <integer>,
    "predicted_third_class": <integer>,
    "confidence_score": <float between 0.0 and 1.0>,
    "expected_total_passengers": <integer>,
    "expected_first_class_demand": <integer>,
    "expected_second_class_demand": <integer>,
    "expected_third_class_demand": <integer>,
    "reasoning": "<explanation of your prediction>",
    "factors_considered": ["<factor1>", "<factor2>", ...]
}

Key considerations:
1. Balance capacity with expected demand
2. Consider historical load factors and trends
3. Account for pricing (lower prices = higher demand)
4. Ensure at least 1 third-class compartment (most affordable)
5. Total compartments must match the train's physical capacity
6. Higher confidence when historical data is consistent"""
    
    def _build_user_prompt(self, context: Dict[str, Any], total_compartments: int) -> str:
        """
        Build the user prompt with all context data
        
        Args:
            context: Complete context from RAG retrieval
            total_compartments: Total compartments available on the train
        
        Returns:
            Formatted prompt string
        """
        schedule = context.get("schedule", {})
        route = context.get("route", {})
        train_model = context.get("train_model", {})
        pricing = context.get("pricing", {})
        demand = context.get("historical_demand", {})
        similar = context.get("similar_dates", [])
        
        prompt = f"""Predict the optimal compartment allocation for the following train schedule:

**SCHEDULE INFORMATION:**
- Schedule: {schedule.get('schedule_name', 'N/A')}
- Date: {context.get('target_date', 'N/A')} ({context.get('day_of_week', 'N/A')})
- Route: {schedule.get('origin', 'N/A')} → {schedule.get('destination', 'N/A')}
- Departure: {schedule.get('departure_time', 'N/A')}

**ROUTE CHARACTERISTICS:**
- Route Type: {route.get('route_type', 'N/A')}
- Number of Stations: {route.get('station_count', 'N/A')}
- Distance: {pricing.get('distance_km', 'N/A')} km

**TRAIN CAPACITY:**
- Total Compartments Available: {total_compartments}
- Seats per Compartment: {train_model.get('seats_per_compartment', 'N/A')}
- Standing per Compartment: {train_model.get('standing_per_compartment', 'N/A')}
- Total Capacity per Compartment: {train_model.get('total_capacity_per_compartment', 'N/A')}

**PRICING:**
- First Class: Rs. {pricing.get('first_class_fee', 0):.2f}
- Second Class: Rs. {pricing.get('second_class_fee', 0):.2f}
- Third Class: Rs. {pricing.get('third_class_fee', 0):.2f}

**HISTORICAL DEMAND (Last {demand.get('total_records', 0)} days):**
- Average Total Passengers: {demand.get('avg_total_passengers', 'N/A')}
- Average Load Factor: {demand.get('avg_load_factor', 'N/A')}%
- Class Distribution:
  * First Class: {demand.get('avg_first_class', 0):.1f} passengers
  * Second Class: {demand.get('avg_second_class', 0):.1f} passengers
  * Third Class: {demand.get('avg_third_class', 0):.1f} passengers
- Trend: {demand.get('recent_trend', 'N/A')}
- Peak Demand: {demand.get('peak_passengers', 'N/A')} passengers
- Minimum Demand: {demand.get('min_passengers', 'N/A')} passengers

**SIMILAR DATES (Same day of week):**
"""
        
        for i, sim in enumerate(similar[:3], 1):
            prompt += f"\n{i}. {sim.get('date')}: {sim.get('total_passengers')} passengers "
            prompt += f"(1st: {sim.get('first_class', 0)}, 2nd: {sim.get('second_class', 0)}, 3rd: {sim.get('third_class', 0)})"
            prompt += f" | Load Factor: {sim.get('load_factor', 'N/A')}%"
        
        prompt += f"""

**YOUR TASK:**
Based on this data, predict the optimal compartment allocation that will:
1. Maximize passenger satisfaction
2. Optimize revenue
3. Minimize overcrowding
4. Account for the affordability factor (third class is most popular)

Remember: Total compartments must equal {total_compartments}
"""
        
        return prompt
    
    def predict(
        self,
        schedule_id: str,
        route_id: str,
        train_id: str,
        target_date: date,
        save_to_db: bool = True,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate compartment prediction using RAG + LLM
        
        Args:
            schedule_id: Train schedule ID
            route_id: Route ID
            train_id: Operational train ID
            target_date: Date to predict for
            save_to_db: Whether to save prediction to database
            force_regenerate: If True, regenerate even if prediction exists
        
        Returns:
            Dict with prediction results
        """
        start_time = datetime.now()
        logger.info(f"🎯 Starting prediction for {schedule_id} on {target_date}")
        
        # Check if prediction already exists (unless forced to regenerate)
        if not force_regenerate:
            existing_prediction = self.db.query(CompartmentPrediction).filter(
                CompartmentPrediction.schedule_id == schedule_id,
                CompartmentPrediction.schedule_date == target_date,
                CompartmentPrediction.is_active == 1
            ).first()
            
            if existing_prediction:
                logger.info(f"✅ Prediction already exists (ID: {existing_prediction.id}). Returning cached prediction.")
                return {
                    "success": True,
                    "prediction": {
                        "prediction_id": existing_prediction.id,
                        "predicted_first_class": existing_prediction.predicted_first_class,
                        "predicted_second_class": existing_prediction.predicted_second_class,
                        "predicted_third_class": existing_prediction.predicted_third_class,
                        "expected_total_passengers": existing_prediction.expected_total_passengers,
                        "confidence_score": float(existing_prediction.confidence_score) if existing_prediction.confidence_score else None,
                        "reasoning": existing_prediction.reasoning
                    },
                    "execution_time_ms": 0,
                    "cached": True
                }
        
        try:
            # Step 1: Retrieve context using RAG
            logger.info("📊 Step 1: Retrieving context data...")
            context = self.rag_service.get_complete_context(
                schedule_id, route_id, train_id, target_date
            )
            
            train_info = context.get("train_model", {})
            total_compartments = train_info.get("total_compartments", 8)
            
            # Step 2: Build prompts
            logger.info("📝 Step 2: Building prompts...")
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(context, total_compartments)
            
            # Step 3: Call Ollama LLM
            logger.info("🤖 Step 3: Calling Ollama LLM...")
            response = self.ollama.generate_structured(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Step 4: Process response
            if "error" in response:
                logger.error(f"❌ Ollama error: {response['error']}")
                self._log_failure(
                    schedule_id, target_date, context, response, execution_time_ms
                )
                return {
                    "success": False,
                    "error": response["error"],
                    "message": response.get("message", "LLM call failed")
                }
            
            if "parsed" not in response:
                logger.error("❌ Failed to parse LLM response")
                self._log_failure(
                    schedule_id, target_date, context, response, execution_time_ms
                )
                return {
                    "success": False,
                    "error": "parse_error",
                    "message": "Could not parse JSON from LLM response",
                    "raw_response": response.get("response", "")
                }
            
            prediction_data = response["parsed"]
            logger.info("✅ Successfully parsed prediction")
            
            # Step 5: Validate prediction
            validation_result = self._validate_prediction(prediction_data, total_compartments)
            if not validation_result["valid"]:
                logger.warning(f"⚠️ Prediction validation failed: {validation_result['reason']}")
                # Try to fix it
                prediction_data = self._fix_prediction(prediction_data, total_compartments)
            
            # Step 6: Calculate capacity
            seats_per_comp = train_info.get("seats_per_compartment", 60)
            standing_per_comp = train_info.get("standing_per_compartment", 40)
            total_per_comp = train_info.get("total_capacity_per_compartment", 100)
            
            prediction_data["predicted_first_class_capacity"] = (
                prediction_data["predicted_first_class"] * total_per_comp
            )
            prediction_data["predicted_second_class_capacity"] = (
                prediction_data["predicted_second_class"] * total_per_comp
            )
            prediction_data["predicted_third_class_capacity"] = (
                prediction_data["predicted_third_class"] * total_per_comp
            )
            prediction_data["total_predicted_capacity"] = (
                prediction_data["predicted_first_class_capacity"] +
                prediction_data["predicted_second_class_capacity"] +
                prediction_data["predicted_third_class_capacity"]
            )
            
            # Step 7: Save to database
            if save_to_db:
                logger.info("💾 Step 7: Saving prediction to database...")
                db_prediction = self._save_prediction(
                    schedule_id, route_id, target_date, prediction_data,
                    total_compartments, context, response
                )
                prediction_data["prediction_id"] = db_prediction.id
            
            # Log success
            self._log_success(
                schedule_id, target_date, context, prediction_data, execution_time_ms
            )
            
            logger.info(f"🎉 Prediction completed in {execution_time_ms:.0f}ms")
            
            return {
                "success": True,
                "prediction": prediction_data,
                "execution_time_ms": int(execution_time_ms),
                "context_summary": {
                    "historical_records": context["historical_demand"].get("total_records", 0),
                    "avg_passengers": context["historical_demand"].get("avg_total_passengers", 0),
                    "route_type": context["route"].get("route_type", "unknown")
                }
            }
        
        except Exception as e:
            logger.error(f"❌ Prediction failed with exception: {e}", exc_info=True)
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._log_failure(schedule_id, target_date, {}, {"error": str(e)}, execution_time_ms)
            return {
                "success": False,
                "error": "exception",
                "message": str(e)
            }
    
    def _validate_prediction(self, prediction: Dict, total_compartments: int) -> Dict[str, Any]:
        """Validate prediction meets constraints"""
        try:
            first = prediction.get("predicted_first_class", 0)
            second = prediction.get("predicted_second_class", 0)
            third = prediction.get("predicted_third_class", 0)
            
            # Check all are integers
            if not all(isinstance(x, int) for x in [first, second, third]):
                return {"valid": False, "reason": "Non-integer compartment counts"}
            
            # Check non-negative
            if any(x < 0 for x in [first, second, third]):
                return {"valid": False, "reason": "Negative compartment counts"}
            
            # Check sum
            if first + second + third != total_compartments:
                return {"valid": False, "reason": f"Sum ({first + second + third}) != total ({total_compartments})"}
            
            # Check at least 1 third class
            if third < 1:
                return {"valid": False, "reason": "Must have at least 1 third class compartment"}
            
            return {"valid": True}
        except Exception as e:
            return {"valid": False, "reason": f"Validation error: {e}"}
    
    def _fix_prediction(self, prediction: Dict, total_compartments: int) -> Dict:
        """Attempt to fix invalid prediction"""
        first = max(0, int(prediction.get("predicted_first_class", 0)))
        second = max(0, int(prediction.get("predicted_second_class", 0)))
        third = max(1, int(prediction.get("predicted_third_class", 0)))
        
        # Adjust to match total
        current_sum = first + second + third
        if current_sum != total_compartments:
            diff = total_compartments - current_sum
            third = max(1, third + diff)
        
        prediction["predicted_first_class"] = first
        prediction["predicted_second_class"] = second
        prediction["predicted_third_class"] = third
        
        return prediction
    
    def _save_prediction(
        self,
        schedule_id: str,
        route_id: str,
        target_date: date,
        prediction_data: Dict,
        total_compartments: int,
        context: Dict,
        ollama_response: Dict
    ) -> CompartmentPrediction:
        """Save prediction to database"""
        
        # Deactivate old predictions for this schedule+date
        self.db.query(CompartmentPrediction).filter(
            CompartmentPrediction.schedule_id == schedule_id,
            CompartmentPrediction.schedule_date == target_date,
            CompartmentPrediction.is_active == 1
        ).update({"is_active": 0})
        
        # Create new prediction
        db_prediction = CompartmentPrediction(
            schedule_id=schedule_id,
            schedule_date=target_date,
            route_id=route_id,
            predicted_first_class=prediction_data["predicted_first_class"],
            predicted_second_class=prediction_data["predicted_second_class"],
            predicted_third_class=prediction_data["predicted_third_class"],
            total_compartments=total_compartments,
            predicted_first_class_capacity=prediction_data["predicted_first_class_capacity"],
            predicted_second_class_capacity=prediction_data["predicted_second_class_capacity"],
            predicted_third_class_capacity=prediction_data["predicted_third_class_capacity"],
            total_predicted_capacity=prediction_data["total_predicted_capacity"],
            expected_total_passengers=prediction_data.get("expected_total_passengers"),
            expected_first_class_demand=prediction_data.get("expected_first_class_demand", 0),
            expected_second_class_demand=prediction_data.get("expected_second_class_demand", 0),
            expected_third_class_demand=prediction_data.get("expected_third_class_demand", 0),
            model_name=ollama_response.get("model", "ollama:llama3.1"),
            confidence_score=prediction_data.get("confidence_score"),
            reasoning=prediction_data.get("reasoning", ""),
            historical_context=context.get("historical_demand", {}),
            factors_considered=prediction_data.get("factors_considered", []),
            is_active=1
        )
        
        self.db.add(db_prediction)
        self.db.commit()
        self.db.refresh(db_prediction)
        
        return db_prediction
    
    def _log_success(self, schedule_id: str, target_date: date, context: Dict, prediction: Dict, exec_time: float):
        """Log successful prediction"""
        log = PredictionLog(
            schedule_id=schedule_id,
            schedule_date=target_date,
            request_type="auto_prediction",
            input_data={"context_summary": str(context)[:500]},
            success=1,
            response_data=prediction,
            execution_time_ms=int(exec_time),
            model_name=self.ollama.model,
            triggered_by="system"
        )
        self.db.add(log)
        self.db.commit()
    
    def _log_failure(self, schedule_id: str, target_date: date, context: Dict, error: Dict, exec_time: float):
        """Log failed prediction"""
        log = PredictionLog(
            schedule_id=schedule_id,
            schedule_date=target_date,
            request_type="auto_prediction",
            input_data={"context_summary": str(context)[:500]},
            success=0,
            response_data=None,
            error_message=str(error),
            execution_time_ms=int(exec_time),
            model_name=self.ollama.model,
            triggered_by="system"
        )
        self.db.add(log)
        self.db.commit()
