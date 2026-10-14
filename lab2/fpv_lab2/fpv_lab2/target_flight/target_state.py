from enum import Enum, auto


class TargetState(Enum):
    """Додаткові стани польоту до точки.

    Базові стани (FlightState) не змінюються: ці стани вставляються
    між зльотом (FlightState.HOVERING) і посадкою (FlightState.LANDING).
    """

    STABILIZING = auto()
    FLYING_TO_TARGET = auto()
    HOLDING_AT_TARGET = auto()
