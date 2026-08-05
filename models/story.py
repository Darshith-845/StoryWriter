from dataclasses import dataclass, field
from typing import List

from models.chapter import Chapter
from models.character import Character
from models.memory import StoryMemory


@dataclass
class Story:
    title: str
    topic: str
    world: str
    theme: str
    writing_style: str
    characters: List[Character] = field(default_factory=list)
    chapters: List[Chapter] = field(default_factory=list)
    memory: StoryMemory = field(default_factory=StoryMemory)
    status: str = "planning"
    narrative: dict = field(default_factory=dict)