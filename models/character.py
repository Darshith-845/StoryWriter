from dataclasses import dataclass, field
from typing import List
from typing import Any

@dataclass
class Character:
    name: str
    role: str
    personality: str
    motivation: str
    backstory: str
    speech_profile: dict[str, Any] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    knowledge: List[str] = field(default_factory=list)
    beliefs: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    current_location: str = ""
    current_goal: str = ""
    current_emotion: str = ""
    relationships: dict[str, str] = field(default_factory=dict)