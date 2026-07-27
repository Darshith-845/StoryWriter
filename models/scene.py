from dataclasses import dataclass, field
from typing import List


@dataclass
class Scene:
    number: int
    title: str
    location: str
    objective: str
    conflict: str
    ending: str
    participating_characters: List[str] = field(default_factory=list)
    summary: str = ""
    prose: str = ""