"""Gas production / auxiliary supply model module."""

class Producer:
    """Represents an external gas source, forcing vaporizer, or BOG injection rate.

    Attributes:
        rate (int | float): Gas generation or supply rate [kg/h].
    """
    rate: float | int

    def __init__(self, rate: float | int) -> None:
        """Initializes a Producer instance with a designated generation rate.

        Args:
            rate (int | float): Gas generation rate [kg/h].
        """
        self.rate = rate