from dataclasses import dataclass
from abc import ABC
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)


@dataclass
class ParamConfig(ABC):
    """Base parameter configuration using a dataclass."""

    name: str
    sql_identifier: str


@dataclass
class SliderParamConfig(ParamConfig):
    """Slider configuration inheriting from the base dataclass."""

    min_val: int
    max_val: int
    step: int
    # Use a field with a default_factory to handle the mutable default logic
    value: int = None

    def __post_init__(self):
        """Called after the dataclass's own __init__."""
        if self.value is None:
            self.value = self.min_val


s = SliderParamConfig(name="named", sql_identifier="sql", min_val=1, max_val=3, step=1)
t = SliderParamConfig(
    name="named", sql_identifier="sql", min_val=1, max_val=3, step=1, value=2
)

logger.info(f"s name {s.name} min {s.min_val} value {s.value}")
logger.info(f"t name {t.name} min {t.min_val} value {t.value}")
