# RailSight

**Train Compartment Demand Analysis and Forecasting Platform**

RailSight is a full-stack railway operations platform that forecasts passenger demand by compartment class, optimises train-to-schedule allocation, and delivers real-time operational analytics through an interactive dashboard. It combines a machine learning backend with a natural-language query interface and comprehensive management capabilities for schedules, pricing, ticketing, and daily reporting.

---

## Features

**Demand Forecasting** forecasts compartment class distribution using trained machine learning models with scikit-learn and LightGBM, enabling data-driven capacity planning.

**Allocation Optimisation** assigns trains to schedules with conflict-aware logic to maximise utilisation and operational efficiency.

**Natural Language Querying** powered by Ollama RAG integration, allowing analysts to query schedule and demand data using natural language without requiring SQL expertise.

**Operations Dashboard** provides real-time analytics through an interactive Plotly and Dash interface covering schedules, pricing, ticketing, and demand summaries.

**Secure API** implements role-based JWT authentication with OAuth2 support and production-grade middleware for logging, CORS, and exception handling.

**Complete CRUD Management** for stations, routes, trains, schedules, pricing tiers, and ticket transactions.

---

## Tech Stack

**Backend**

Python, FastAPI, Uvicorn, SQLAlchemy ORM, PostgreSQL (psycopg2), scikit-learn, LightGBM, Pandas, NumPy, joblib, Ollama RAG integration, JWT authentication via python-jose, bcrypt via passlib, Pydantic, python-dotenv, Alembic for schema migrations.

**Frontend**

Python Dash, Plotly for visualisations, Dash Bootstrap Components for UI consistency, Requests for HTTP communication, Pandas and NumPy for data manipulation.

---

## Project Structure

```
TCDAFS-Project/
├── backend/
│   ├── app.py                      # FastAPI application and route registration
│   ├── db.py                       # Database engine and session management
│   ├── models.py                   # SQLAlchemy ORM models
│   ├── schemas.py                  # Pydantic request/response schemas
│   ├── auth.py                     # JWT authentication and role authorisation
│   ├── train_allocator.py          # Conflict-aware train allocation optimiser
│   ├── compartment_predictor.py    # Compartment class demand predictor
│   ├── api_ai_predictions.py       # AI prediction API router
│   ├── ai_models.py                # Model loading and inference
│   ├── Requirements.txt            # Python dependencies
│   ├── middleware/
│   │   └── logging_middleware.py   # Request/response logging
│   ├── services/
│   │   ├── ai_prediction_engine.py # Core prediction logic
│   │   ├── ollama_service.py       # Ollama RAG service layer
│   │   ├── rag_data_service.py     # RAG data preparation
│   │   └── capacity_service.py     # Capacity calculations
│   └── utils/
│       ├── calendar_service.py     # Date and calendar utilities
│       ├── validators.py           # Data validation helpers
│       ├── helpers.py              # General utilities
│       └── errors.py               # Custom exception classes
├── frontend/
│   ├── app.py                      # Dash application entry point
│   ├── requirements.txt            # Python dependencies
│   ├── config/
│   │   ├── settings.py             # Configuration and API URL
│   │   └── styles.py               # Theme and styling configuration
│   ├── layouts/
│   │   ├── overview.py             # Dashboard overview page
│   │   ├── schedules.py            # Schedule management
│   │   ├── daily_schedules.py      # Daily schedule view
│   │   ├── trains.py               # Train management
│   │   ├── routes.py               # Route management
│   │   ├── pricing.py              # Pricing management
│   │   ├── tickets.py              # Ticket management
│   │   ├── ticket_verification.py  # Ticket validation
│   │   ├── train_models.py         # Model management
│   │   ├── ai_predictions.py       # Predictions interface
│   │   └── schedule_by_station.py  # Station-based schedules
│   ├── callbacks/
│   │   ├── auth_callbacks.py       # Authentication callbacks
│   │   ├── overview_callbacks.py   # Dashboard callbacks
│   │   ├── navigation_callbacks.py # Navigation logic
│   │   └── [other page callbacks]  # Feature-specific callbacks
│   ├── components/
│   │   ├── auth/                   # Authentication components
│   │   └── common/                 # Shared UI components
│   ├── assets/
│   │   └── custom.css              # Custom styling
│   └── utils/
│       ├── api.py                  # Backend HTTP client wrapper
│       └── cache.py                # Caching utilities
├── model_artifacts/
│   └── schema_only.sql             # Database schema reference
├── scripts/
│   └── create_admin.py             # Admin user creation script
├── run_server.py                   # Backend startup script
├── run_dashboard.py                # Frontend startup script
└── railway_system.db               # SQLite development database

```

---

## Getting Started

### Prerequisites

Python 3.10 or later, PostgreSQL, and Ollama (optional, for RAG features).

### Installation

1. Clone the repository

```bash
git clone https://github.com/thilaksha-sankalpana/Train-Compartment-Demand-Analysis-and-Forecasting-Platform.git
cd Train-Compartment-Demand-Analysis-and-Forecasting-Platform
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate              # Windows
source .venv/bin/activate             # Linux/macOS
```

3. Install dependencies

```bash
pip install -r backend/Requirements.txt
pip install -r frontend/requirements.txt
```

4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/railsight
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Set up the database

```bash
# Create database and run migrations
alembic upgrade head
```

6. Create an admin user (optional)

```bash
python scripts/create_admin.py
```

7. Start the backend server

```bash
python run_server.py
```

8. Start the frontend dashboard (in a new terminal)

```bash
python run_dashboard.py
```

The backend API will be available at http://localhost:8000 and the dashboard at http://localhost:8050.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/token` | Obtain JWT access token |
| GET, POST | `/stations` | Station management |
| GET, POST | `/trains` | Train management |
| GET, POST | `/schedules` | Schedule management and queries |
| GET, POST | `/tickets` | Ticket creation and management |
| GET | `/analytics/summary` | Dashboard summary analytics |
| POST | `/predict/compartments` | Compartment demand prediction |
| POST | `/allocate/train` | Train-to-schedule allocation |

Full API documentation is available via Swagger UI at http://localhost:8000/docs when the backend server is running.

---

## System Architecture

```
┌─────────────────────┐        HTTP / REST        ┌──────────────────────┐
│   Dash Frontend     │ ◄────────────────────────► │   FastAPI Backend    │
│  (localhost:8050)   │                            │  (localhost:8000)   │
└─────────────────────┘                            └──────────┬───────────┘
                                                              │
                                          ┌───────────────────┼───────────────────┐
                                          │                   │                   │
                                   ┌──────▼──────┐   ┌────────▼──────┐   ┌───────▼──────┐
                                   │ PostgreSQL  │   │  ML Engine    │   │  Ollama RAG  │
                                   │  Database   │   │ (LightGBM /   │   │   Service    │
                                   └─────────────┘   │  scikit-learn)│   └──────────────┘
                                                      └───────────────┘
```

---

## Key Components

**Backend Services** handle forecasting through trained ML models, capacity optimisation algorithms, RAG-powered natural language queries, and secure REST API endpoints.

**Frontend Interface** provides a comprehensive dashboard for real-time monitoring, data entry forms for schedules and tickets, predictive analytics visualisations, and user-friendly navigation.

**Database Layer** maintains normalised schema for stations, routes, trains, schedules, pricing, tickets, and ML model metadata.

**Authentication** implements JWT-based stateless authentication with role-based access control (RBAC) for operational security.

---

## Usage

Access the dashboard at http://localhost:8050. Log in with your credentials to view operational summaries, manage schedules and trains, create pricing rules, issue and verify tickets, and run demand forecasts.

Use the API directly via http://localhost:8000/docs for programmatic access, or query the system using natural language through the Ollama RAG interface.

---

## License

This project is licensed under the MIT License. See LICENSE for details.

---

## Contact

For questions or feedback, please reach out to the development team through the GitHub repository.
