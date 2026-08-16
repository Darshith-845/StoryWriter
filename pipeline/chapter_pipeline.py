from models.story import Story
from models.chapter import Chapter
from models.memory import StoryMemory

from agents.chapter_director import ChapterDirector
from agents.scene_planner import ScenePlanner
from agents.character_simulator import CharacterSimulator
from agents.scene_composer import SceneComposer
from agents.critic import Critic
from agents.memory_manager import MemoryManager
from agents.continuity_editor import ContinuityEditor


class ChapterPipeline:
    """
    Coordinates the complete generation lifecycle of a chapter.

    Responsibilities:
    - Direct the chapter
    - Plan scenes
    - Simulate participating characters
    - Compose scenes
    - Evaluate generated scenes
    - Update long-term memory
    - Perform continuity verification

    This class coordinates agents but does not contain
    the reasoning logic of those agents.
    """

    def __init__(
        self,
        llm,
        chapter_director: ChapterDirector | None = None,
        scene_planner: ScenePlanner | None = None,
        character_simulator: CharacterSimulator | None = None,
        scene_composer: SceneComposer | None = None,
        critic: Critic | None = None,
        memory_manager: MemoryManager | None = None,
        continuity_editor: ContinuityEditor | None = None
    ):
        self.llm = llm

        self.chapter_director = (
            chapter_director
            or ChapterDirector(llm)
        )

        self.scene_planner = (
            scene_planner
            or ScenePlanner(llm)
        )

        self.character_simulator = (
            character_simulator
            or CharacterSimulator(llm)
        )

        self.scene_composer = (
            scene_composer
            or SceneComposer(llm)
        )

        self.critic = (
            critic
            or Critic(llm)
        )

        self.memory_manager = (
            memory_manager
            or MemoryManager(llm)
        )

        self.continuity_editor = (
            continuity_editor
            or ContinuityEditor(llm)
        )

    def run(
        self,
        story: Story,
        chapter: Chapter,
        memory: StoryMemory
    ) -> Chapter:

        chapter_direction = self.chapter_director.direct(
            story,
            chapter,
            memory
        )

        scenes = self.scene_planner.plan(
            story,
            chapter,
            chapter_direction,
            memory
        )

        chapter.scenes = scenes

        for scene in chapter.scenes:

            character_states = self._simulate_characters(
                story,
                scene,
                memory
            )

            scene.character_states = character_states

            scene.prose = self.scene_composer.compose(
                story,
                scene,
                character_states,
                memory
            )

            evaluation = self.critic.evaluate(
                story,
                scene,
                memory
            )

            scene = self._handle_critique(
                story,
                scene,
                evaluation,
                character_states,
                memory
            )

            chapter.scenes[
                scene.number - 1
            ] = scene

            memory = self.memory_manager.update(
                story,
                scene,
                memory
            )

        continuity_result = self.continuity_editor.check(
            story,
            chapter,
            memory
        )

        chapter = self._apply_continuity_result(
            chapter,
            continuity_result
        )

        chapter.final_text = self._assemble_chapter(
            chapter
        )

        return chapter


    def _simulate_characters(
        self,
        story: Story,
        scene,
        memory: StoryMemory
    ) -> dict:

        character_states = {}

        for character_name in scene.participating_characters:

            character = self._find_character(
                story,
                character_name
            )

            if character is None:
                continue

            state = self.character_simulator.simulate(
                character,
                scene,
                story,
                memory
            )

            character_states[character_name] = state

        return character_states

    def _handle_critique(
        self,
        story: Story,
        scene,
        evaluation: dict,
        character_states: dict,
        memory: StoryMemory
    ):
        """
        Handles critic output.

        The Critic only evaluates.

        Rewriting responsibility can be added later through
        a dedicated Scene Rewriter agent.
        """

        scene.critic_evaluation = evaluation

        return scene

    def _apply_continuity_result(
        self,
        chapter: Chapter,
        continuity_result: dict
    ) -> Chapter:

        chapter.continuity_check = continuity_result

        return chapter

    def _assemble_chapter(
        self,
        chapter: Chapter
    ) -> str:

        sections = []

        for scene in chapter.scenes:

            if not scene.prose:
                continue

            sections.append(
                scene.prose.strip()
            )

        return "\n\n".join(sections)

    def _find_character(
        self,
        story: Story,
        character_name: str
    ):

        for character in story.characters:

            if character.name == character_name:
                return character

        return None

