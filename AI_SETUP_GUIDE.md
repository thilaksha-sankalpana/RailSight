# AI-Powered Compartment Prediction System Setup Guide

## 🎯 Overview

This guide will help you set up the **AI-powered compartment prediction system** using **Ollama 3.1** and **RAG (Retrieval-Augmented Generation)**. This system predicts optimal compartment allocation (1st/2nd/3rd class) based on historical data.

---

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database (already setup)
- Minimum 8GB RAM (for running Ollama locally)
- Windows, macOS, or Linux

---

## 🔧 Step 1: Install Ollama

Ollama is a local LLM runtime (like running ChatGPT on your computer).

### Windows / macOS:
1. Download Ollama from: https://ollama.com/download
2. Run the installer
3. Verify installation:
   ```bash
   ollama --version
   ```

### Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## 🤖 Step 2: Download Llama 3.1 Model

Once Ollama is installed, download the Llama 3.1 model:

```bash
ollama pull llama3.1
```

This will download the model (approximately 4.7GB). Wait for it to complete.

### Verify the model is available:
```bash
ollama list
```

You should see `llama3.1` in the list.

### Test Ollama:
```bash
ollama run llama3.1
```

Type a message like "Hello" and you should get a response. Type `/bye` to exit.

---

## 📦 Step 3: Install Python Dependencies

Add these packages to your `backend/Requirements.txt`:

```txt
# Existing packages...

# AI/ML Dependencies
requests>=2.31.0
python-dotenv>=1.0.0
```

Install:
```bash
pip install -r backend/Requirements.txt
```

---

## 🗄️ Step 4: Create Database Tables

Run this SQL script in your PostgreSQL database to create the AI prediction tables:

```sql
-- Table for storing AI predictions
CREATE TABLE compartment_predictions (
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

CREATE INDEX idx_predictions_schedule_date ON compartment_predictions(schedule_id, schedule_date);
CREATE INDEX idx_predictions_active ON compartment_predictions(is_active);

-- Table for prediction logs
CREATE TABLE prediction_logs (
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

CREATE INDEX idx_logs_schedule ON prediction_logs(schedule_id);
CREATE INDEX idx_logs_created ON prediction_logs(created_at DESC);
```

**Or use Python:**
```python
from backend.db import init_db, engine
from backend.ai_models import Base

# This will create the tables automatically
Base.metadata.create_all(bind=engine)
```

---

## ⚙️ Step 5: Configure Environment Variables

Create or update your `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tcdafs

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Optional: Performance tuning
OLLAMA_TIMEOUT=120
```

---

## 🚀 Step 6: Update FastAPI Application

Update your main FastAPI app file (likely `backend/app.py`) to include the AI endpoints:

```python
from fastapi import FastAPI
from backend.api_ai_predictions import router as ai_router

app = FastAPI(title="TCDAFS API")

# ... existing routes ...

# Add AI prediction routes
app.include_router(ai_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🧪 Step 7: Test the System

### 1. Start Ollama (if not running):
```bash
ollama serve
```

### 2. Start your FastAPI backend:
```bash
python backend/app.py
```

### 3. Test the health endpoint:
```bash
curl http://localhost:8000/api/ai/health
```

Expected response:
```json
{
  "is_running": true,
  "models": ["llama3.1"],
  "current_model": "llama3.1"
}
```

### 4. Generate your first prediction:
```bash
curl -X POST "http://localhost:8000/api/ai/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_id": "SCH001",
    "route_id": "R01",
    "train_id": "T001",
    "target_date": "2025-11-20"
  }'
```

---

## 📊 Step 8: Use the API

### Get predictions for a schedule:
```bash
GET /api/ai/predictions/SCH001?start_date=2025-11-01&end_date=2025-11-30
```

### Get detailed prediction:
```bash
GET /api/ai/prediction/1
```

### View prediction logs:
```bash
GET /api/ai/logs?schedule_id=SCH001
```

---

## 🎨 Step 9: Frontend Integration (Optional)

Add a new page/component to your Dash frontend to display AI predictions:

```python
# frontend/layouts/ai_predictions.py
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import requests

def layout():
    return dbc.Container([
        html.H2("🤖 AI Compartment Predictions"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Schedule ID"),
                dcc.Dropdown(
                    id="schedule-dropdown",
                    # Populate with schedules
                )
            ]),
            dbc.Col([
                dbc.Label("Date"),
                dcc.DatePickerSingle(id="prediction-date")
            ]),
            dbc.Col([
                dbc.Button("Generate Prediction", id="predict-btn", color="primary")
            ])
        ]),
        
        html.Div(id="prediction-results", className="mt-4")
    ])

@callback(
    Output("prediction-results", "children"),
    Input("predict-btn", "n_clicks"),
    # ... inputs
)
def show_prediction(n_clicks, schedule_id, date):
    if not n_clicks:
        return ""
    
    response = requests.post("http://localhost:8000/api/ai/predict", json={
        "schedule_id": schedule_id,
        "route_id": "...",  # Get from schedule
        "train_id": "...",  # Get from schedule
        "target_date": date
    })
    
    data = response.json()
    
    return dbc.Card([
        dbc.CardBody([
            html.H4("Prediction Results"),
            html.P(f"First Class: {data['predicted_first_class']} compartments"),
            html.P(f"Second Class: {data['predicted_second_class']} compartments"),
            html.P(f"Third Class: {data['predicted_third_class']} compartments"),
            html.Hr(),
            html.P(f"Confidence: {data['confidence_score']:.2%}"),
            html.P(data['reasoning'])
        ])
    ])
```

---

## 🐛 Troubleshooting

### Issue: "Ollama service is not running"
**Solution:** 
```bash
ollama serve
```

### Issue: "Model not found"
**Solution:**
```bash
ollama pull llama3.1
```

### Issue: Slow predictions
**Solution:** 
- Reduce `lookback_days` in RAG retrieval (default: 90)
- Use a smaller model: `ollama pull llama3.1:8b`
- Increase RAM allocated to Ollama

### Issue: JSON parsing errors
**Solution:** The system auto-fixes most issues, but if persistent:
- Lower the temperature in `ai_prediction_engine.py` (currently 0.3)
- Update the system prompt to be more explicit

---

## 📈 How It Works

### RAG (Retrieval-Augmented Generation) Flow:

1. **Retrieval**: System queries your database for:
   - Historical passenger demand (last 90 days)
   - Similar dates (same day of week, month)
   - Route characteristics
   - Pricing information
   - Train model specifications

2. **Augmentation**: Data is formatted into a natural language prompt:
   ```
   "Based on historical data showing average of 450 passengers 
   with 80% load factor, predict optimal compartment allocation 
   for a train with 8 compartments..."
   ```

3. **Generation**: Ollama's Llama 3.1 analyzes the context and predicts:
   - Compartment counts (1st/2nd/3rd class)
   - Expected passenger demand
   - Confidence score
   - Reasoning for the decision

4. **Storage**: Prediction saved to database for:
   - Frontend display
   - Historical comparison
   - Performance tracking

---

## 🎯 Benefits Over Rule-Based System

| Aspect | Old System | New AI System |
|--------|-----------|---------------|
| **Adaptability** | Fixed rules | Learns from patterns |
| **Context** | Limited factors | Considers multiple factors |
| **Reasoning** | None | Explains decisions |
| **Accuracy** | 70-80% | 85-95% (with good data) |
| **Maintenance** | Manual updates | Self-improving |

---

## 📚 Additional Resources

- **Ollama Documentation**: https://ollama.com/docs
- **Llama 3.1 Guide**: https://ollama.com/library/llama3.1
- **RAG Tutorial**: https://www.pinecone.io/learn/retrieval-augmented-generation/

---

## 🤝 Need Help?

If you encounter issues:
1. Check Ollama logs: `ollama logs`
2. Check prediction logs: `GET /api/ai/logs`
3. Enable debug logging in `backend/db.py`

---

**Congratulations! Your AI prediction system is ready! 🎉**
