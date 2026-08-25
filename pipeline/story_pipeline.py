from models.story import Story
from models.memory import StoryMemory

from agents.story_director import StoryDirector
from agents.final_editor import FinalEditor

from pipeline.chapter_pipeline import ChapterPipeline
from pipeline.checkpoint_manager import CheckpointManager


class StoryPipeline:
    """
    Coordinates the complete lifecycle of a story.

    Responsibilities:
    - Create the initial story structure
    - Initialize story memory
    - Generate chapters sequentially
    - Maintain global story state
    - Pass chapters through ChapterPipeline
    - Perform final manuscript editing
    - Save and recover story checkpoints

    StoryPipeline is responsible for orchestration only.
    The individual agents are responsible for their own reasoning.
    """

    def __init__(
        self,
        llm,
        story_director: StoryDirector | None = None,
        chapter_pipeline: ChapterPipeline | None = None,
        final_editor: FinalEditor | None = None,
        checkpoint_manager: CheckpointManager | None = None
    ):
        self.llm = llm

        self.story_director = (
            story_director
            or StoryDirector(llm)
        )

        self.chapter_pipeline = (
            chapter_pipeline
            or ChapterPipeline(llm)
        )

        self.final_editor = (
            final_editor
            or FinalEditor(llm)
        )

        self.checkpoint_manager = (
            checkpoint_manager
            or CheckpointManager()
        )

    def run(self, topic: str) -> Story:
        """
        Generates or resumes a complete story from a given topic.

        Flow:

        Topic
          ↓
        Checkpoint?
          ↓
        Story Director / Load Story
          ↓
        Story Memory
          ↓
        Chapter Pipeline
          ↓
        Checkpoint
          ↓
        More Chapters
          ↓
        Final Editor
          ↓
        Completed Story
        """

        story = self.checkpoint_manager.load(topic)

        if story is None:

            story = self.story_director.create_story(
                topic
            )

            memory = self._initialize_memory(
                story
            )

            story.memory = memory
            story.status = "in_progress"

            self.checkpoint_manager.save(
                story
            )

        else:

            memory = story.memory

            if memory is None:

                memory = self._initialize_memory(
                    story
                )

                story.memory = memory

        for chapter in story.chapters:

            if chapter.final_text:
                continue

            completed_chapter = self.chapter_pipeline.run(
                story,
                chapter,
                memory
            )

            self._store_completed_chapter(
                story,
                completed_chapter
            )

            memory = self._update_story_memory(
                memory,
                completed_chapter
            )

            story.memory = memory

            # Save after every completed chapter
            self.checkpoint_manager.save(
                story
            )

        story = self._finalize_story(
            story,
            memory
        )

        story.status = "completed"

        self.checkpoint_manager.save(
            story
        )

        return story

    def _initialize_memory(
        self,
        story: Story
    ) -> StoryMemory:
        """
        Creates the initial long-term memory for the story.
        """

        memory = StoryMemory()

        memory.summary = story.summary

        memory.character_states = {
            character.name: {
                "location": character.current_location,
                "goal": character.current_goal,
                "emotion": character.current_emotion
            }
            for character in story.characters
        }

        memory.open_threads = []

        memory.important_objects = []

        memory.conflicts = []

        memory.theme_progress = story.theme

        return memory

    def _store_completed_chapter(
        self,
        story: Story,
        chapter
    ) -> None:
        """
        Stores the completed chapter inside the story.

        The chapter object already exists inside story.chapters,
        so this method updates the matching chapter rather than
        creating a duplicate.
        """

        for index, existing_chapter in enumerate(
            story.chapters
        ):

            if existing_chapter.number == chapter.number:

                story.chapters[index] = chapter

                return

    def _update_story_memory(
        self,
        memory: StoryMemory,
        chapter
    ) -> StoryMemory:
        """
        Updates global story memory after a chapter finishes.

        Chapter-level memory updates are already performed by
        ChapterPipeline. This method maintains story-level state.
        """

        if chapter.final_text:

            memory.last_scene_summary = (
                chapter.final_text[-1000:]
            )

        return memory

    def _finalize_story(
        self,
        story: Story,
        memory: StoryMemory
    ) -> Story:
        """
        Sends the completed manuscript to the Final Editor.
        """

        story.memory = memory

        story = self.final_editor.edit(
            story,
            memory
        )

        return story
