from .binding import Binding
from .template import Template
from dataclasses import dataclass, field


@dataclass
class Settings:
    bindings: list[Binding] = field(default_factory=list)  # type: ignore
    templates: list[Template] = field(default_factory=list)  # type: ignore
