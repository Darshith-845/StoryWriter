from models.story import Story
from models.memory import StoryMemory

from agents.story_director import StoryDirector
from agents.final_editor import FinalEditor

from pipeline.chapter_pipeline import ChapterPipeline


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

    StoryPipeline is responsible for orchestration only.
    The individual agents are responsible for their own reasoning.
    """

    def __init__(
        self,
        llm,
        story_director: StoryDirector | None = None,
        chapter_pipeline: ChapterPipeline | None = None,
        final_editor: FinalEditor | None = None
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

    # ================================================================
    # PUBLIC API
    # ================================================================

    def run(self, topic: str) -> Story:
        """
        Generates a complete story from a given topic.

        Flow:

        Topic
          ↓
        Story Director
          ↓
        Story
          ↓
        Story Memory
          ↓
        Chapter Pipeline
          ↓
        Completed Chapters
          ↓
        Final Editor
          ↓
        Completed Story
        """

        story = self.story_director.create_story(
            topic
        )

        memory = self._initialize_memory(
            story
        )

        story.memory = memory

        for chapter in story.chapters:

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

        story = self._finalize_story(
            story,
            memory
        )

        return story

    # ================================================================
    # MEMORY INITIALIZATION
    # ================================================================

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

    # ================================================================
    # CHAPTER MANAGEMENT
    # ================================================================

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

    # ================================================================
    # STORY MEMORY
    # ================================================================

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

    # ================================================================
    # FINALIZATION
    # ================================================================

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

