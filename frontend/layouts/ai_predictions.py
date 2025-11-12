"""
Example Frontend Layout for AI Predictions
Add this to your Dash frontend to display AI predictions
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"

def layout():
    """
    AI Predictions page layout
    """
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("🤖 AI-Powered Compartment Predictions"),
                html.P("Predict optimal compartment allocation using historical data and AI", 
                       className="text-muted")
            ])
        ], className="mb-4"),
        
        # Status Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Ollama Status", className="card-title"),
                        html.Div(id="ollama-status"),
                        dbc.Button("Refresh", id="refresh-status-btn", size="sm", className="mt-2")
                    ])
                ])
            ], width=4)
        ], className="mb-4"),
        
        # Prediction Form
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Generate New Prediction"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Schedule ID"),
                                dbc.Input(id="pred-schedule-id", placeholder="e.g., SCH001", type="text")
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Route ID"),
                                dbc.Input(id="pred-route-id", placeholder="e.g., R01", type="text")
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Train ID"),
                                dbc.Input(id="pred-train-id", placeholder="e.g., T001", type="text")
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Target Date"),
                                dcc.DatePickerSingle(
                                    id="pred-target-date",
                                    date=(datetime.now() + timedelta(days=7)).date(),
                                    display_format="YYYY-MM-DD"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Button(
                            "🎯 Generate Prediction", 
                            id="generate-pred-btn", 
                            color="primary", 
                            className="w-100",
                            size="lg"
                        ),
                        
                        dbc.Spinner(html.Div(id="prediction-loading"), color="primary", className="mt-3")
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Results Section
        dbc.Row([
            dbc.Col([
                html.Div(id="prediction-results")
            ], width=12)
        ])
        
    ], fluid=True)


@callback(
    Output("ollama-status", "children"),
    Input("refresh-status-btn", "n_clicks"),
    prevent_initial_call=False
)
def check_ollama_status(n_clicks):
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/ai/health", timeout=2)
        data = response.json()
        
        if data["is_running"]:
            return dbc.Alert([
                html.Strong("✅ Ollama is Running"),
                html.Br(),
                html.Small(f"Model: {data['current_model']}")
            ], color="success")
        else:
            return dbc.Alert([
                html.Strong("⚠️ Ollama is Not Running"),
                html.Br(),
                html.Small("Start Ollama: ollama serve")
            ], color="warning")
    
    except Exception as e:
        return dbc.Alert([
            html.Strong("❌ Cannot Connect"),
            html.Br(),
            html.Small(str(e))
        ], color="danger")


@callback(
    [Output("prediction-results", "children"),
     Output("prediction-loading", "children")],
    Input("generate-pred-btn", "n_clicks"),
    [State("pred-schedule-id", "value"),
     State("pred-route-id", "value"),
     State("pred-train-id", "value"),
     State("pred-target-date", "date")],
    prevent_initial_call=True
)
def generate_prediction(n_clicks, schedule_id, route_id, train_id, target_date):
    """Generate AI prediction"""
    if not all([schedule_id, route_id, train_id, target_date]):
        return dbc.Alert("Please fill in all fields", color="warning"), ""
    
    try:
        # Show loading
        loading_msg = dbc.Alert("🤖 AI is analyzing historical data and generating prediction...", color="info")
        
        # Call API
        response = requests.post(
            f"{API_BASE_URL}/api/ai/predict",
            json={
                "schedule_id": schedule_id,
                "route_id": route_id,
                "train_id": train_id,
                "target_date": target_date
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return dbc.Alert(f"Error: {response.text}", color="danger"), ""
        
        data = response.json()
        
        # Create visualization
        fig = go.Figure(data=[
            go.Bar(
                name="Compartments",
                x=["First Class", "Second Class", "Third Class"],
                y=[
                    data["predicted_first_class"],
                    data["predicted_second_class"],
                    data["predicted_third_class"]
                ],
                marker_color=["gold", "silver", "#CD7F32"]
            )
        ])
        
        fig.update_layout(
            title="Predicted Compartment Allocation",
            yaxis_title="Number of Compartments",
            height=300
        )
        
        result_card = dbc.Card([
            dbc.CardHeader([
                html.H4("✅ Prediction Generated Successfully"),
                html.Small(f"Confidence: {data['confidence_score']:.1%}", className="text-muted")
            ]),
            dbc.CardBody([
                dbc.Row([
                    # Left: Chart
                    dbc.Col([
                        dcc.Graph(figure=fig)
                    ], width=6),
                    
                    # Right: Details
                    dbc.Col([
                        html.H5("Allocation Details"),
                        dbc.Table([
                            html.Tbody([
                                html.Tr([
                                    html.Td("First Class:"),
                                    html.Td(html.Strong(f"{data['predicted_first_class']} compartments"))
                                ]),
                                html.Tr([
                                    html.Td("Second Class:"),
                                    html.Td(html.Strong(f"{data['predicted_second_class']} compartments"))
                                ]),
                                html.Tr([
                                    html.Td("Third Class:"),
                                    html.Td(html.Strong(f"{data['predicted_third_class']} compartments"))
                                ]),
                                html.Tr([
                                    html.Td("Total:"),
                                    html.Td(html.Strong(f"{data['total_compartments']} compartments"), style={"border-top": "2px solid black"})
                                ])
                            ])
                        ], bordered=True, hover=True, className="mt-2"),
                        
                        html.Hr(),
                        
                        html.H5("AI Reasoning", className="mt-3"),
                        html.P(data.get("reasoning", "No reasoning provided"), className="text-muted")
                    ], width=6)
                ])
            ])
        ], className="mt-3")
        
        return result_card, ""
    
    except requests.exceptions.Timeout:
        return dbc.Alert("⏱️ Request timed out. AI analysis takes time, please try again.", color="warning"), ""
    except Exception as e:
        return dbc.Alert(f"❌ Error: {str(e)}", color="danger"), ""


# Register this in your main Dash app
# app.layout = layout()
