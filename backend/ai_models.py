"""
AI-Enhanced Models for Compartment Prediction System
Database models for storing AI-generated predictions
"""
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, 
    DECIMAL, Text, Float, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from backend.db import Base
from datetime import datetime
from typing import Optional


class CompartmentPrediction(Base):
    """
    AI-generated compartment allocation predictions using Ollama RAG
    Stores predictions for train schedules to enable advance booking and optimization
    """
    __tablename__ = "compartment_predictions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Schedule Reference
    schedule_id = Column(
        String(20),
        ForeignKey("train_schedules.train_schedule_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    schedule_date = Column(Date, nullable=False, index=True)
    route_id = Column(String(10), index=True)
    
    # Predicted Compartment Allocation
    predicted_first_class = Column(Integer, nullable=False, default=0)
    predicted_second_class = Column(Integer, nullable=False, default=0)
    predicted_third_class = Column(Integer, nullable=False, default=0)
    total_compartments = Column(Integer, nullable=False)
    
    # Predicted Capacity (seats)
    predicted_first_class_capacity = Column(Integer, default=0)
    predicted_second_class_capacity = Column(Integer, default=0)
    predicted_third_class_capacity = Column(Integer, default=0)
    total_predicted_capacity = Column(Integer, default=0)
    
    # Expected Demand
    expected_total_passengers = Column(Integer)
    expected_first_class_demand = Column(Integer, default=0)
    expected_second_class_demand = Column(Integer, default=0)
    expected_third_class_demand = Column(Integer, default=0)
    
    # AI Model Information
    model_name = Column(String(50), default="ollama:llama3.1")
    model_version = Column(String(20))
    confidence_score = Column(Float)  # 0.0 to 1.0
    
    # Reasoning & Context
    reasoning = Column(Text)  # Why this allocation was chosen
    historical_context = Column(JSON)  # Summary of data used
    factors_considered = Column(JSON)  # List of factors (holidays, weather, etc.)
    
    # Actual vs Predicted (filled after the fact)
    actual_first_class = Column(Integer)
    actual_second_class = Column(Integer)
    actual_third_class = Column(Integer)
    actual_passengers = Column(Integer)
    
    # Accuracy Metrics
    prediction_accuracy = Column(Float)  # Calculated after the date
    
    # Status & Metadata
    is_active = Column(Integer, default=1)  # Boolean: 1=active, 0=superseded
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    # schedule = relationship("TrainSchedule", back_populates="ai_predictions")
    
    __table_args__ = (
        # Unique constraint: one active prediction per schedule+date
        # Index('idx_unique_active_prediction', 'schedule_id', 'schedule_date', 'is_active', unique=True),
        {},
    )
    
    def __repr__(self):
        return (
            f"<CompartmentPrediction(schedule={self.schedule_id}, "
            f"date={self.schedule_date}, "
            f"predicted={self.predicted_first_class}/{self.predicted_second_class}/{self.predicted_third_class})>"
        )


class PredictionLog(Base):
    """
    Audit trail for all prediction attempts (success and failures)
    Helps track model performance and debugging
    """
    __tablename__ = "prediction_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(String(20), index=True)
    schedule_date = Column(Date, index=True)
    
    # Request Information
    request_type = Column(String(50))  # 'auto_schedule', 'manual_request', etc.
    input_data = Column(JSON)  # Summary of input provided to model
    
    # Response Information
    success = Column(Integer, default=1)  # Boolean
    response_data = Column(JSON)  # Raw model response
    error_message = Column(Text)
    
    # Performance Metrics
    execution_time_ms = Column(Integer)  # How long it took
    tokens_used = Column(Integer)  # If available from Ollama
    
    # Metadata
    model_name = Column(String(50))
    triggered_by = Column(String(100))  # User ID or 'system'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"<PredictionLog({status}, schedule={self.schedule_id}, date={self.schedule_date})>"
