"""
Shared database helper functions.
"""

from webapp.extensions import db


def get_or_create(model, filter_by, defaults=None):
    """
    Find an existing record by filter_by dict, or create a new one.

    Args:
        model: SQLAlchemy model class
        filter_by: dict of columns to filter by (e.g. {"google_id": "abc123"})
        defaults: dict of additional columns to set when creating (not used for lookup)

    Returns:
        (instance, created) — the model instance and a boolean indicating if it was newly created
    """
    instance = model.query.filter_by(**filter_by).first()

    if instance:
        return instance, False

    # Merge filter keys + defaults for creation
    create_kwargs = {**filter_by, **(defaults or {})}
    instance = model(**create_kwargs)
    db.session.add(instance)

    return instance, True