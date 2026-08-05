from dataclasses import dataclass, field

@dataclass
class StoryMemory:
    summary: str = ""
    last_scene_summary: str = ""
    character_states: dict = field(default_factory=dict)
    open_threads: list = field(default_factory=list)
    important_objects: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)
    theme_progress: str = ""
    timeline: list = field(default_factory=list)