"""
TCDAFS - Train Models Management Page
Manage railway train models, specifications, and route assignments
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.common.topbar import create_topbar
from config.styles import COLORS


def train_models_layout():
    """
    Create train models management page with filters, table, and CRUD modals

    Returns:
        Dash HTML component for the train models page
    """
    return html.Div([
        create_topbar(),
        html.Div([
            # Enhanced Header with Gradient Background
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-train", style={
                            'fontSize': '36px',
                            'color': 'white'
                        })
                    ], style={
                        'width': '70px',
                        'height': '70px',
                        'borderRadius': '12px',
                        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["primary_dark"]} 100%)',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'marginRight': '16px',
                        'boxShadow': '0 4px 12px rgba(196, 30, 58, 0.25)'
                    }),
                    html.Div([
                        html.H3("Train Model Configuration", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '28px',
                            'letterSpacing': '-0.5px'
                        }),
                        html.P([
                            html.I(className="fas fa-info-circle", style={'marginRight': '8px', 'fontSize': '13px'}),
                            "Configure train specifications, capacity parameters, and route assignments for optimal fleet management"
                        ], style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'margin': '8px 0 0 0',
                            'lineHeight': '1.5'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'}),
                dbc.Button([
                    html.I(className="fas fa-plus-circle", style={'marginRight': '8px'}),
                    "Add Train Model"
                ], id="add-train-model-btn", color="primary", size="lg", style={
                    'boxShadow': '0 4px 12px rgba(196, 30, 58, 0.3)',
                    'fontWeight': '600',
                    'padding': '12px 24px'
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'background': f'linear-gradient(135deg, {COLORS["surface"]} 0%, #f8f9fa 100%)',
                'padding': '24px 28px',
                'marginBottom': '24px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Alert for CRUD operations
            dbc.Alert(id="train-model-alert", is_open=False, duration=4000, dismissable=True,
                     style={'marginBottom': '20px'}),

            # Enhanced Filter Section with Modern Design
            html.Div([
                # Filter Header
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-filter", style={
                                'marginRight': '12px',
                                'color': COLORS['primary'],
                                'fontSize': '18px'
                            }),
                            html.H5("Advanced Filtering", style={
                                'margin': '0',
                                'fontWeight': '600',
                                'fontSize': '18px',
                                'color': COLORS['text_primary']
                            })
                        ], style={'display': 'flex', 'alignItems': 'center'}),
                        html.P("Narrow down results by model specifications, type, manufacturer, or assigned routes", style={
                            'margin': '6px 0 0 0',
                            'color': COLORS['text_secondary'],
                            'fontSize': '13px'
                        })
                    ])
                ], style={
                    'padding': '20px 24px',
                    'borderBottom': f'1px solid {COLORS["border"]}',
                    'background': '#fafbfc'
                }),

                # Filter Controls
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-tag", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Model Name"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-name",
                                placeholder="All train models",
                                clearable=True,
                                searchable=True,
                                style={'fontSize': '14px'}
                            ),
                        ], md=3),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-subway", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Model Type"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-type",
                                placeholder="All types",
                                clearable=True,
                                searchable=True,
                                style={'fontSize': '14px'}
                            ),
                        ], md=3),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-globe", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Country"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-country",
                                placeholder="All countries",
                                clearable=True,
                                searchable=True,
                                style={'fontSize': '14px'}
                            ),
                        ], md=3),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-industry", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Manufacturer"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-manufacturer",
                                placeholder="All manufacturers",
                                clearable=True,
                                searchable=True,
                                style={'fontSize': '14px'}
                            ),
                        ], md=3),
                    ], className="mb-3"),

                    # Second Row: Routes and Action Buttons
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-route", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Assigned Routes"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-routes",
                                placeholder="All routes",
                                clearable=True,
                                searchable=True,
                                style={'fontSize': '14px'}
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("\u00A0", style={'marginBottom': '8px'}),
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '8px'}),
                                "Apply Filters"
                            ], id="apply-train-model-filter", color="primary", className="w-100"),
                        ], md=3),
                        dbc.Col([
                            dbc.Label("\u00A0", style={'marginBottom': '8px'}),
                            dbc.Button([
                                html.I(className="fas fa-times-circle", style={'marginRight': '8px'}),
                                "Clear All"
                            ], id="clear-train-model-filters", color="secondary", outline=True, className="w-100"),
                        ], md=3),
                    ])
                ], style={'padding': '24px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '24px'
            }),

            # Enhanced Train Models Table with Modern Card Design
            html.Div([
                # Table Header
                html.Div([
                    html.Div([
                        html.I(className="fas fa-table", style={
                            'marginRight': '10px',
                            'color': COLORS['primary'],
                            'fontSize': '18px'
                        }),
                        html.H5("Fleet Model Inventory", style={
                            'margin': '0',
                            'fontWeight': '600',
                            'fontSize': '18px',
                            'color': COLORS['text_primary']
                        }),
                        html.Div(id="train-models-count", style={
                            'marginLeft': '12px',
                            'padding': '4px 12px',
                            'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["primary_dark"]} 100%)',
                            'color': 'white',
                            'borderRadius': '12px',
                            'fontSize': '12px',
                            'fontWeight': '600'
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.Span([
                        html.I(className="fas fa-edit", style={
                            'marginRight': '6px',
                            'color': COLORS['info'],
                            'fontSize': '12px'
                        }),
                        "Use action buttons to edit or remove models"
                    ], style={'fontSize': '13px', 'color': COLORS['text_secondary']})
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'padding': '20px 24px',
                    'borderBottom': f'1px solid {COLORS["border"]}',
                    'background': '#fafbfc'
                }),

                # Table Content
                html.Div(id="train-models-table", style={
                    'padding': '20px',
                    'minHeight': '400px',
                    'background': COLORS['surface']
                })
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Enhanced Add/Edit Modal with Modern Design
            dbc.Modal([
                dbc.ModalHeader([
                    html.I(className="fas fa-train", style={
                        'fontSize': '20px',
                        'color': COLORS['primary'],
                        'marginRight': '10px'
                    }),
                    dbc.ModalTitle(id="train-model-modal-title", style={
                        'fontSize': '20px',
                        'fontWeight': '600'
                    })
                ], style={
                    'borderBottom': f'1px solid {COLORS["border"]}',
                    'padding': '20px 24px',
                    'background': '#fafbfc'
                }),
                dbc.ModalBody([
                    # Basic Information Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                            "Model Identification & Specifications"
                        ], style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px', 'fontSize': '16px'}),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Model ID *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-id", type="text", placeholder="e.g., S12EXP", maxLength=10, style={'fontSize': '14px'}),
                                html.Small("Unique identifier (A-Z, 0-9, max 10 characters)", className="text-muted", style={'fontSize': '12px'})
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Model Name *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-name", type="text", placeholder="e.g., S12 Express", style={'fontSize': '14px'})
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Model Type *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-type", type="text", placeholder="e.g., EMU, DMU, Locomotive", style={'fontSize': '14px'})
                            ], md=4),
                        ], className="mb-3"),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Manufacturer *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-manufacturer", type="text", placeholder="e.g., CRRC, Alstom, Siemens", style={'fontSize': '14px'})
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Country of Origin *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-country", type="text", placeholder="e.g., China, France, Germany", style={'fontSize': '14px'})
                            ], md=6),
                        ]),
                    ], style={
                        'padding': '20px',
                        'background': '#f8f9fa',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'border': f'1px solid {COLORS["border"]}'
                    }),

                    # Capacity Information Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-users", style={'marginRight': '8px'}),
                            "Operational Capacity Configuration"
                        ], style={'color': COLORS['info'], 'fontWeight': '600', 'marginBottom': '12px', 'fontSize': '16px'}),
                        html.P("Define the capacity and compartment structure for this train model",
                               style={'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '16px', 'marginTop': '-8px'}),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Operational Units *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-operational-units", type="number", placeholder="Number of units", min=0, style={'fontSize': '14px'}),
                                html.Small("Available train units of this model", className="text-muted", style={'fontSize': '11px'})
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Compartments per Unit *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-compartments-unit", type="number", placeholder="Compartments", min=1, style={'fontSize': '14px'}),
                                html.Small("Compartments in each unit", className="text-muted", style={'fontSize': '11px'})
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Total Compartments Assigned *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-total-compartments", type="number", placeholder="Total", min=0, style={'fontSize': '14px'}),
                                html.Small("Total compartments across all units", className="text-muted", style={'fontSize': '11px'})
                            ], md=4),
                        ], className="mb-3"),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Seating Capacity per Compartment *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-seating-capacity", type="number", placeholder="Seats", min=0, style={'fontSize': '14px'}),
                                html.Small("Number of seats per compartment", className="text-muted", style={'fontSize': '11px'})
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Standing Capacity per Compartment *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-standing-capacity", type="number", placeholder="Standing", min=0, style={'fontSize': '14px'}),
                                html.Small("Standing passengers per compartment", className="text-muted", style={'fontSize': '11px'})
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Total Passengers per Compartment *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px', 'color': COLORS['text_primary']}),
                                dbc.Input(id="train-model-total-capacity", type="number", placeholder="Total", min=0, style={'fontSize': '14px'}),
                                html.Small("Maximum passengers per compartment", className="text-muted", style={'fontSize': '11px'})
                            ], md=4),
                        ]),
                    ], style={
                        'padding': '20px',
                        'background': '#f0f8ff',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'border': f'1px solid {COLORS["border"]}'
                    }),

                    # Route Assignments Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-route", style={'marginRight': '8px'}),
                            "Route Assignment Configuration"
                        ], style={'color': COLORS['success'], 'fontWeight': '600', 'marginBottom': '12px', 'fontSize': '16px'}),
                        html.P("Select all railway routes where this train model is authorized to operate",
                               style={'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '16px', 'marginTop': '-8px'}),
                        dbc.Checklist(
                            id="train-model-routes",
                            options=[
                                {"label": "R01", "value": "r01"},
                                {"label": "R02", "value": "r02"},
                                {"label": "R03", "value": "r03"},
                                {"label": "R04", "value": "r04"},
                                {"label": "R05", "value": "r05"},
                                {"label": "R06", "value": "r06"},
                                {"label": "R07", "value": "r07"},
                                {"label": "R08", "value": "r08"},
                                {"label": "R09", "value": "r09"},
                            ],
                            value=[],
                            inline=True,
                            style={'fontSize': '14px'}
                        ),
                    ], style={
                        'padding': '20px',
                        'background': '#f0fff4',
                        'borderRadius': '8px',
                        'border': f'1px solid {COLORS["border"]}'
                    }),
                ], style={'padding': '24px'}),

                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-times", style={'marginRight': '8px'}),
                        "Cancel"
                    ], id="cancel-train-model-btn", color="secondary", outline=True, size="lg", style={
                        'padding': '10px 24px',
                        'fontWeight': '600'
                    }),
                    dbc.Button([
                        html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                        "Save Configuration"
                    ], id="save-train-model-btn", color="primary", size="lg", style={
                        'padding': '10px 24px',
                        'fontWeight': '600',
                        'boxShadow': '0 4px 12px rgba(196, 30, 58, 0.3)'
                    }),
                ], style={
                    'borderTop': f'1px solid {COLORS["border"]}',
                    'padding': '16px 24px',
                    'background': '#fafbfc'
                })
            ], id="train-model-modal", size="xl", is_open=False),

            # Delete Confirmation Modal
            dbc.Modal([
                dbc.ModalHeader(
                    dbc.ModalTitle([
                        html.I(className="fas fa-exclamation-triangle", style={'marginRight': '10px', 'color': COLORS['warning']}),
                        "Confirm Model Deletion"
                    ], style={'fontSize': '20px', 'fontWeight': '600'}),
                    style={'background': '#fff8f0', 'borderBottom': f'2px solid {COLORS["warning"]}'}
                ),
                dbc.ModalBody([
                    html.Div([
                        html.I(className="fas fa-exclamation-circle", style={
                            'fontSize': '56px',
                            'color': COLORS['error'],
                            'display': 'block',
                            'textAlign': 'center',
                            'marginBottom': '20px'
                        }),
                        html.H5("Are you sure you want to delete this train model?", style={
                            'textAlign': 'center',
                            'fontSize': '18px',
                            'marginBottom': '12px',
                            'fontWeight': '600',
                            'color': COLORS['text_primary']
                        }),
                        html.P("This action is permanent and cannot be reversed. All associated data will be removed from the system.", style={
                            'textAlign': 'center',
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'lineHeight': '1.6'
                        })
                    ], style={'padding': '20px'})
                ]),
                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-arrow-left", style={'marginRight': '8px'}),
                        "Keep Model"
                    ], id="cancel-delete-model-btn", color="secondary", outline=True, size="lg", style={
                        'padding': '10px 24px',
                        'fontWeight': '600'
                    }),
                    dbc.Button([
                        html.I(className="fas fa-trash-alt", style={'marginRight': '8px'}),
                        "Delete Permanently"
                    ], id="confirm-delete-model-btn", color="danger", size="lg", style={
                        'padding': '10px 24px',
                        'fontWeight': '600',
                        'boxShadow': '0 4px 12px rgba(239, 68, 68, 0.4)'
                    }),
                ], style={'background': '#fafbfc', 'padding': '16px 24px'})
            ], id="delete-confirm-modal", is_open=False, centered=True),

            # Hidden stores for state management
            dcc.Store(id="delete-model-id-store"),
            dcc.Store(id="train-model-refresh-trigger", data=0),
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
