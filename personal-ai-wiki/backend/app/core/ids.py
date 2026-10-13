import uuid


def new_id() -> str:
    """Stable, globally unique identifier for every entity (UUID4, lowercase hex with dashes)."""
    return str(uuid.uuid4())
