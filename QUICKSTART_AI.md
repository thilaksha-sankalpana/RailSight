# 🚀 Quick Start Guide - AI Compartment Prediction

## ⚡ Fastest Way to Get Started

### 1️⃣ Install Ollama (5 minutes)

**Windows/Mac:**
- Download from https://ollama.com/download
- Run installer

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2️⃣ Download AI Model (5-10 minutes)
```bash
ollama pull llama3.1
```

### 3️⃣ Install Python Dependencies
```bash
cd d:\Projects\Python\TCDAFS
pip install requests python-dotenv
```

### 4️⃣ Setup Database
```bash
python scripts/migrate_ai_tables.py
```

### 5️⃣ Add to .env file
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### 6️⃣ Update backend/app.py
Add this line:
```python
from backend.api_ai_predictions import router as ai_router
app.include_router(ai_router)
```

### 7️⃣ Test It!
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start backend
python run_server.py

# Terminal 3: Test
curl http://localhost:8000/api/ai/health
```

## 🎯 First Prediction

```python
import requests

response = requests.post("http://localhost:8000/api/ai/predict", json={
    "schedule_id": "SCH001",  # Replace with your schedule ID
    "route_id": "R01",        # Replace with your route ID
    "train_id": "T001",       # Replace with your train ID
    "target_date": "2025-11-20"
})

print(response.json())
```

Expected output:
```json
{
  "success": true,
  "predicted_first_class": 1,
  "predicted_second_class": 2,
  "predicted_third_class": 5,
  "confidence_score": 0.85,
  "reasoning": "Based on 90 days of historical data..."
}
```

## 📊 How It Works

1. **You ask** for a prediction (schedule + date)
2. **System retrieves** historical data from your database
3. **AI analyzes** patterns, trends, pricing, demand
4. **AI predicts** optimal compartment allocation
5. **System saves** prediction with reasoning

## 🆘 Troubleshooting

### "Ollama is not running"
```bash
ollama serve
```

### "Model not found"
```bash
ollama pull llama3.1
ollama list
```

### "No historical data"
- Ensure you have `passenger_demand_history` records
- System needs at least 30 days of data for good predictions

## 📈 Performance Tips

- **First prediction**: ~20-30 seconds (model loading)
- **Subsequent predictions**: ~5-10 seconds
- **Faster predictions**: Use `ollama pull llama3.1:8b` (smaller model)

## 🎨 Frontend Example

See `frontend/layouts/ai_predictions.py` for Dash integration example.

## 📚 Full Documentation

See `AI_SETUP_GUIDE.md` for complete documentation.

---

**Ready to predict! 🎉**
