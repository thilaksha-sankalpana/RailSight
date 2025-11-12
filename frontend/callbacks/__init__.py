"""
TCDAFS - Callback Registration
Register all application callbacks
"""
from . import (
    auth_callbacks,
    navigation_callbacks,
    overview_callbacks,
    tickets_callbacks,
    ticket_verification_callbacks,
    train_models_callbacks,
    trains_callbacks,
    routes_callbacks,
    train_schedules_callbacks,
    profile_callbacks,
    schedule_by_station_callbacks,
    pricing_callbacks,
    clientside_callbacks,
    daily_schedules_callbacks
)


def register_callbacks(app):
    """
    Register all callbacks with the Dash app

    Args:
        app: Dash application instance
    """
    auth_callbacks.register(app)
    navigation_callbacks.register(app)
    overview_callbacks.register(app)
    tickets_callbacks.register(app)
    ticket_verification_callbacks.register(app)
    train_models_callbacks.register(app)
    trains_callbacks.register(app)
    routes_callbacks.register(app)
    train_schedules_callbacks.register(app)
    profile_callbacks.register(app)
    schedule_by_station_callbacks.register(app)
    pricing_callbacks.register(app)
    clientside_callbacks.register(app)
    daily_schedules_callbacks.register(app)
