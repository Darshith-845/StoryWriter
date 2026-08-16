from dataclasses import dataclass, field
from typing import List

from models.scene import Scene

@dataclass
class Chapter:
    number: int
    title: str
    goal: str
    revelation: str
    ending_hook: str
    scenes: List[Scene] = field(default_factory=list)
    final_text: str = ""
    critic_evaluation: dict = field(default_factory=dict)
    continuity_check: dict = field(default_factory=dict)