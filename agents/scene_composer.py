from models.scene import Scene
from models.chapter import Chapter
from models.story import Story
from models.memory import StoryMemory


class SceneComposer:

    def __init__(self, llm):
        self.llm = llm

    def compose(
        self,
        story: Story,
        chapter: Chapter,
        scene: Scene,
        memory: StoryMemory,
        character_outputs: list[dict]
    ) -> str:
        """
        Compose the final prose for a scene.

        The Scene Composer does not decide what should happen.
        It transforms the decisions made by the Story Director,
        Scene Planner, and Character Simulator into literary prose.
        """

        prompt = self._build_prompt(
            story,
            chapter,
            scene,
            memory,
            character_outputs
        )

        response = self.llm.generate(prompt)

        return self._clean_output(response)

    # ------------------------------------------------------------------
    # Prompt Construction
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        story: Story,
        chapter: Chapter,
        scene: Scene,
        memory: StoryMemory,
        character_outputs: list[dict]
    ) -> str:

        story_context = self._build_story_context(story)
        chapter_context = self._build_chapter_context(chapter)
        scene_context = self._build_scene_context(scene)
        character_context = self._build_character_context(
            character_outputs
        )
        memory_context = self._build_memory_context(memory)

        return f"""
You are the Scene Composer in an autonomous long-form
fiction generation system.

Your task is to transform a structured scene plan and
character simulations into polished literary prose.

You are NOT the story planner.

You are NOT the character planner.

You are NOT the critic.

Those decisions have already been made.

Your responsibility is to WRITE THE SCENE.

============================================================
STORY CONTEXT
============================================================

{story_context}

============================================================
CHAPTER CONTEXT
============================================================

{chapter_context}

============================================================
SCENE PLAN
============================================================

{scene_context}

============================================================
CHARACTER SIMULATIONS
============================================================

{character_context}

============================================================
STORY MEMORY
============================================================

{memory_context}

============================================================
WRITING REQUIREMENTS
============================================================

1. Follow the scene objective exactly.

2. Preserve the planned conflict.

3. Preserve the intended ending.

4. Do not introduce major events that are not supported
   by the scene plan or character simulations.

5. Keep every character consistent with their personality,
   motivations, beliefs, knowledge, secrets, emotional state,
   and speech profile.

6. Characters must NOT know information that they have not
   previously learned.

7. Dialogue must reflect each character's individual
   speech profile.

8. Do not make every character sound the same.

9. Use body language and physical behavior naturally.

10. Show emotions through actions, reactions, thoughts,
    expressions, and dialogue rather than repeatedly
    stating emotions directly.

11. Preserve continuity with the supplied story memory.

12. Do not resolve unrelated open plot threads unless
    the scene explicitly requires it.

13. Maintain the established narrative perspective,
    tense, voice, and style.

14. Avoid unnecessary exposition.

15. Avoid repetitive descriptions.

16. Avoid generic dialogue.

17. Do not summarize the scene.

18. Write the actual scene as finished fiction.

============================================================
DIALOGUE REQUIREMENTS
============================================================

Dialogue is one of the primary mechanisms through which
the reader should understand a character.

Each character should have a recognizable voice.

Consider:

- vocabulary
- sentence length
- grammatical complexity
- formality
- emotional restraint
- verbal habits
- cultural influence
- age
- education
- confidence
- personality
- relationship with the listener

Do not turn speech profiles into caricatures.

If a character speaks imperfect English, preserve that quality
naturally without making every sentence artificially incorrect.

A child should generally use language appropriate to their age.

A highly educated character may use more precise vocabulary.

A nervous character may hesitate.

A confident character may speak directly.

These traits should emerge naturally through dialogue.

============================================================
CHARACTER INTERNAL REASONING
============================================================

Character simulations contain internal reasoning.

Do not expose private thoughts mechanically as a list.

Convert them into natural narrative when appropriate.

A character's internal reasoning may influence:

- what they notice
- what they say
- what they avoid saying
- what they misunderstand
- what they decide
- how they react

Do not reveal secrets simply because they exist in the
character simulation.

A secret remains hidden unless the character has a reason
to reveal it or the narrative explicitly allows the reader
to know it.

============================================================
SCENE STRUCTURE
============================================================

The scene should have natural progression:

1. Establish the immediate situation.

2. Introduce character interaction.

3. Develop the scene objective.

4. Escalate the conflict.

5. Allow character decisions and reactions to shape
   the interaction.

6. Build toward the planned ending.

7. Finish on the intended ending or hook.

Do not force every scene into the same rhythm.

============================================================
PROSE STYLE
============================================================

Write polished long-form fiction.

Use:

- natural paragraphs
- varied sentence structure
- sensory details where useful
- meaningful physical actions
- subtext
- natural dialogue
- controlled pacing

Avoid:

- excessive adjectives
- purple prose
- repetitive emotional descriptions
- exposition dumps
- artificial dialogue
- screenplay formatting
- bullet points
- headings inside the scene
- meta-commentary

============================================================
OUTPUT FORMAT
============================================================

Return ONLY the finished prose of the scene.

Do not return:

- JSON
- Markdown
- explanations
- analysis
- character notes
- scene summaries
- labels such as "Scene:"
- comments about the writing process

Begin directly with the scene.
"""

    # ------------------------------------------------------------------
    # Context Builders
    # ------------------------------------------------------------------

    def _build_story_context(self, story: Story) -> str:
        """
        Builds the high-level narrative context.
        """

        return f"""
Title:
{getattr(story, "title", "")}

Premise:
{getattr(story, "premise", "")}

Theme:
{getattr(story, "theme", "")}

Setting:
{getattr(story, "setting", "")}

Narrative Style:
{getattr(story, "narrative_style", "")}

Point of View:
{getattr(story, "pov", "")}

Tense:
{getattr(story, "tense", "")}
"""

    def _build_chapter_context(self, chapter: Chapter) -> str:
        """
        Builds context specific to the current chapter.
        """

        return f"""
Chapter Number:
{chapter.number}

Chapter Title:
{chapter.title}

Chapter Goal:
{chapter.goal}

Chapter Revelation:
{chapter.revelation}

Chapter Ending Hook:
{chapter.ending_hook}
"""

    def _build_scene_context(self, scene: Scene) -> str:
        """
        Builds the structured scene plan.
        """

        return f"""
Scene Number:
{scene.number}

Scene Title:
{scene.title}

Location:
{scene.location}

POV:
{scene.pov}

Scene Goal:
{scene.goal}

Conflict:
{scene.conflict}

Planned Ending:
{scene.ending}

Participating Characters:
{scene.participating_characters}

Existing Scene Summary:
{scene.summary}
"""

    def _build_character_context(
        self,
        character_outputs: list[dict]
    ) -> str:
        """
        Converts Character Simulator outputs into instructions
        that the prose generator can use.
        """

        if not character_outputs:
            return "No character simulations were provided."

        sections = []

        for index, character in enumerate(character_outputs, start=1):

            section = f"""
CHARACTER {index}

Name:
{character.get("character", "Unknown")}

Current Goal:
{character.get("goal", "")}

Current Emotion:
{character.get("emotion", "")}

Internal Thoughts:
{character.get("thoughts", "")}

Decision:
{character.get("decision", "")}

Action Plan:
{self._format_list(character.get("action_plan", []))}

Dialogue Style:
{character.get("dialogue_style", "")}

Body Language:
{character.get("body_language", "")}

Dialogue Examples:
{self._format_list(character.get("dialogue_examples", []))}

Relationship Updates:
{self._format_dict(character.get("relationship_updates", {}))}

Knowledge Updates:
{self._format_list(character.get("knowledge_updates", []))}

Belief Updates:
{self._format_list(character.get("belief_updates", []))}

Secret Updates:
{self._format_list(character.get("secret_updates", []))}
"""

            sections.append(section)

        return "\n".join(sections)

    def _build_memory_context(
        self,
        memory: StoryMemory
    ) -> str:
        """
        Builds the relevant long-term narrative memory.
        """

        return f"""
Story Summary:
{memory.summary}

Last Scene:
{memory.last_scene_summary}

Character States:
{self._format_dict(memory.character_states)}

Open Plot Threads:
{self._format_list(memory.open_threads)}

Important Objects:
{self._format_list(memory.important_objects)}

Active Conflicts:
{self._format_list(memory.conflicts)}

Theme Progression:
{memory.theme_progress}
"""

    # ------------------------------------------------------------------
    # Formatting Helpers
    # ------------------------------------------------------------------

    def _format_list(self, values) -> str:
        """
        Formats lists for inclusion in prompts.
        """

        if not values:
            return "None"

        if isinstance(values, str):
            return values

        return "\n".join(
            f"- {value}"
            for value in values
        )

    def _format_dict(self, values) -> str:
        """
        Formats dictionaries for inclusion in prompts.
        """

        if not values:
            return "None"

        if isinstance(values, str):
            return values

        return "\n".join(
            f"- {key}: {value}"
            for key, value in values.items()
        )

    # ------------------------------------------------------------------
    # Output Cleaning
    # ------------------------------------------------------------------

    def _clean_output(self, response: str) -> str:
        """
        Cleans accidental formatting produced by the LLM.
        """

        if not response:
            return ""

        response = response.strip()

        if response.startswith("```"):
            lines = response.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response = "\n".join(lines)

        prefixes = [
            "Scene:",
            "Scene Prose:",
            "Here is the scene:",
            "Here is the completed scene:"
        ]

        for prefix in prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        return response