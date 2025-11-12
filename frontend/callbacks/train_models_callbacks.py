"""
TCDAFS - Train Models Callbacks
Handle train models CRUD operations, filtering, and table display
"""
from dash import callback, Input, Output, State, html, no_update, dash, dash_table, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
import pandas as pd
import logging
import re
from utils.api import make_api_request
from config.styles import COLORS

logger = logging.getLogger(__name__)

# Constants
NO_UPDATE_15 = tuple([no_update] * 15)
ROUTE_COLS = ['r01', 'r02', 'r03', 'r04', 'r05', 'r06', 'r07', 'r08', 'r09']


def register(app):
    """Register train models callbacks with the app"""

    @callback(
        [Output("train-models-table", "children"),
         Output("train-models-count", "children")],
        [Input("url", "pathname"),
         Input("apply-train-model-filter", "n_clicks"),
         Input("train-model-refresh-trigger", "data")],
        [State("token-store", "data"),
         State("filter-train-model-name", "value"),
         State("filter-train-model-type", "value"),
         State("filter-train-model-country", "value"),
         State("filter-train-model-manufacturer", "value"),
         State("filter-train-model-routes", "value")]
    )
    def load_train_models(pathname, n_clicks, refresh_trigger, token, model_name_filter, model_type_filter,
                          country_filter, manufacturer_filter, routes_filter):
        """Load and display train models table with filtering"""
        if pathname != "/train-models" or not token:
            return html.P("Loading..."), "0 Models"

        train_models = make_api_request("/train-models", token=token)
        if not train_models:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-train", style={
                        'fontSize': '64px',
                        'color': COLORS['border'],
                        'marginBottom': '20px'
                    }),
                    html.H5("No Train Models Configured", style={
                        'color': COLORS['text_primary'],
                        'fontWeight': '600',
                        'marginBottom': '12px',
                        'fontSize': '20px'
                    }),
                    html.P("Start by adding your first train model to the fleet inventory. Click the 'Add Train Model' button above to begin.", style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '14px',
                        'lineHeight': '1.6',
                        'maxWidth': '400px',
                        'margin': '0 auto'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '60px 40px',
                    'background': '#fafbfc',
                    'borderRadius': '12px',
                    'border': f'2px dashed {COLORS["border"]}'
                })
            ], style={'padding': '40px'}), "0 Models"

        df = pd.DataFrame(train_models)

        # Apply filters
        if model_name_filter:
            df = df[df['model_name'] == model_name_filter]

        if model_type_filter:
            df = df[df['model_type'] == model_type_filter]

        if country_filter:
            df = df[df['country_of_origin'] == country_filter]

        if manufacturer_filter:
            df = df[df['manufacturer'] == manufacturer_filter]

        if routes_filter:
            # Filter by route boolean column (r01-r09)
            route_col = routes_filter.lower()  # e.g., 'R01' -> 'r01'
            if route_col in df.columns:
                df = df[df[route_col] == True]

        if df.empty:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-filter", style={
                        'fontSize': '56px',
                        'color': COLORS['border'],
                        'marginBottom': '20px'
                    }),
                    html.H5("No Matching Results", style={
                        'color': COLORS['text_primary'],
                        'fontWeight': '600',
                        'marginBottom': '12px',
                        'fontSize': '18px'
                    }),
                    html.P("No train models match your current filter criteria. Try adjusting your filters or clearing them to see all available models.", style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '14px',
                        'lineHeight': '1.6',
                        'maxWidth': '400px',
                        'margin': '0 auto'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '50px 40px',
                    'background': '#fafbfc',
                    'borderRadius': '12px',
                    'border': f'1px solid {COLORS["border"]}'
                })
            ], style={'padding': '40px'}), f"{len(train_models)} Models"

        # Create assigned routes column by combining r01-r09 boolean values
        df['assigned_routes_display'] = df.apply(
            lambda row: ', '.join([col.upper() for col in ROUTE_COLS if col in df.columns and row.get(col, False)]),
            axis=1
        )

        # Create table rows with action buttons
        table_rows = []
        for idx, row in df.iterrows():
            table_rows.append(html.Tr([
                html.Td(row.get('model_id', 'N/A'), style={'padding': '12px', 'fontSize': '13px'}),
                html.Td(row.get('model_name', 'N/A'), style={'padding': '12px', 'fontSize': '13px', 'fontWeight': '600'}),
                html.Td(row.get('model_type', 'N/A'), style={'padding': '12px', 'fontSize': '13px'}),
                html.Td(row.get('manufacturer', 'N/A'), style={'padding': '12px', 'fontSize': '13px'}),
                html.Td(row.get('country_of_origin', 'N/A'), style={'padding': '12px', 'fontSize': '13px'}),
                html.Td([
                    html.Span(route, style={
                        'display': 'inline-block',
                        'padding': '4px 8px',
                        'margin': '2px',
                        'background': f'linear-gradient(135deg, {COLORS["success"]} 0%, #45a049 100%)',
                        'color': 'white',
                        'borderRadius': '4px',
                        'fontSize': '11px',
                        'fontWeight': '600'
                    }) for route in (row.get('assigned_routes_display', '').split(', ') if row.get('assigned_routes_display') else [])
                ] if row.get('assigned_routes_display') else html.Span('-', style={'color': COLORS['text_secondary']}), style={'padding': '12px', 'fontSize': '13px'}),
                html.Td(str(row.get('operational_units', 0)), style={'padding': '12px', 'fontSize': '13px', 'textAlign': 'center'}),
                html.Td(str(row.get('compartments_per_unit', 0)), style={'padding': '12px', 'fontSize': '13px', 'textAlign': 'center'}),
                html.Td(str(row.get('total_compartments_assigned_per_model', 0)), style={'padding': '12px', 'fontSize': '13px', 'textAlign': 'center'}),
                html.Td([
                    html.Button([
                        html.I(className="fas fa-edit", style={'marginRight': '6px'}),
                        "Edit"
                    ], id={"type": "edit-train-model", "index": row.get('model_id')}, style={
                        'background': COLORS['info'],
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer',
                        'marginRight': '8px',
                        'fontSize': '13px',
                        'fontWeight': '500',
                        'transition': 'all 0.2s',
                        'boxShadow': '0 2px 4px rgba(33, 150, 243, 0.3)'
                    }, title="Edit configuration"),
                    html.Button([
                        html.I(className="fas fa-trash-alt", style={'marginRight': '6px'}),
                        "Remove"
                    ], id={"type": "delete-train-model", "index": row.get('model_id')}, style={
                        'background': COLORS['error'],
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 16px',
                        'borderRadius': '6px',
                        'cursor': 'pointer',
                        'fontSize': '13px',
                        'fontWeight': '500',
                        'transition': 'all 0.2s',
                        'boxShadow': '0 2px 4px rgba(244, 67, 54, 0.3)'
                    }, title="Remove from inventory")
                ], style={'padding': '12px', 'textAlign': 'center', 'whiteSpace': 'nowrap'})
            ], style={
                'borderBottom': f'1px solid {COLORS["border"]}',
                'transition': 'background 0.2s'
            }, className='table-row-hover'))

        return html.Div([
            html.Div([
                html.Table([
                    html.Thead(html.Tr([
                        html.Th('Model ID', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
                        html.Th('Model Name', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
                        html.Th('Type', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
                        html.Th('Manufacturer', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
                        html.Th('Country', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
                        html.Th('Assigned Routes', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
                        html.Th('Units', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px', 'textAlign': 'center'}),
                        html.Th('Comp/Unit', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px', 'textAlign': 'center'}),
                        html.Th('Total Comp', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px', 'textAlign': 'center'}),
                        html.Th('Actions', style={'padding': '14px 12px', 'fontSize': '13px', 'fontWeight': '700', 'textTransform': 'uppercase', 'letterSpacing': '0.5px', 'textAlign': 'center'})
                    ], style={
                        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, #9B1829 100%)',
                        'color': 'white'
                    })),
                    html.Tbody(table_rows)
                ], style={
                    'width': '100%',
                    'borderCollapse': 'separate',
                    'borderSpacing': '0',
                    'background': 'white',
                    'borderRadius': '8px',
                    'overflow': 'hidden',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                })
            ], style={'overflowX': 'auto'})
        ]), f"{len(df)} Models"

    @callback(
        Output("filter-train-model-name", "options"),
        Input("url", "pathname"),
        State("token-store", "data")
    )
    def populate_model_name_filter(pathname, token):
        """Populate model name filter dropdown"""
        if pathname != "/train-models" or not token:
            return []

        train_models = make_api_request("/train-models", token=token)
        if not train_models:
            return []

        # Get unique model names
        model_names = sorted(list(set([model['model_name'] for model in train_models if model.get('model_name')])))
        return [{"label": name, "value": name} for name in model_names]

    @callback(
        Output("filter-train-model-type", "options"),
        Input("url", "pathname"),
        State("token-store", "data")
    )
    def populate_model_type_filter(pathname, token):
        """Populate model type filter dropdown"""
        if pathname != "/train-models" or not token:
            return []

        train_models = make_api_request("/train-models", token=token)
        if not train_models:
            return []

        # Get unique model types
        model_types = sorted(list(set([model['model_type'] for model in train_models if model.get('model_type')])))
        return [{"label": mtype, "value": mtype} for mtype in model_types]

    @callback(
        Output("filter-train-model-country", "options"),
        Input("url", "pathname"),
        State("token-store", "data")
    )
    def populate_country_filter(pathname, token):
        """Populate country filter dropdown"""
        if pathname != "/train-models" or not token:
            return []

        train_models = make_api_request("/train-models", token=token)
        if not train_models:
            return []

        # Get unique countries
        countries = sorted(list(set([model['country_of_origin'] for model in train_models if model.get('country_of_origin')])))
        return [{"label": country, "value": country} for country in countries]

    @callback(
        Output("filter-train-model-manufacturer", "options"),
        Input("url", "pathname"),
        State("token-store", "data")
    )
    def populate_manufacturer_filter(pathname, token):
        """Populate manufacturer filter dropdown"""
        if pathname != "/train-models" or not token:
            return []

        train_models = make_api_request("/train-models", token=token)
        if not train_models:
            return []

        # Get unique manufacturers
        manufacturers = sorted(list(set([model['manufacturer'] for model in train_models if model.get('manufacturer')])))
        return [{"label": mfr, "value": mfr} for mfr in manufacturers]

    @callback(
        Output("filter-train-model-routes", "options"),
        Input("url", "pathname"),
        State("token-store", "data")
    )
    def populate_routes_filter(pathname, token):
        """Populate routes filter dropdown"""
        if pathname != "/train-models" or not token:
            return []

        # Return all routes R01-R09 as options
        return [{"label": route.upper(), "value": route.upper()} for route in ROUTE_COLS]

    @callback(
        [Output("filter-train-model-name", "value"),
         Output("filter-train-model-type", "value"),
         Output("filter-train-model-country", "value"),
         Output("filter-train-model-manufacturer", "value"),
         Output("filter-train-model-routes", "value")],
        Input("clear-train-model-filters", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_train_model_filters(n_clicks):
        """Clear all train model filters"""
        return None, None, None, None, None

    @callback(
        [Output("train-model-modal", "is_open"),
         Output("train-model-modal-title", "children"),
         Output("train-model-id", "disabled", allow_duplicate=True)],
        [Input("add-train-model-btn", "n_clicks"),
         Input("cancel-train-model-btn", "n_clicks")],
        State("train-model-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_train_model_modal(add_clicks, cancel_clicks, is_open):
        """Toggle train model add/edit modal"""
        ctx = callback_context
        if not ctx.triggered:
            return is_open, "Add New Train Model", False

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "add-train-model-btn":
            return True, "Add New Train Model", False  # Enable model_id for new models
        elif button_id == "cancel-train-model-btn":
            return False, "Add New Train Model", False

        return is_open, "Add New Train Model", False

    @callback(
        [Output("train-model-alert", "children"),
         Output("train-model-alert", "is_open"),
         Output("train-model-alert", "color"),
         Output("train-model-modal", "is_open", allow_duplicate=True),
         Output("train-model-id", "value"),
         Output("train-model-name", "value"),
         Output("train-model-type", "value"),
         Output("train-model-manufacturer", "value"),
         Output("train-model-country", "value"),
         Output("train-model-operational-units", "value"),
         Output("train-model-compartments-unit", "value"),
         Output("train-model-total-compartments", "value"),
         Output("train-model-seating-capacity", "value"),
         Output("train-model-standing-capacity", "value"),
         Output("train-model-total-capacity", "value"),
         Output("train-model-routes", "value"),
         Output("train-model-refresh-trigger", "data")],
        Input("save-train-model-btn", "n_clicks"),
        [State("train-model-id", "value"),
         State("train-model-name", "value"),
         State("train-model-type", "value"),
         State("train-model-manufacturer", "value"),
         State("train-model-country", "value"),
         State("train-model-operational-units", "value"),
         State("train-model-compartments-unit", "value"),
         State("train-model-total-compartments", "value"),
         State("train-model-seating-capacity", "value"),
         State("train-model-standing-capacity", "value"),
         State("train-model-total-capacity", "value"),
         State("train-model-routes", "value"),
         State("token-store", "data"),
         State("train-model-id", "disabled"),
         State("train-model-refresh-trigger", "data")],
        prevent_initial_call=True
    )
    def save_train_model(n_clicks, model_id, model_name, model_type, manufacturer, country,
                         operational_units, compartments_unit, total_compartments,
                         seating_capacity, standing_capacity, total_capacity, routes, token, is_editing, current_refresh):
        """Save new or update existing train model"""
        if not n_clicks or not token:
            return no_update, False, "info", *([no_update] * 14)

        # Validation
        if not all([model_id, model_name, model_type, manufacturer, country]):
            return "Please fill in all required fields marked with *", True, "danger", *([no_update] * 14)

        if not all([operational_units is not None, compartments_unit is not None, total_compartments is not None,
                    seating_capacity is not None, standing_capacity is not None, total_capacity is not None]):
            return "Please fill in all capacity fields", True, "danger", *([no_update] * 14)

        # Validate model_id format (uppercase letters and numbers only, max 10 chars)
        if not re.match(r'^[A-Z0-9]{1,10}$', model_id):
            return "Model ID must be 1-10 uppercase letters/numbers only", True, "danger", *([no_update] * 14)

        # Prepare data payload with route assignments
        route_data = {route: route in (routes or []) for route in ROUTE_COLS}

        data = {
            "model_id": model_id,
            "model_name": model_name,
            "model_type": model_type,
            "manufacturer": manufacturer,
            "country_of_origin": country,
            "operational_units": int(operational_units),
            "compartments_per_unit": int(compartments_unit),
            "total_compartments_assigned_per_model": int(total_compartments),
            "seating_passengers_per_compartment": int(seating_capacity),
            "standing_passengers_per_compartment": int(standing_capacity),
            "total_passengers_per_compartment": int(total_capacity),
            **route_data
        }

        # Make API request - PATCH if editing, POST if creating
        if is_editing:
            result = make_api_request(f"/train-models/{model_id}", method="PATCH", token=token, data=data)
            success_msg = f"✓ Train model '{model_name}' has been successfully updated with the latest configuration."
        else:
            result = make_api_request("/train-models", method="POST", token=token, data=data)
            success_msg = f"✓ Train model '{model_name}' has been successfully added to the fleet inventory."

        if result and (not isinstance(result, dict) or 'error' not in result):
            return (
                success_msg, True, "success", False,
                "", "", "", "", "", None, None, None, None, None, None, [],
                (current_refresh or 0) + 1
            )

        error_msg = result.get('message', 'Operation failed: Unable to save train model configuration. Please verify all fields and try again.') if isinstance(result, dict) else 'Operation failed: Unable to save train model configuration. Please verify all fields and try again.'
        return error_msg, True, "danger", *([no_update] * 14)

    @callback(
        [Output("train-model-modal", "is_open", allow_duplicate=True),
         Output("train-model-modal-title", "children", allow_duplicate=True),
         Output("train-model-id", "value", allow_duplicate=True),
         Output("train-model-id", "disabled"),
         Output("train-model-name", "value", allow_duplicate=True),
         Output("train-model-type", "value", allow_duplicate=True),
         Output("train-model-manufacturer", "value", allow_duplicate=True),
         Output("train-model-country", "value", allow_duplicate=True),
         Output("train-model-operational-units", "value", allow_duplicate=True),
         Output("train-model-compartments-unit", "value", allow_duplicate=True),
         Output("train-model-total-compartments", "value", allow_duplicate=True),
         Output("train-model-seating-capacity", "value", allow_duplicate=True),
         Output("train-model-standing-capacity", "value", allow_duplicate=True),
         Output("train-model-total-capacity", "value", allow_duplicate=True),
         Output("train-model-routes", "value", allow_duplicate=True)],
        Input({"type": "edit-train-model", "index": ALL}, "n_clicks"),
        State("token-store", "data"),
        prevent_initial_call=True
    )
    def open_edit_modal(n_clicks_list, token):
        """Open modal with train model data for editing"""
        if not any(n_clicks_list) or not token:
            return NO_UPDATE_15

        # Find which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            return NO_UPDATE_15

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        import json
        model_id = json.loads(button_id)["index"]

        # Fetch train model data
        model_data = make_api_request(f"/train-models/{model_id}", token=token)

        if not model_data:
            return NO_UPDATE_15

        # Get assigned routes
        assigned_routes = [col for col in ROUTE_COLS if model_data.get(col, False)]
        
        return (
            True,  # Open modal
            "Edit Train Model",  # Modal title
            model_data.get('model_id', ''),
            True,  # Disable model_id field (can't change primary key)
            model_data.get('model_name', ''),
            model_data.get('model_type', ''),
            model_data.get('manufacturer', ''),
            model_data.get('country_of_origin', ''),
            model_data.get('operational_units', 0),
            model_data.get('compartments_per_unit', 0),
            model_data.get('total_compartments_assigned_per_model', 0),
            model_data.get('seating_passengers_per_compartment', 0),
            model_data.get('standing_passengers_per_compartment', 0),
            model_data.get('total_passengers_per_compartment', 0),
            assigned_routes
        )

    @callback(
        [Output("delete-confirm-modal", "is_open"),
         Output("delete-model-id-store", "data")],
        Input({"type": "delete-train-model", "index": ALL}, "n_clicks"),
        State("delete-confirm-modal", "is_open"),
        prevent_initial_call=True
    )
    def open_delete_modal(n_clicks_list, is_open):
        """Open delete confirmation modal"""
        if not any(n_clicks_list):
            return no_update, no_update
        
        # Find which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        import json
        model_id = json.loads(button_id)["index"]
        
        return True, model_id

    @callback(
        [Output("train-model-alert", "children", allow_duplicate=True),
         Output("train-model-alert", "is_open", allow_duplicate=True),
         Output("train-model-alert", "color", allow_duplicate=True),
         Output("delete-confirm-modal", "is_open", allow_duplicate=True),
         Output("train-model-refresh-trigger", "data", allow_duplicate=True)],
        Input("confirm-delete-model-btn", "n_clicks"),
        [State("delete-model-id-store", "data"),
         State("token-store", "data"),
         State("train-model-refresh-trigger", "data")],
        prevent_initial_call=True
    )
    def delete_train_model(n_clicks, model_id, token, current_refresh):
        """Delete train model from database"""
        if not n_clicks or not model_id or not token:
            return no_update, no_update, no_update, no_update, no_update
        
        # Make DELETE request (DELETE returns 204 No Content on success)
        result = make_api_request(f"/train-models/{model_id}", method="DELETE", token=token)

        # Check if deletion was successful
        if result is None or result is True or (isinstance(result, dict) and 'error' not in result):
            return f"✓ Train model '{model_id}' has been permanently removed from the system.", True, "success", False, (current_refresh or 0) + 1

        return "✗ Deletion failed: Unable to remove train model. This model may be in use by active schedules.", True, "danger", False, no_update

    @callback(
        Output("delete-confirm-modal", "is_open", allow_duplicate=True),
        Input("cancel-delete-model-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def close_delete_modal(n_clicks):
        """Close delete confirmation modal"""
        if n_clicks:
            return False
        return no_update
