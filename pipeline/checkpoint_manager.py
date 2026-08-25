import json
from pathlib import Path
from dataclasses import asdict

from models.story import Story
from models.chapter import Chapter
from models.scene import Scene
from models.character import Character
from models.memory import StoryMemory


class CheckpointManager:
    """
    Handles serialization, deserialization, and persistence
    of StoryWriter state.

    The manager converts nested dataclass objects into JSON
    and reconstructs them when a story is resumed.
    """

    def __init__(self, checkpoint_directory: str = "stories/incomplete"):
        self.checkpoint_directory = Path(checkpoint_directory)

        self.checkpoint_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(
        self,
        story: Story,
        memory: StoryMemory
    ) -> Path:
        """
        Serializes the current story state and saves it
        as a checkpoint.
        """

        checkpoint = self._serialize(
            story,
            memory
        )

        path = self._checkpoint_path(
            story
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                checkpoint,
                file,
                indent=2,
                ensure_ascii=False
            )

        return path

    def load(
        self,
        story_title: str
    ) -> tuple[Story, StoryMemory]:

        path = self.checkpoint_directory / (
            f"{story_title}_checkpoint.json"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"No checkpoint found for: {story_title}"
            )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return self._deserialize(data)

    def exists(
        self,
        story_title: str
    ) -> bool:

        path = self.checkpoint_directory / (
            f"{story_title}_checkpoint.json"
        )

        return path.exists()

    def delete(
        self,
        story_title: str
    ) -> None:

        path = self.checkpoint_directory / (
            f"{story_title}_checkpoint.json"
        )

        if path.exists():
            path.unlink()

    def _serialize(
        self,
        story: Story,
        memory: StoryMemory
    ) -> dict:
        """
        Converts the Story and StoryMemory dataclasses
        into JSON-compatible dictionaries.
        """

        return {
            "story": asdict(story),
            "memory": asdict(memory)
        }

    def _deserialize(
        self,
        data: dict
    ) -> tuple[Story, StoryMemory]:

        story_data = data["story"]
        memory_data = data["memory"]

        memory = self._deserialize_memory(
            memory_data
        )

        story = self._deserialize_story(
            story_data,
            memory
        )

        return story, memory

    def _deserialize_story(
        self,
        data: dict,
        memory: StoryMemory
    ) -> Story:

        characters = [
            self._deserialize_character(character)
            for character in data.get(
                "characters",
                []
            )
        ]

        chapters = [
            self._deserialize_chapter(chapter)
            for chapter in data.get(
                "chapters",
                []
            )
        ]

        return Story(
            title=data.get("title", ""),
            topic=data.get("topic", ""),
            summary=data.get("summary", ""),
            theme=data.get("theme", ""),
            characters=characters,
            chapters=chapters,
            memory=memory,
            narrative_style=data.get(
                "narrative_style",
                ""
            ),
            perspective=data.get(
                "perspective",
                ""
            ),
            tense=data.get(
                "tense",
                ""
            )
        )

    def _deserialize_chapter(
        self,
        data: dict
    ) -> Chapter:

        scenes = [
            self._deserialize_scene(scene)
            for scene in data.get(
                "scenes",
                []
            )
        ]

        return Chapter(
            number=data.get("number", 0),
            title=data.get("title", ""),
            goal=data.get("goal", ""),
            revelation=data.get(
                "revelation",
                ""
            ),
            ending_hook=data.get(
                "ending_hook",
                ""
            ),
            scenes=scenes,
            final_text=data.get(
                "final_text",
                ""
            ),
            critic_evaluation=data.get(
                "critic_evaluation",
                {}
            ),
            continuity_check=data.get(
                "continuity_check",
                {}
            )
        )

    def _deserialize_scene(
        self,
        data: dict
    ) -> Scene:

        return Scene(
            number=data.get("number", 0),
            title=data.get("title", ""),
            location=data.get(
                "location",
                ""
            ),
            goal=data.get(
                "goal",
                ""
            ),
            conflict=data.get(
                "conflict",
                ""
            ),
            ending=data.get(
                "ending",
                ""
            ),
            participating_characters=data.get(
                "participating_characters",
                []
            ),
            character_states=data.get(
                "character_states",
                {}
            ),
            summary=data.get(
                "summary",
                ""
            ),
            prose=data.get(
                "prose",
                ""
            ),
            pov=data.get(
                "pov",
                ""
            )
        )

    def _deserialize_character(
        self,
        data: dict
    ) -> Character:

        return Character(
            name=data.get(
                "name",
                ""
            ),
            role=data.get(
                "role",
                ""
            ),
            personality=data.get(
                "personality",
                ""
            ),
            motivation=data.get(
                "motivation",
                ""
            ),
            backstory=data.get(
                "backstory",
                ""
            ),
            speech_profile=data.get(
                "speech_profile",
                {}
            ),
            strengths=data.get(
                "strengths",
                []
            ),
            weaknesses=data.get(
                "weaknesses",
                []
            ),
            knowledge=data.get(
                "knowledge",
                []
            ),
            beliefs=data.get(
                "beliefs",
                []
            ),
            secrets=data.get(
                "secrets",
                []
            ),
            current_location=data.get(
                "current_location",
                ""
            ),
            current_goal=data.get(
                "current_goal",
                ""
            ),
            current_emotion=data.get(
                "current_emotion",
                ""
            ),
            relationships=data.get(
                "relationships",
                {}
            )
        )

    def _deserialize_memory(
        self,
        data: dict
    ) -> StoryMemory:

        return StoryMemory(
            summary=data.get(
                "summary",
                ""
            ),
            last_scene_summary=data.get(
                "last_scene_summary",
                ""
            ),
            character_states=data.get(
                "character_states",
                {}
            ),
            open_threads=data.get(
                "open_threads",
                []
            ),
            important_objects=data.get(
                "important_objects",
                []
            ),
            conflicts=data.get(
                "conflicts",
                []
            ),
            theme_progress=data.get(
                "theme_progress",
                ""
            )
        )

    def _checkpoint_path(
        self,
        story: Story
    ) -> Path:

        safe_title = (
            story.title
            .strip()
            .lower()
            .replace(" ", "_")
        )

        return (
            self.checkpoint_directory
            / f"{safe_title}_checkpoint.json"
        )

