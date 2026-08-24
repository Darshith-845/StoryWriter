from dataclasses import dataclass, field
from typing import List

from models.chapter import Chapter
from models.character import Character
from models.memory import StoryMemory


@dataclass
class Story:
    title: str
    topic: str
    summary: str
    theme: str

    characters: List[Character] = field(default_factory=list)
    chapters: List[Chapter] = field(default_factory=list)

    memory: StoryMemory | None = None

    narrative_style: str = ""
    perspective: str = ""
    tense: str = ""