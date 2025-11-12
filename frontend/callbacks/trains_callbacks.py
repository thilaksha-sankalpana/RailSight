"""
TCDAFS - Operational Trains Callbacks
Handle operational trains CRUD operations, filtering, and table display
"""
from dash import callback, Input, Output, State, html, no_update, dash_table, callback_context, ALL
import pandas as pd
from utils.api import make_api_request
from config.styles import COLORS
import logging
import dash_bootstrap_components as dbc
import json

logger = logging.getLogger(__name__)

print("trains_callbacks.py module loaded successfully")


def register(app):
    """Register operational trains callbacks with the app"""
    print("Registering trains callbacks...")

    @callback(
        Output("trains-table", "children"),
        [Input("url", "pathname"),
         Input("filter-operational-train-model", "value"),
         Input("filter-operational-train-status", "value"),
         Input("trains-refresh-trigger", "data")],
        [State("token-store", "data")],
        prevent_initial_call=False
    )
    def load_operational_trains(pathname, model_filter, status_filter, refresh_trigger, token):
        """Load and display operational trains table with filtering"""
        if pathname != "/trains" or not token:
            return html.P("Loading...")

        # Build query parameters for server-side filtering
        query_params = []
        if model_filter:
            query_params.append(f"model_id={model_filter}")
        if status_filter:
            query_params.append(f"status={status_filter}")

        # Construct API endpoint with query parameters
        api_endpoint = "/trains"
        if query_params:
            api_endpoint += "?" + "&".join(query_params)

        trains = make_api_request(api_endpoint, token=token)

        if not trains:
            return html.Div([
                html.I(className="fas fa-train", style={
                    'fontSize': '64px',
                    'color': '#e0e0e0',
                    'display': 'block',
                    'textAlign': 'center',
                    'marginBottom': '20px'
                }),
                html.P("No trains available", style={
                    'textAlign': 'center',
                    'color': COLORS['text_primary'],
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'marginBottom': '8px'
                }),
                html.P("Click 'Add Train' to create your first operational train", style={
                    'textAlign': 'center',
                    'color': COLORS['text_secondary'],
                    'fontSize': '14px'
                })
            ], style={'padding': '60px 40px'})

        df = pd.DataFrame(trains)

        # Get train model names
        train_models = make_api_request("/train-models", token=token)
        if train_models:
            models_df = pd.DataFrame(train_models)
            # Create a mapping of model_id to model_name
            model_map = dict(zip(models_df['model_id'], models_df['model_name']))
            # Add model_name column to trains dataframe
            df['model_name'] = df['model_id'].map(model_map)
        else:
            df['model_name'] = df['model_id']  # Fallback to showing model_id

        if df.empty:
            return html.Div([
                html.I(className="fas fa-filter", style={
                    'fontSize': '56px',
                    'color': '#e0e0e0',
                    'display': 'block',
                    'textAlign': 'center',
                    'marginBottom': '20px'
                }),
                html.P("No trains match your filters", style={
                    'textAlign': 'center',
                    'color': COLORS['text_primary'],
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'marginBottom': '8px'
                }),
                html.P("Try adjusting your filter criteria or reset filters", style={
                    'textAlign': 'center',
                    'color': COLORS['text_secondary'],
                    'fontSize': '14px'
                })
            ], style={'padding': '60px 40px'})

        # Create table rows with status badge and dropdown
        table_rows = []
        for _, row in df.iterrows():
            train_id = row['train_id']
            status = row['status']
            model_name = row['model_name']
            compartments = row.get('compartments_per_unit', 'N/A')

            # Status badge colors
            status_colors = {
                'Active': 'success',
                'Maintenance': 'warning',
                'Inactive': 'secondary',
                'Retired': 'danger'
            }

            table_rows.append(
                html.Tr([
                    html.Td(train_id, style={
                        'padding': '16px',
                        'verticalAlign': 'middle',
                        'fontWeight': '600',
                        'color': COLORS['text_primary']
                    }),
                    html.Td(model_name, style={
                        'padding': '16px',
                        'verticalAlign': 'middle',
                        'color': COLORS['text_secondary']
                    }),
                    html.Td(str(compartments), style={
                        'padding': '16px',
                        'verticalAlign': 'middle',
                        'textAlign': 'center',
                        'fontWeight': '500'
                    }),
                    html.Td([
                        dbc.Badge(
                            status,
                            color=status_colors.get(status, 'secondary'),
                            className="me-2",
                            style={'fontSize': '12px', 'padding': '6px 12px'}
                        ),
                        dbc.Select(
                            id={'type': 'train-status-select', 'index': train_id},
                            options=[
                                {"label": "Active", "value": "Active"},
                                {"label": "Maintenance", "value": "Maintenance"},
                                {"label": "Inactive", "value": "Inactive"},
                                {"label": "Retired", "value": "Retired"}
                            ],
                            value=status,
                            size="sm",
                            style={'width': '140px', 'display': 'inline-block'}
                        )
                    ], style={'padding': '16px', 'verticalAlign': 'middle'}),
                ], style={
                    'borderBottom': f'1px solid {COLORS["border"]}',
                    'transition': 'background-color 0.2s',
                }, className="table-row-hover")
            )

        return html.Table([
            html.Thead(
                html.Tr([
                    html.Th("Train ID", style={
                        'padding': '16px',
                        'backgroundColor': COLORS['primary'],
                        'color': 'white',
                        'fontWeight': '600',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'borderTopLeftRadius': '8px'
                    }),
                    html.Th("Train Model", style={
                        'padding': '16px',
                        'backgroundColor': COLORS['primary'],
                        'color': 'white',
                        'fontWeight': '600',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px'
                    }),
                    html.Th("Compartments", style={
                        'padding': '16px',
                        'backgroundColor': COLORS['primary'],
                        'color': 'white',
                        'fontWeight': '600',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'textAlign': 'center'
                    }),
                    html.Th("Status", style={
                        'padding': '16px',
                        'backgroundColor': COLORS['primary'],
                        'color': 'white',
                        'fontWeight': '600',
                        'fontSize': '13px',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'borderTopRightRadius': '8px'
                    }),
                ])
            ),
            html.Tbody(table_rows)
        ], style={
            'width': '100%',
            'borderCollapse': 'separate',
            'borderSpacing': '0',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
        })

    @callback(
        Output("filter-operational-train-model", "options"),
        Input("url", "pathname"),
        State("token-store", "data")
    )
    def populate_model_filter(pathname, token):
        """Populate train model filter dropdown with model names from operational trains"""
        if pathname != "/trains" or not token:
            return []

        # Get operational trains
        trains = make_api_request("/trains", token=token)
        if not trains:
            return []

        # Get unique model_ids from operational trains
        train_df = pd.DataFrame(trains)
        unique_model_ids = train_df['model_id'].unique().tolist()

        # Get train models to get their names
        train_models = make_api_request("/train-models", token=token)
        if not train_models:
            # Fallback: just show model IDs
            return [{"label": model_id, "value": model_id} for model_id in sorted(unique_model_ids)]

        # Create mapping and return options with model names as labels
        models_df = pd.DataFrame(train_models)
        # Filter to only models that are actually in operational trains
        models_df = models_df[models_df['model_id'].isin(unique_model_ids)]
        
        options = [
            {"label": f"{row['model_name']} ({row['model_id']})", "value": row['model_id']}
            for _, row in models_df.iterrows()
        ]
        
        return sorted(options, key=lambda x: x['label'])

    @callback(
        [Output("filter-operational-train-model", "value"),
         Output("filter-operational-train-status", "value")],
        Input("clear-operational-train-filters", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_operational_train_filters(n_clicks):
        """Clear all operational train filters"""
        return None, None

    @callback(
        [Output("operational-train-alert", "children"),
         Output("operational-train-alert", "is_open"),
         Output("operational-train-alert", "color")],
        Input({'type': 'train-status-select', 'index': ALL}, 'value'),
        [State({'type': 'train-status-select', 'index': ALL}, 'id'),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def update_train_status(status_values, status_ids, token):
        """Update train status when dropdown is changed"""
        ctx = callback_context
        if not ctx.triggered or not token:
            return no_update, False, "info"

        triggered_prop = ctx.triggered[0]['prop_id']

        # Ignore false triggers from table re-render
        if triggered_prop == '.' or not triggered_prop:
            return no_update, False, "info"

        try:
            # Extract train_id from triggered prop (Format: {"index":"T001","type":"train-status-select"}.value)
            prop_parts = triggered_prop.split('.')[0]
            train_info = json.loads(prop_parts)
            train_id = train_info['index']

            # Find the index of this train in the lists
            train_index = None
            for i, status_id in enumerate(status_ids):
                if status_id['index'] == train_id:
                    train_index = i
                    break

            if train_index is None:
                return "Error: Train not found", True, "danger"

            new_status = status_values[train_index]

        except Exception as e:
            logger.error(f"Error parsing train status update: {e}")
            return "Error updating status", True, "danger"

        # Fetch current train data to check if status actually changed
        current_train = make_api_request(f"/trains/{train_id}", token=token)
        if current_train and current_train.get('status') == new_status:
            return no_update, False, "info"

        # Update train status via API
        result = make_api_request(f"/trains/{train_id}", method="PATCH", token=token, data={"status": new_status})

        if result:
            return f"Train {train_id} status updated to {new_status}", True, "success"
        else:
            return f"Failed to update status for train {train_id}", True, "danger"

    # ============= ADD TRAIN MODAL CALLBACKS =============

    @callback(
        [Output("operational-train-modal", "is_open"),
         Output("operational-train-model", "value"),
         Output("operational-train-compartments", "value"),
         Output("operational-train-quantity", "value"),
         Output("operational-train-status", "value")],
        [Input("add-operational-train-btn", "n_clicks"),
         Input("cancel-operational-train-btn", "n_clicks"),
         Input("save-operational-train-btn", "n_clicks")],
        [State("operational-train-modal", "is_open"),
         State("operational-train-model", "value"),
         State("operational-train-compartments", "value"),
         State("operational-train-quantity", "value"),
         State("operational-train-status", "value"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def toggle_add_modal(add_clicks, cancel_clicks, save_clicks, is_open, model_id, compartments, quantity, status, token):
        """Open/close add train modal and reset form"""
        ctx = callback_context
        if not ctx.triggered:
            return False, None, "", 1, "Active"

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == "add-operational-train-btn":
            # Open modal and reset form
            return True, None, "", 1, "Active"
        elif button_id == "cancel-operational-train-btn":
            # Close modal and reset form
            return False, None, "", 1, "Active"
        elif button_id == "save-operational-train-btn":
            # Validation and save logic will be handled by separate callback
            # Just keep modal open until save is successful
            return no_update, no_update, no_update, no_update, no_update

        return False, None, "", 1, "Active"

    @callback(
        Output("operational-train-model", "options"),
        Input("operational-train-modal", "is_open"),
        State("token-store", "data")
    )
    def populate_add_modal_train_models(is_open, token):
        """Populate train model dropdown in add modal"""
        if not is_open or not token:
            return []

        train_models = make_api_request("/train-models", token=token)
        if not train_models:
            return []

        return [
            {"label": f"{model['model_name']} ({model['model_id']})", "value": model['model_id']}
            for model in train_models
        ]

    @callback(
        Output("operational-train-compartments", "value", allow_duplicate=True),
        Input("operational-train-model", "value"),
        State("token-store", "data"),
        prevent_initial_call=True
    )
    def autofill_compartments(model_id, token):
        """Auto-fill compartments per unit based on selected model"""
        if not model_id or not token:
            return ""

        train_models = make_api_request("/train-models", token=token)
        if not train_models:
            return ""

        # Find the selected model
        for model in train_models:
            if model['model_id'] == model_id:
                return model.get('compartments_per_unit', "")

        return ""

    @callback(
        Output("train-id-preview", "children"),
        [Input("operational-train-model", "value"),
         Input("operational-train-quantity", "value")],
        State("token-store", "data")
    )
    def preview_train_ids(model_id, quantity, token):
        """Show preview of train IDs that will be created"""
        if not model_id or not quantity or not token:
            return None

        try:
            quantity = int(quantity)
            if quantity < 1 or quantity > 50:
                return dbc.Alert("Quantity must be between 1 and 50", color="warning", className="mt-2")
        except:
            return None

        # Get existing trains to determine next available ID
        trains = make_api_request("/trains", token=token)
        existing_ids = [train['train_id'] for train in trains] if trains else []

        # Find the highest existing counter for this model
        max_counter = 0
        prefix = f"{model_id}-"
        for train_id in existing_ids:
            if train_id.startswith(prefix):
                try:
                    # Extract counter from train_id (e.g., "S14-05" -> 5)
                    counter_part = train_id[len(prefix):]
                    counter_val = int(counter_part)
                    max_counter = max(max_counter, counter_val)
                except:
                    continue

        # Generate preview IDs starting from max_counter + 1
        preview_ids = []
        counter = max_counter + 1
        for _ in range(quantity):
            new_id = f"{model_id}-{counter:02d}"
            preview_ids.append(new_id)
            counter += 1

        return html.Div([
            html.Hr(style={'margin': '20px 0', 'borderColor': '#e0e0e0'}),
            html.Div([
                html.I(className="fas fa-list", style={'marginRight': '8px', 'color': COLORS['primary'], 'fontSize': '14px'}),
                html.Span("Preview: Train IDs to be Created", style={'fontWeight': '600', 'fontSize': '14px', 'color': COLORS['text_primary']})
            ], style={'marginBottom': '12px', 'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                dbc.Badge(train_id, color="primary", className="me-2 mb-2", style={
                    'fontSize': '13px',
                    'padding': '8px 14px',
                    'fontWeight': '500',
                    'fontFamily': 'monospace'
                })
                for train_id in preview_ids
            ]),
            dbc.Alert([
                html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
                f"{quantity} train{'s' if quantity > 1 else ''} will be added to the operational fleet"
            ], color="info", className="mt-3", style={'fontSize': '13px', 'padding': '10px 14px'})
        ])

    @callback(
        [Output("operational-train-alert", "children", allow_duplicate=True),
         Output("operational-train-alert", "is_open", allow_duplicate=True),
         Output("operational-train-alert", "color", allow_duplicate=True),
         Output("operational-train-modal", "is_open", allow_duplicate=True),
         Output("trains-refresh-trigger", "data", allow_duplicate=True)],
        Input("save-operational-train-btn", "n_clicks"),
        [State("operational-train-model", "value"),
         State("operational-train-compartments", "value"),
         State("operational-train-quantity", "value"),
         State("operational-train-status", "value"),
         State("trains-refresh-trigger", "data"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def save_new_trains(n_clicks, model_id, compartments, quantity, status, current_refresh_trigger, token):
        """Save new trains to database"""
        if not n_clicks or not token:
            return no_update, False, "info", no_update, no_update

        # Validation
        if not model_id:
            return "Please select a train model", True, "danger", True, no_update

        if not compartments:
            return "Compartments per unit is required", True, "danger", True, no_update

        try:
            quantity = int(quantity)
            if quantity < 1 or quantity > 50:
                return "Quantity must be between 1 and 50", True, "danger", True, no_update
        except:
            return "Invalid quantity", True, "danger", True, no_update

        # Get existing trains to determine next available IDs
        trains = make_api_request("/trains", token=token)
        existing_ids = [train['train_id'] for train in trains] if trains else []

        # Find the highest existing counter for this model
        max_counter = 0
        prefix = f"{model_id}-"
        for train_id in existing_ids:
            if train_id.startswith(prefix):
                try:
                    # Extract counter from train_id (e.g., "S14-05" -> 5)
                    counter_part = train_id[len(prefix):]
                    counter_val = int(counter_part)
                    max_counter = max(max_counter, counter_val)
                except:
                    continue

        # Create trains starting from max_counter + 1
        created_trains = []
        failed_trains = []
        counter = max_counter + 1

        for _ in range(quantity):
            new_train_id = f"{model_id}-{counter:02d}"
            counter += 1

            # Create train via API
            train_data = {
                "train_id": new_train_id,
                "model_id": model_id,
                "compartments_per_unit": int(compartments),
                "status": status
            }

            result = make_api_request("/trains", method="POST", token=token, data=train_data)

            if result:
                created_trains.append(new_train_id)
            else:
                failed_trains.append(new_train_id)

        # Prepare response message and trigger table refresh
        if created_trains and not failed_trains:
            message = f"Successfully created {len(created_trains)} train(s): {', '.join(created_trains)}"
            color = "success"
            close_modal = True
            new_trigger = (current_refresh_trigger or 0) + 1
        elif created_trains and failed_trains:
            message = f"Partially successful: Created {len(created_trains)} train(s), {len(failed_trains)} failed"
            color = "warning"
            close_modal = False
            new_trigger = (current_refresh_trigger or 0) + 1
        else:
            message = "Failed to create trains. Please try again."
            color = "danger"
            close_modal = False
            new_trigger = no_update

        return message, True, color, not close_modal, new_trigger
