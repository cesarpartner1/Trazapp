from .models import ActivityLog


def log_activity(category: str, title: str, meta: str = "", event_type: str = ActivityLog.EVENT_CREATE) -> None:
    """Crea de forma segura un registro de actividad para el tablero."""
    ActivityLog.objects.create(
        category=category,
        title=title,
        meta=meta,
        event_type=event_type,
    )
