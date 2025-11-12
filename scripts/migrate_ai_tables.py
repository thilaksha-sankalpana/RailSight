"""
Database Migration Script for AI Prediction Tables
Run this to create the new tables without affecting existing data
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    print("❌ DATABASE_URL not set in .env file")
    exit(1)

engine = create_engine(DB_URL)

# SQL for creating AI prediction tables
CREATE_TABLES_SQL = """
-- Table for storing AI predictions
CREATE TABLE IF NOT EXISTS compartment_predictions (
    id SERIAL PRIMARY KEY,
    schedule_id VARCHAR(20) NOT NULL,
    schedule_date DATE NOT NULL,
    route_id VARCHAR(10),
    
    -- Predicted allocation
    predicted_first_class INTEGER NOT NULL DEFAULT 0,
    predicted_second_class INTEGER NOT NULL DEFAULT 0,
    predicted_third_class INTEGER NOT NULL DEFAULT 0,
    total_compartments INTEGER NOT NULL,
    
    -- Predicted capacity
    predicted_first_class_capacity INTEGER DEFAULT 0,
    predicted_second_class_capacity INTEGER DEFAULT 0,
    predicted_third_class_capacity INTEGER DEFAULT 0,
    total_predicted_capacity INTEGER DEFAULT 0,
    
    -- Expected demand
    expected_total_passengers INTEGER,
    expected_first_class_demand INTEGER DEFAULT 0,
    expected_second_class_demand INTEGER DEFAULT 0,
    expected_third_class_demand INTEGER DEFAULT 0,
    
    -- AI model info
    model_name VARCHAR(50) DEFAULT 'ollama:llama3.1',
    model_version VARCHAR(20),
    confidence_score FLOAT,
    
    -- Reasoning
    reasoning TEXT,
    historical_context JSON,
    factors_considered JSON,
    
    -- Actual vs predicted (for learning)
    actual_first_class INTEGER,
    actual_second_class INTEGER,
    actual_third_class INTEGER,
    actual_passengers INTEGER,
    prediction_accuracy FLOAT,
    
    -- Metadata
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (schedule_id) REFERENCES train_schedules(train_schedule_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_predictions_schedule_date 
    ON compartment_predictions(schedule_id, schedule_date);
CREATE INDEX IF NOT EXISTS idx_predictions_active 
    ON compartment_predictions(is_active);

-- Table for prediction logs
CREATE TABLE IF NOT EXISTS prediction_logs (
    id SERIAL PRIMARY KEY,
    schedule_id VARCHAR(20),
    schedule_date DATE,
    request_type VARCHAR(50),
    input_data JSON,
    success INTEGER DEFAULT 1,
    response_data JSON,
    error_message TEXT,
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    model_name VARCHAR(50),
    triggered_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_schedule 
    ON prediction_logs(schedule_id);
CREATE INDEX IF NOT EXISTS idx_logs_created 
    ON prediction_logs(created_at DESC);
"""

def run_migration():
    """Run the migration to create AI prediction tables"""
    print("🔄 Starting database migration...")
    
    try:
        with engine.connect() as conn:
            # Execute the migration SQL
            conn.execute(text(CREATE_TABLES_SQL))
            conn.commit()
            
            print("✅ Migration completed successfully!")
            print("📊 Created tables:")
            print("   - compartment_predictions")
            print("   - prediction_logs")
            
            # Verify tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name IN ('compartment_predictions', 'prediction_logs')
            """))
            
            tables = [row[0] for row in result]
            print(f"\n✓ Verified: {tables}")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
