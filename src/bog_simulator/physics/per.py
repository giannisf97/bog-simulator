"""Time-rate conversion utility module."""

def sec(quantity: float | int) -> float:
    """Converts a rate from per-hour to per-second (divides by 3600).

    Args:
        quantity (float | int): Quantity per hour (e.g., kg/h).

    Returns:
        float: Quantity per second (e.g., kg/s).
    """
    return quantity / 3600

def hour(quantity: float | int) -> float:
    """Converts a rate from per-second to per-hour (multiplies by 3600).

    Args:
        quantity (float | int): Quantity per second (e.g., kg/s).

    Returns:
        float: Quantity per hour (e.g., kg/h).
    """
    return quantity * 3600