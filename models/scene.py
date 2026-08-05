from dataclasses import dataclass, field
from typing import List


@dataclass
class Scene:
    number: int
    title: str
    location: str
    goal: str
    conflict: str
    ending: str
    pov: str
    participating_characters: List[str] = field(default_factory=list)
    character_plans: dict = field(default_factory=dict)
    summary: str = ""
    prose: str = ""