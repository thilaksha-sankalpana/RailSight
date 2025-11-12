"""
TCDAFS - Daily Schedules Callbacks
Handle daily schedule viewing and AI predictions display
"""
from dash import Input, Output, State, html, callback_context, ALL
import dash_bootstrap_components as dbc
from datetime import datetime
import logging
from config.styles import COLORS
from utils.api import make_api_request

logger = logging.getLogger(__name__)


def register(app):
    """Register daily schedule callbacks with the app"""
    
    @app.callback(
        [Output("daily-schedules-container", "children"),
         Output("daily-schedule-count", "children"),
         Output("daily-schedule-alert", "children"),
         Output("daily-schedule-alert", "is_open"),
         Output("daily-schedule-alert", "color")],
        [Input("load-daily-schedules-btn", "n_clicks"),
         Input({'type': 'generate-prediction-btn', 'index': ALL}, 'n_clicks')],
        [State("daily-schedule-date", "value"),
         State("token-store", "data")],
        prevent_initial_call=False
    )
    def load_daily_schedules(n_clicks, generate_clicks, schedule_date, token):
        """Load schedules for selected date with AI predictions"""
        if not token:
            return html.Div("Please log in to view schedules"), "0", "", False, "warning"
        
        # Use today's date if none selected
        if not schedule_date:
            schedule_date = datetime.now().strftime("%Y-%m-%d")
        
        # Check which button was clicked
        ctx = callback_context
        if ctx.triggered:
            triggered_id = ctx.triggered[0]['prop_id']
            
            # If a generate prediction button was clicked
            if 'generate-prediction-btn' in triggered_id:
                try:
                    # Extract schedule_id from the triggered component
                    import json
                    triggered_dict = json.loads(triggered_id.split('.')[0])
                    schedule_id = triggered_dict['index']
                    
                    logger.info(f"Generating prediction for schedule {schedule_id} on {schedule_date}")
                    
                    # Call the simplified prediction API
                    prediction_response = make_api_request(
                        "/api/ai/predict-simple",
                        token=token,
                        method="POST",
                        data={
                            "schedule_id": schedule_id,
                            "prediction_date": schedule_date
                        },
                        timeout=120  # AI predictions can take 60-90 seconds
                    )
                    
                    if prediction_response and "error" not in prediction_response:
                        logger.info(f"✓ Prediction generated successfully!")
                        # Continue to reload schedules below to show the new prediction
                    else:
                        error_msg = prediction_response.get('message', 'Failed to generate prediction') if prediction_response else 'Server connection error'
                        logger.error(f"Error generating prediction: {error_msg}")
                        # Return error to user
                        return (
                            html.Div("Failed to generate prediction", style={'padding': '20px', 'textAlign': 'center'}),
                            "0",
                            f"Error: {error_msg}",
                            True,
                            "danger"
                        )
                        
                except Exception as e:
                    logger.error(f"Error generating prediction: {e}", exc_info=True)
                    return (
                        html.Div("Failed to generate prediction", style={'padding': '20px', 'textAlign': 'center'}),
                        "0",
                        f"Error: {str(e)}",
                        True,
                        "danger"
                    )
        
        try:
            # Fetch schedules from API
            response = make_api_request(
                f"/daily-schedules?schedule_date={schedule_date}",
                token=token,
                timeout=30  # Increased timeout for prediction queries
            )
            
            if not response:
                return (
                    html.Div("Failed to connect to server", style={'padding': '20px', 'textAlign': 'center'}),
                    "0",
                    "Error: Could not connect to the backend server",
                    True,
                    "danger"
                )
            
            if "error" in response:
                return (
                    html.Div("Failed to load schedules", style={'padding': '20px', 'textAlign': 'center'}),
                    "0",
                    f"Error: {response.get('message', 'Unknown error')}",
                    True,
                    "danger"
                )
            
            schedules = response.get("schedules", [])
            date_info = response.get("date", schedule_date)
            day_of_week = response.get("day_of_week", "")
            is_poya = response.get("is_poya_day", False)
            is_holiday = response.get("is_holiday", False)
            
            if not schedules:
                return (
                    html.Div([
                        html.I(className="fas fa-calendar-times", style={
                            'fontSize': '64px',
                            'color': COLORS['text_secondary'],
                            'marginBottom': '16px'
                        }),
                        html.H5("No schedules found for this date", style={
                            'color': COLORS['text_secondary']
                        })
                    ], style={'padding': '60px', 'textAlign': 'center'}),
                    "0",
                    "",
                    False,
                    "info"
                )
            
            # Build schedule cards with predictions
            schedule_cards = []
            for schedule in schedules:
                prediction = schedule.get("prediction")
                has_prediction = prediction is not None
                
                # Build prediction display
                if has_prediction:
                    pred_content = html.Div([
                        html.Div([
                            html.I(className="fas fa-robot", style={
                                'marginRight': '8px',
                                'color': COLORS['info']
                            }),
                            html.Strong("AI Prediction", style={'color': COLORS['info']})
                        ], style={'marginBottom': '12px', 'fontSize': '15px'}),
                        
                        # Compartment allocation
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Div("1st Class", style={
                                        'fontSize': '12px',
                                        'color': COLORS['text_secondary'],
                                        'marginBottom': '4px'
                                    }),
                                    html.Div([
                                        html.I(className="fas fa-train", style={
                                            'marginRight': '6px',
                                            'color': COLORS['primary']
                                        }),
                                        html.Strong(f"{prediction['predicted_first_class']}", style={
                                            'fontSize': '20px',
                                            'color': COLORS['primary']
                                        })
                                    ])
                                ], style={
                                    'padding': '12px',
                                    'background': '#fef2f2',
                                    'borderRadius': '8px',
                                    'textAlign': 'center'
                                })
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.Div("2nd Class", style={
                                        'fontSize': '12px',
                                        'color': COLORS['text_secondary'],
                                        'marginBottom': '4px'
                                    }),
                                    html.Div([
                                        html.I(className="fas fa-train", style={
                                            'marginRight': '6px',
                                            'color': COLORS['success']
                                        }),
                                        html.Strong(f"{prediction['predicted_second_class']}", style={
                                            'fontSize': '20px',
                                            'color': COLORS['success']
                                        })
                                    ])
                                ], style={
                                    'padding': '12px',
                                    'background': '#f0fdf4',
                                    'borderRadius': '8px',
                                    'textAlign': 'center'
                                })
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.Div("3rd Class", style={
                                        'fontSize': '12px',
                                        'color': COLORS['text_secondary'],
                                        'marginBottom': '4px'
                                    }),
                                    html.Div([
                                        html.I(className="fas fa-train", style={
                                            'marginRight': '6px',
                                            'color': COLORS['info']
                                        }),
                                        html.Strong(f"{prediction['predicted_third_class']}", style={
                                            'fontSize': '20px',
                                            'color': COLORS['info']
                                        })
                                    ])
                                ], style={
                                    'padding': '12px',
                                    'background': '#eff6ff',
                                    'borderRadius': '8px',
                                    'textAlign': 'center'
                                })
                            ], width=4),
                        ], style={'marginBottom': '12px'}),
                        
                        # Expected passengers and confidence
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-users", style={'marginRight': '6px'}),
                                html.Span(f"Expected: {prediction.get('expected_total_passengers', 'N/A')} passengers", style={
                                    'fontSize': '13px',
                                    'marginRight': '16px'
                                })
                            ], style={'display': 'inline-block'}),
                            html.Div([
                                html.I(className="fas fa-chart-line", style={'marginRight': '6px'}),
                                html.Span(f"Confidence: {prediction.get('confidence_score', 0)*100:.0f}%", style={
                                    'fontSize': '13px'
                                })
                            ], style={'display': 'inline-block'})
                        ], style={'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                        
                        # Reasoning (collapsible)
                        html.Details([
                            html.Summary("View AI Reasoning", style={
                                'cursor': 'pointer',
                                'fontSize': '13px',
                                'color': COLORS['info'],
                                'fontWeight': '500'
                            }),
                            html.P(prediction.get('reasoning', 'No reasoning provided'), style={
                                'fontSize': '12px',
                                'color': COLORS['text_secondary'],
                                'marginTop': '8px',
                                'padding': '12px',
                                'background': '#f8f9fa',
                                'borderRadius': '6px',
                                'lineHeight': '1.6'
                            })
                        ], style={'marginTop': '8px'})
                    ], style={
                        'padding': '16px',
                        'background': '#f8f9fa',
                        'borderRadius': '12px',
                        'marginTop': '16px',
                        'border': f'2px solid {COLORS["info"]}33'
                    })
                else:
                    pred_content = html.Div([
                        html.Div([
                            html.I(className="fas fa-exclamation-circle", style={
                                'marginRight': '8px',
                                'color': COLORS['warning']
                            }),
                            html.Span("No AI prediction available for this schedule", style={
                                'fontSize': '13px',
                                'color': COLORS['text_secondary']
                            })
                        ], style={'marginBottom': '12px'}),
                        dbc.Button([
                            html.I(className="fas fa-magic", style={'marginRight': '8px'}),
                            html.Span("Generate AI Prediction", id={'type': 'btn-text', 'index': schedule['train_schedule_id']})
                        ], 
                        id={'type': 'generate-prediction-btn', 'index': schedule['train_schedule_id']},
                        color="primary", 
                        size="sm", 
                        outline=True,
                        disabled=False,
                        style={'cursor': 'pointer'})
                    ], style={
                        'padding': '16px',
                        'background': '#fffbeb',
                        'borderRadius': '12px',
                        'marginTop': '16px',
                        'border': f'1px solid {COLORS["warning"]}33'
                    })
                
                # Create schedule card
                card = html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.I(className="fas fa-train", style={
                                    'fontSize': '24px',
                                    'color': COLORS['primary'],
                                    'marginRight': '12px'
                                }),
                                html.Div([
                                    html.H5(schedule['train_schedule'], style={
                                        'margin': '0',
                                        'color': COLORS['text_primary'],
                                        'fontWeight': '600'
                                    }),
                                    html.P(f"{schedule['origin_station']} → {schedule['destination_station']}", style={
                                        'margin': '4px 0 0 0',
                                        'fontSize': '14px',
                                        'color': COLORS['text_secondary']
                                    })
                                ])
                            ], style={'display': 'flex', 'alignItems': 'center'})
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                html.I(className="fas fa-clock", style={'marginRight': '6px'}),
                                html.Span(f"{schedule['origin_departure']} - {schedule['destination_departure']}", style={
                                    'fontSize': '15px',
                                    'fontWeight': '500'
                                })
                            ], style={'textAlign': 'right', 'color': COLORS['text_primary']})
                        ], width=6)
                    ]),
                    
                    html.Hr(style={'margin': '16px 0', 'borderColor': COLORS['border']}),
                    
                    # Schedule details
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.I(className="fas fa-hashtag", style={'marginRight': '6px', 'color': COLORS['text_secondary']}),
                                html.Small(f"ID: {schedule['train_schedule_id']}", style={'color': COLORS['text_secondary']})
                            ])
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                html.I(className="fas fa-route", style={'marginRight': '6px', 'color': COLORS['text_secondary']}),
                                html.Small(f"Route: {schedule['route_id']}", style={'color': COLORS['text_secondary']})
                            ])
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                html.Span(schedule['status'], className=f"badge bg-{get_status_color(schedule['status'])}", style={
                                    'padding': '6px 12px',
                                    'fontSize': '12px',
                                    'fontWeight': '600'
                                })
                            ], style={'textAlign': 'right'})
                        ], width=4)
                    ]),
                    
                    # AI Prediction section
                    pred_content
                    
                ], style={
                    'background': COLORS['surface'],
                    'padding': '24px',
                    'borderRadius': '16px',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
                    'border': f'1px solid {COLORS["border"]}',
                    'marginBottom': '20px',
                    'transition': 'all 0.3s ease'
                }, className='schedule-card')
                
                schedule_cards.append(card)
            
            # Add date info header
            date_header = html.Div([
                html.H5(f"{day_of_week}, {date_info}", style={
                    'display': 'inline',
                    'marginRight': '12px',
                    'color': COLORS['text_primary']
                }),
                html.Span("🌙 Poya Day", style={
                    'padding': '4px 12px',
                    'background': COLORS['accent'],
                    'borderRadius': '8px',
                    'fontSize': '13px',
                    'marginRight': '8px',
                    'fontWeight': '600'
                }) if is_poya else None,
                html.Span("🎉 Public Holiday", style={
                    'padding': '4px 12px',
                    'background': COLORS['success'],
                    'color': 'white',
                    'borderRadius': '8px',
                    'fontSize': '13px',
                    'fontWeight': '600'
                }) if is_holiday else None
            ], style={'marginBottom': '24px'})
            
            return (
                html.Div([date_header] + schedule_cards),
                str(len(schedules)),
                f"Loaded {len(schedules)} schedules for {date_info}",
                True,
                "success"
            )
            
        except Exception as e:
            logger.error(f"Error loading daily schedules: {e}", exc_info=True)
            return (
                html.Div("An error occurred", style={'padding': '20px', 'textAlign': 'center'}),
                "0",
                f"Error: {str(e)}",
                True,
                "danger"
            )


def get_status_color(status):
    """Get Bootstrap color class for status"""
    status_colors = {
        "Active": "success",
        "Scheduled": "info",
        "In Progress": "primary",
        "Completed": "success",
        "Cancelled": "danger",
        "Delayed": "warning"
    }
    return status_colors.get(status, "secondary")
