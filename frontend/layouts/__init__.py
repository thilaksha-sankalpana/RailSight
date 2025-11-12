"""
TCDAFS - Page Layouts
Export all page layout functions
"""
from .overview import overview_layout
from .tickets import ticket_layout
from .train_models import train_models_layout
from .trains import trains_layout
from .routes import routes_layout
from .schedules import train_schedules_layout
from .pricing import ticket_pricing_layout
from .daily_schedules import daily_schedules_layout
from .schedule_by_station import schedule_by_station_layout

__all__ = [
    'overview_layout',
    'ticket_layout',
    'train_models_layout',
    'trains_layout',
    'routes_layout',
    'train_schedules_layout',
    'ticket_pricing_layout',
    'daily_schedules_layout',
    'schedule_by_station_layout'
]
