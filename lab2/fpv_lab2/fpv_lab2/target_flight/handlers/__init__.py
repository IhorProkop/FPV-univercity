from ...flight_test.flight_state import FlightState
from ..target_state import TargetState
from .climbing import ClimbingHandler
from .flying_to_target import FlyingToTargetHandler
from .holding_at_target import HoldingAtTargetHandler
from .prearm_retry import PrearmRetryHandler
from .stabilizing import StabilizingHandler

# Ці обробники додаються поверх базової таблиці HANDLERS
TARGET_HANDLERS = {
    FlightState.PREARM_CHECK: PrearmRetryHandler(),
    FlightState.HOVERING: ClimbingHandler(),
    TargetState.STABILIZING: StabilizingHandler(),
    TargetState.FLYING_TO_TARGET: FlyingToTargetHandler(),
    TargetState.HOLDING_AT_TARGET: HoldingAtTargetHandler(),
}
