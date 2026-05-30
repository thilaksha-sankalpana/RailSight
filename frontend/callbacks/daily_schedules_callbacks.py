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
    
    # Callback to populate route filter options with server-side loading
    @app.callback(
        Output("daily-schedule-route-filter", "options"),
        [Input("token-store", "data"),
         Input("daily-schedule-route-filter", "search_value")],
        prevent_initial_call=False
    )
    def populate_route_filter(token, search_value):
        """Fetch routes for the filter dropdown with server-side search"""
        if not token:
            return []
        
        try:
            # Use server-side search if user is typing
            if search_value and len(search_value) >= 2:
                response = make_api_request(f"/routes?search={search_value}&limit=20", token=token, timeout=10)
            else:
                # Load initial routes
                response = make_api_request("/routes?limit=50", token=token, timeout=10)
            
            if response and isinstance(response, list):
                routes = response
                return [
                    {
                        "label": f"{r.get('route_id', '')} - {r.get('route_name', r.get('route', 'Unknown'))}",
                        "value": r['route_id']
                    } 
                    for r in routes
                ]
            return []
        except Exception as e:
            logger.error(f"Error fetching routes: {e}")
            return []
    
    @app.callback(
        [Output("daily-schedules-container", "children"),
         Output("daily-schedule-count", "children"),
         Output("daily-schedule-alert", "children"),
         Output("daily-schedule-alert", "is_open"),
         Output("daily-schedule-alert", "color")],
        [Input("load-daily-schedules-btn", "n_clicks"),
         Input({'type': 'generate-prediction-btn', 'index': ALL}, 'n_clicks'),
         Input({'type': 'regenerate-prediction-btn', 'index': ALL}, 'n_clicks')],
        [State("daily-schedule-date", "value"),
         State("daily-schedule-route-filter", "value"),
         State("daily-schedule-id-filter", "value"),
         State("token-store", "data")],
        prevent_initial_call=False
    )
    def load_daily_schedules(n_clicks, generate_clicks, regenerate_clicks, schedule_date, route_filter, schedule_id_filter, token):
        """Load schedules for selected date with AI predictions and server-side filters"""
        if not token:
            return html.Div("Please log in to view schedules"), "0", "", False, "warning"
        
        # Use today's date if none selected
        if not schedule_date:
            schedule_date = datetime.now().strftime("%Y-%m-%d")
        
        # Check which button was clicked
        ctx = callback_context
        prediction_cached = False
        if ctx.triggered:
            triggered_id = ctx.triggered[0]['prop_id']
            
            # If a regenerate prediction button was clicked
            if 'regenerate-prediction-btn' in triggered_id:
                try:
                    import json
                    from time import sleep
                    triggered_dict = json.loads(triggered_id.split('.')[0])
                    schedule_id = triggered_dict['index']
                    
                    prediction_response = make_api_request(
                        "/api/ai/predict-simple",
                        token=token,
                        method="POST",
                        data={
                            "schedule_id": schedule_id,
                            "prediction_date": schedule_date,
                            "force_regenerate": True
                        },
                        timeout=120
                    )
                    
                    if prediction_response and "error" not in prediction_response:
                        sleep(0.5)  # Ensure database commit completes
                    else:
                        error_msg = prediction_response.get('message', 'Failed to regenerate prediction') if prediction_response else 'Server connection error'
                        return (
                            html.Div("Failed to regenerate prediction", style={'padding': '20px', 'textAlign': 'center'}),
                            "0",
                            f"Error: {error_msg}",
                            True,
                            "danger"
                        )
                        
                except Exception as e:
                    logger.error(f"Error regenerating prediction: {e}")
                    return (
                        html.Div("Failed to regenerate prediction", style={'padding': '20px', 'textAlign': 'center'}),
                        "0",
                        f"Error: {str(e)}",
                        True,
                        "danger"
                    )
            
            # If a generate prediction button was clicked
            elif 'generate-prediction-btn' in triggered_id:
                try:
                    import json
                    from time import sleep
                    triggered_dict = json.loads(triggered_id.split('.')[0])
                    schedule_id = triggered_dict['index']
                    
                    prediction_response = make_api_request(
                        "/api/ai/predict-simple",
                        token=token,
                        method="POST",
                        data={
                            "schedule_id": schedule_id,
                            "prediction_date": schedule_date
                        },
                        timeout=120
                    )
                    
                    if prediction_response and "error" not in prediction_response:
                        prediction_cached = prediction_response.get('cached', False)
                        if not prediction_cached:
                            sleep(0.5)  # Ensure database commit completes for new predictions
                    else:
                        error_msg = prediction_response.get('message', 'Failed to generate prediction') if prediction_response else 'Server connection error'
                        return (
                            html.Div("Failed to generate prediction", style={'padding': '20px', 'textAlign': 'center'}),
                            "0",
                            f"Error: {error_msg}",
                            True,
                            "danger"
                        )
                        
                except Exception as e:
                    logger.error(f"Error generating prediction: {e}")
                    return (
                        html.Div("Failed to generate prediction", style={'padding': '20px', 'textAlign': 'center'}),
                        "0",
                        f"Error: {str(e)}",
                        True,
                        "danger"
                    )
        
        try:
            # Build API URL with server-side filters
            api_url = f"/daily-schedules?schedule_date={schedule_date}"
            if route_filter:
                api_url += f"&route_id={route_filter}"
            if schedule_id_filter and schedule_id_filter.strip():
                api_url += f"&schedule_id={schedule_id_filter.strip()}"
            
            response = make_api_request(api_url, token=token, timeout=30)
            
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
                # Determine message based on filters
                if route_filter or schedule_id_filter:
                    empty_message = "No schedules match your filters"
                    empty_submessage = "Try adjusting your filter criteria"
                else:
                    empty_message = "No schedules found for this date"
                    empty_submessage = "There are no running trains on this date"
                
                return (
                    html.Div([
                        html.I(className="fas fa-calendar-times", style={
                            'fontSize': '64px',
                            'color': COLORS['text_secondary'],
                            'marginBottom': '16px'
                        }),
                        html.H5(empty_message, style={
                            'color': COLORS['text_secondary']
                        }),
                        html.P(empty_submessage, style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px'
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
                            html.Div([
                                html.I(className="fas fa-brain", style={
                                    'marginRight': '10px',
                                    'color': COLORS['info'],
                                    'fontSize': '18px'
                                }),
                                html.Strong("AI-Powered Capacity Prediction", style={
                                    'color': COLORS['info'],
                                    'fontSize': '16px',
                                    'fontWeight': '700'
                                })
                            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '16px'}),
                        ]),
                        
                        # Compartment allocation with enhanced design
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-crown", style={
                                            'fontSize': '14px',
                                            'color': '#dc2626',
                                            'marginRight': '6px'
                                        }),
                                        html.Span("First Class", style={
                                            'fontSize': '12px',
                                            'fontWeight': '600',
                                            'color': COLORS['text_secondary'],
                                            'textTransform': 'uppercase',
                                            'letterSpacing': '0.5px'
                                        })
                                    ], style={'marginBottom': '8px'}),
                                    html.Div([
                                        html.I(className="fas fa-train", style={
                                            'marginRight': '8px',
                                            'color': '#dc2626',
                                            'fontSize': '16px'
                                        }),
                                        html.Strong(f"{prediction['predicted_first_class']}", style={
                                            'fontSize': '28px',
                                            'color': '#dc2626',
                                            'fontWeight': '800'
                                        }),
                                        html.Span(" cars", style={
                                            'fontSize': '14px',
                                            'color': COLORS['text_secondary'],
                                            'marginLeft': '4px'
                                        })
                                    ])
                                ], style={
                                    'padding': '16px',
                                    'background': 'linear-gradient(135deg, #fef2f2, #ffffff)',
                                    'borderRadius': '12px',
                                    'textAlign': 'center',
                                    'border': '2px solid #fecaca',
                                    'boxShadow': '0 2px 8px rgba(220, 38, 38, 0.15)'
                                })
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-star", style={
                                            'fontSize': '14px',
                                            'color': '#16a34a',
                                            'marginRight': '6px'
                                        }),
                                        html.Span("Second Class", style={
                                            'fontSize': '12px',
                                            'fontWeight': '600',
                                            'color': COLORS['text_secondary'],
                                            'textTransform': 'uppercase',
                                            'letterSpacing': '0.5px'
                                        })
                                    ], style={'marginBottom': '8px'}),
                                    html.Div([
                                        html.I(className="fas fa-train", style={
                                            'marginRight': '8px',
                                            'color': '#16a34a',
                                            'fontSize': '16px'
                                        }),
                                        html.Strong(f"{prediction['predicted_second_class']}", style={
                                            'fontSize': '28px',
                                            'color': '#16a34a',
                                            'fontWeight': '800'
                                        }),
                                        html.Span(" cars", style={
                                            'fontSize': '14px',
                                            'color': COLORS['text_secondary'],
                                            'marginLeft': '4px'
                                        })
                                    ])
                                ], style={
                                    'padding': '16px',
                                    'background': 'linear-gradient(135deg, #f0fdf4, #ffffff)',
                                    'borderRadius': '12px',
                                    'textAlign': 'center',
                                    'border': '2px solid #bbf7d0',
                                    'boxShadow': '0 2px 8px rgba(22, 163, 74, 0.15)'
                                })
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-users", style={
                                            'fontSize': '14px',
                                            'color': '#2563eb',
                                            'marginRight': '6px'
                                        }),
                                        html.Span("Third Class", style={
                                            'fontSize': '12px',
                                            'fontWeight': '600',
                                            'color': COLORS['text_secondary'],
                                            'textTransform': 'uppercase',
                                            'letterSpacing': '0.5px'
                                        })
                                    ], style={'marginBottom': '8px'}),
                                    html.Div([
                                        html.I(className="fas fa-train", style={
                                            'marginRight': '8px',
                                            'color': '#2563eb',
                                            'fontSize': '16px'
                                        }),
                                        html.Strong(f"{prediction['predicted_third_class']}", style={
                                            'fontSize': '28px',
                                            'color': '#2563eb',
                                            'fontWeight': '800'
                                        }),
                                        html.Span(" cars", style={
                                            'fontSize': '14px',
                                            'color': COLORS['text_secondary'],
                                            'marginLeft': '4px'
                                        })
                                    ])
                                ], style={
                                    'padding': '16px',
                                    'background': 'linear-gradient(135deg, #eff6ff, #ffffff)',
                                    'borderRadius': '12px',
                                    'textAlign': 'center',
                                    'border': '2px solid #bfdbfe',
                                    'boxShadow': '0 2px 8px rgba(37, 99, 235, 0.15)'
                                })
                            ], width=4),
                        ], style={'marginBottom': '16px'}),
                        
                        # Enhanced metrics display
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-user-friends", style={
                                            'marginRight': '8px',
                                            'color': COLORS['primary'],
                                            'fontSize': '16px'
                                        }),
                                        html.Span("Expected Passengers:", style={
                                            'fontSize': '13px',
                                            'color': COLORS['text_secondary'],
                                            'marginRight': '6px',
                                            'fontWeight': '500'
                                        }),
                                        html.Strong(f"{prediction.get('expected_total_passengers', 'N/A')}", style={
                                            'fontSize': '15px',
                                            'color': COLORS['text_primary'],
                                            'fontWeight': '700'
                                        })
                                    ], style={'display': 'flex', 'alignItems': 'center'})
                                ], md=6),
                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-chart-line", style={
                                            'marginRight': '8px',
                                            'color': COLORS['success'],
                                            'fontSize': '16px'
                                        }),
                                        html.Span("Confidence Score:", style={
                                            'fontSize': '13px',
                                            'color': COLORS['text_secondary'],
                                            'marginRight': '6px',
                                            'fontWeight': '500'
                                        }),
                                        html.Strong(f"{prediction.get('confidence_score', 0)*100:.0f}%", style={
                                            'fontSize': '15px',
                                            'color': COLORS['success'],
                                            'fontWeight': '700'
                                        })
                                    ], style={'display': 'flex', 'alignItems': 'center'})
                                ], md=6)
                            ])
                        ], style={
                            'padding': '14px 16px',
                            'background': '#f8fafc',
                            'borderRadius': '10px',
                            'marginBottom': '12px',
                            'border': '1px solid #e2e8f0'
                        }),
                        
                        # AI Reasoning section
                        html.Details([
                            html.Summary([
                                html.I(className="fas fa-lightbulb", style={'marginRight': '8px'}),
                                "View AI Reasoning & Analysis"
                            ], style={
                                'cursor': 'pointer',
                                'fontSize': '14px',
                                'color': COLORS['info'],
                                'fontWeight': '600',
                                'padding': '10px',
                                'borderRadius': '8px',
                                'background': '#f0f9ff',
                                'border': '1px solid #bfdbfe'
                            }),
                            html.Div([
                                html.P(prediction.get('reasoning', 'No reasoning provided'), style={
                                    'fontSize': '13px',
                                    'color': COLORS['text_secondary'],
                                    'margin': '0',
                                    'lineHeight': '1.7'
                                })
                            ], style={
                                'marginTop': '12px',
                                'padding': '16px',
                                'background': '#ffffff',
                                'borderRadius': '8px',
                                'border': '1px solid #e5e7eb'
                            })
                        ], style={'marginBottom': '16px'}),
                        
                        # Regenerate button
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-sync-alt", style={'marginRight': '10px'}),
                                "Regenerate Prediction"
                            ], 
                            id={'type': 'regenerate-prediction-btn', 'index': schedule['train_schedule_id']},
                            color="warning", 
                            size="sm", 
                            outline=True,
                            style={
                                'fontSize': '13px',
                                'fontWeight': '600',
                                'padding': '8px 16px',
                                'borderRadius': '8px',
                                'borderWidth': '2px'
                            })
                        ])
                    ], style={
                        'padding': '20px',
                        'background': 'linear-gradient(to bottom, #fafbfc, #ffffff)',
                        'borderRadius': '14px',
                        'marginTop': '20px',
                        'border': f'2px solid {COLORS["info"]}30',
                        'boxShadow': '0 4px 12px rgba(0,0,0,0.06)'
                    })
                else:
                    pred_content = html.Div([
                        html.Div([
                            html.I(className="fas fa-robot", style={
                                'fontSize': '32px',
                                'color': COLORS['warning'],
                                'marginBottom': '12px'
                            }),
                            html.H6("No AI Prediction Available", style={
                                'color': COLORS['text_primary'],
                                'fontWeight': '700',
                                'marginBottom': '8px'
                            }),
                            html.P("Generate an AI-powered prediction to optimize compartment allocation based on historical data and demand patterns.", style={
                                'fontSize': '13px',
                                'color': COLORS['text_secondary'],
                                'marginBottom': '16px',
                                'lineHeight': '1.6'
                            })
                        ], style={'textAlign': 'center', 'marginBottom': '16px'}),
                        dbc.Button([
                            html.I(className="fas fa-magic", style={'marginRight': '10px'}),
                            html.Span("Generate AI Prediction Now", id={'type': 'btn-text', 'index': schedule['train_schedule_id']})
                        ], 
                        id={'type': 'generate-prediction-btn', 'index': schedule['train_schedule_id']},
                        color="primary", 
                        size="md",
                        style={
                            'width': '100%',
                            'padding': '12px 24px',
                            'fontWeight': '700',
                            'fontSize': '14px',
                            'borderRadius': '10px',
                            'boxShadow': f'0 4px 12px {COLORS["primary"]}30'
                        })
                    ], style={
                        'padding': '24px',
                        'background': 'linear-gradient(135deg, #fffbeb, #ffffff)',
                        'borderRadius': '14px',
                        'marginTop': '20px',
                        'border': f'2px dashed {COLORS["warning"]}80',
                        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)'
                    })
                
                # Create enhanced schedule card
                card = html.Div([
                    # Card Header
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-train", style={
                                            'fontSize': '20px',
                                            'color': 'white'
                                        }),
                                    ], style={
                                        'width': '48px',
                                        'height': '48px',
                                        'background': f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary"]}dd)',
                                        'borderRadius': '12px',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'marginRight': '16px',
                                        'boxShadow': f'0 4px 12px {COLORS["primary"]}40'
                                    }),
                                    html.Div([
                                        html.H5(schedule['train_schedule'], style={
                                            'margin': '0 0 4px 0',
                                            'color': COLORS['text_primary'],
                                            'fontWeight': '800',
                                            'fontSize': '18px'
                                        }),
                                        html.Div([
                                            html.I(className="fas fa-map-marked-alt", style={
                                                'fontSize': '12px',
                                                'marginRight': '6px',
                                                'color': COLORS['text_secondary']
                                            }),
                                            html.Span(f"{schedule['origin_station']}", style={
                                                'fontSize': '14px',
                                                'color': COLORS['text_secondary'],
                                                'fontWeight': '600'
                                            }),
                                            html.I(className="fas fa-arrow-right", style={
                                                'fontSize': '11px',
                                                'margin': '0 8px',
                                                'color': COLORS['primary']
                                            }),
                                            html.Span(f"{schedule['destination_station']}", style={
                                                'fontSize': '14px',
                                                'color': COLORS['text_secondary'],
                                                'fontWeight': '600'
                                            })
                                        ])
                                    ])
                                ], style={'display': 'flex', 'alignItems': 'center'})
                            ], md=7),
                            dbc.Col([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-clock", style={
                                            'marginRight': '8px',
                                            'color': COLORS['primary'],
                                            'fontSize': '16px'
                                        }),
                                        html.Span("Departure", style={
                                            'fontSize': '11px',
                                            'color': COLORS['text_secondary'],
                                            'fontWeight': '600',
                                            'textTransform': 'uppercase',
                                            'letterSpacing': '0.5px',
                                            'display': 'block'
                                        }),
                                        html.Strong(f"{schedule['origin_departure']}", style={
                                            'fontSize': '20px',
                                            'fontWeight': '800',
                                            'color': COLORS['text_primary'],
                                            'display': 'block',
                                            'marginTop': '4px'
                                        })
                                    ], style={'textAlign': 'center', 'marginRight': '20px'}),
                                    html.Div([
                                        html.I(className="fas fa-arrow-right", style={
                                            'color': COLORS['text_secondary'],
                                            'fontSize': '14px'
                                        })
                                    ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'}),
                                    html.Div([
                                        html.I(className="fas fa-flag-checkered", style={
                                            'marginRight': '8px',
                                            'color': COLORS['success'],
                                            'fontSize': '16px'
                                        }),
                                        html.Span("Arrival", style={
                                            'fontSize': '11px',
                                            'color': COLORS['text_secondary'],
                                            'fontWeight': '600',
                                            'textTransform': 'uppercase',
                                            'letterSpacing': '0.5px',
                                            'display': 'block'
                                        }),
                                        html.Strong(f"{schedule['destination_departure']}", style={
                                            'fontSize': '20px',
                                            'fontWeight': '800',
                                            'color': COLORS['text_primary'],
                                            'display': 'block',
                                            'marginTop': '4px'
                                        })
                                    ], style={'textAlign': 'center'})
                                ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'flex-end'})
                            ], md=5)
                        ])
                    ], style={
                        'padding': '20px 24px',
                        'background': 'linear-gradient(to bottom, #fafbfc, #ffffff)',
                        'borderBottom': f'2px solid {COLORS["border"]}'
                    }),
                    
                    # Card Body - Metadata
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-fingerprint", style={
                                        'marginRight': '8px',
                                        'color': COLORS['text_secondary'],
                                        'fontSize': '14px'
                                    }),
                                    html.Span("Schedule ID:", style={
                                        'fontSize': '12px',
                                        'color': COLORS['text_secondary'],
                                        'marginRight': '6px',
                                        'fontWeight': '500'
                                    }),
                                    html.Strong(schedule['train_schedule_id'], style={
                                        'fontSize': '13px',
                                        'color': COLORS['text_primary'],
                                        'fontWeight': '700'
                                    })
                                ])
                            ], md=4),
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-route", style={
                                        'marginRight': '8px',
                                        'color': COLORS['text_secondary'],
                                        'fontSize': '14px'
                                    }),
                                    html.Span("Route:", style={
                                        'fontSize': '12px',
                                        'color': COLORS['text_secondary'],
                                        'marginRight': '6px',
                                        'fontWeight': '500'
                                    }),
                                    html.Strong(schedule['route_id'], style={
                                        'fontSize': '13px',
                                        'color': COLORS['text_primary'],
                                        'fontWeight': '700'
                                    })
                                ])
                            ], md=4),
                            dbc.Col([
                                html.Div([
                                    html.Span(schedule['status'], className=f"badge bg-{get_status_color(schedule['status'])}", style={
                                        'padding': '8px 16px',
                                        'fontSize': '13px',
                                        'fontWeight': '700',
                                        'borderRadius': '20px',
                                        'letterSpacing': '0.5px'
                                    })
                                ], style={'textAlign': 'right'})
                            ], md=4)
                        ])
                    ], style={
                        'padding': '16px 24px',
                        'background': '#ffffff'
                    }),
                    
                    # AI Prediction section
                    pred_content
                    
                ], style={
                    'background': COLORS['surface'],
                    'borderRadius': '16px',
                    'boxShadow': '0 6px 20px rgba(0,0,0,0.1)',
                    'border': f'1px solid {COLORS["border"]}',
                    'marginBottom': '24px',
                    'transition': 'all 0.3s ease',
                    'overflow': 'hidden'
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
            
            # Build alert message
            alert_message = f"Loaded {len(schedules)} schedule{'s' if len(schedules) != 1 else ''} for {date_info}"
            if route_filter or schedule_id_filter:
                alert_message += " (filtered)"
            
            # Check what triggered the callback
            if ctx.triggered and ctx.triggered[0]['prop_id']:
                if 'regenerate-prediction-btn' in ctx.triggered[0]['prop_id']:
                    alert_message += " - Prediction regenerated successfully!"
                elif 'generate-prediction-btn' in ctx.triggered[0]['prop_id']:
                    if prediction_cached:
                        alert_message += " - Using existing prediction"
                    else:
                        alert_message += " - New prediction generated!"
            
            return (
                html.Div([date_header] + schedule_cards),
                str(len(schedules)),
                alert_message,
                True,
                "success"
            )
            
        except Exception as e:
            logger.error(f"Error loading daily schedules: {e}")
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
