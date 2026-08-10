import json

from models.story import Story
from models.chapter import Chapter
from models.memory import StoryMemory


class FinalEditor:

    def __init__(self, llm):
        self.llm = llm

    def edit(
        self,
        story: Story,
        chapters: list[Chapter],
        memory: StoryMemory
    ) -> dict:
        """
        Perform a developmental edit over the completed manuscript.

        The Final Editor improves the existing manuscript while
        preserving the core story, characters, events, and ending.

        It does not generate an entirely new story.
        """

        prompt = self._build_prompt(
            story,
            chapters,
            memory
        )

        response = self.llm.generate(prompt)

        return self._parse_response(response)

    # ------------------------------------------------------------------
    # Prompt Construction
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        story: Story,
        chapters: list[Chapter],
        memory: StoryMemory
    ) -> str:

        story_context = self._build_story_context(story)
        manuscript = self._build_manuscript(chapters)
        memory_context = self._build_memory_context(memory)

        return f"""
You are the Final Developmental Editor of an autonomous
long-form fiction generation system.

The complete manuscript has already been generated.

Your responsibility is to perform a developmental edit.

You must improve the manuscript while preserving its
fundamental identity.

============================================================
STORY
============================================================

{story_context}

============================================================
LONG-TERM STORY MEMORY
============================================================

{memory_context}

============================================================
COMPLETE MANUSCRIPT
============================================================

{manuscript}

============================================================
EDITORIAL OBJECTIVES
============================================================

Evaluate and improve:

1. STORY STRUCTURE

Check:

- overall progression
- beginning, middle and ending
- chapter progression
- escalation of conflict
- payoff of major events
- pacing

------------------------------------------------------------

2. CHARACTER DEVELOPMENT

Check:

- character arcs
- motivations
- emotional progression
- consistency
- meaningful character decisions

Characters should evolve naturally rather than changing
without cause.

------------------------------------------------------------

3. NARRATIVE FLOW

Check:

- chapter transitions
- scene transitions
- pacing
- unnecessary repetition
- abrupt jumps
- slow sections

------------------------------------------------------------

4. CONTINUITY

Check:

- character consistency
- timeline consistency
- locations
- relationships
- objects
- unresolved contradictions

------------------------------------------------------------

5. DIALOGUE

Check:

- character-specific voices
- natural dialogue
- unnecessary exposition
- repetitive dialogue patterns
- dialogue that does not advance the story

Preserve established speech characteristics.

------------------------------------------------------------

6. EMOTIONAL PROGRESSION

Check:

- emotional buildup
- emotional payoff
- character reactions
- tension
- important emotional turning points

------------------------------------------------------------

7. THEMATIC COHERENCE

Check whether the story's themes remain meaningful
throughout the manuscript.

Do not force additional themes.

------------------------------------------------------------

8. REPETITION

Remove unnecessary repetition of:

- information
- descriptions
- emotions
- dialogue
- internal thoughts
- exposition

============================================================
EDITORIAL RULES
============================================================

1. Do not completely rewrite the story.

2. Do not change the fundamental premise.

3. Do not introduce unrelated characters.

4. Do not introduce unrelated plot lines.

5. Do not remove important story events without reason.

6. Do not change the intended ending.

7. Do not arbitrarily change character personalities.

8. Preserve intentional stylistic choices.

9. Preserve character-specific dialogue styles.

10. Fix contradictions when possible.

11. Strengthen weak transitions.

12. Improve pacing where necessary.

13. Preserve the author's narrative voice.

14. Do not add information that contradicts story memory.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_assessment": "...",

    "structural_issues": [
        "..."
    ],

    "character_issues": [
        "..."
    ],

    "continuity_issues": [
        "..."
    ],

    "pacing_issues": [
        "..."
    ],

    "dialogue_issues": [
        "..."
    ],

    "thematic_issues": [
        "..."
    ],

    "recommended_changes": [
        {{
            "chapter": 1,
            "issue": "...",
            "recommendation": "..."
        }}
    ],

    "chapter_edits": [
        {{
            "chapter": 1,
            "edited_text": "..."
        }}
    ],

    "final_assessment": {{
        "structure": 0,
        "characterization": 0,
        "pacing": 0,
        "continuity": 0,
        "dialogue": 0,
        "emotional_progression": 0,
        "thematic_coherence": 0,
        "overall": 0
    }}
}}

Scores must be between 0 and 100.

Important:

The "chapter_edits" field should contain edited chapter text
only when meaningful changes are required.

If a chapter does not require editing, return its original
text unchanged.

Do not include explanations outside the JSON object.
"""

    # ------------------------------------------------------------------
    # Story Context
    # ------------------------------------------------------------------

    def _build_story_context(
        self,
        story: Story
    ) -> str:

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

    def _build_manuscript(
        self,
        chapters: list[Chapter]
    ) -> str:

        if not chapters:
            return "No chapters available."

        sections = []

        for chapter in chapters:

            chapter_text = chapter.final_text

            if not chapter_text:
                chapter_text = self._build_chapter_from_scenes(
                    chapter
                )

            sections.append(
                f"""
============================================================
CHAPTER {chapter.number}: {chapter.title}
============================================================

Chapter Goal:
{chapter.goal}

Revelation:
{chapter.revelation}

Ending Hook:
{chapter.ending_hook}

Chapter Text:

{chapter_text}
"""
            )

        return "\n".join(sections)

    def _build_chapter_from_scenes(
        self,
        chapter: Chapter
    ) -> str:

        if not chapter.scenes:
            return ""

        scene_sections = []

        for scene in chapter.scenes:

            scene_sections.append(
                f"""
[Scene {scene.number}: {scene.title}]

Location:
{scene.location}

Goal:
{scene.goal}

Conflict:
{scene.conflict}

POV:
{scene.pov}

{scene.prose}
"""
            )

        return "\n".join(scene_sections)

    # ------------------------------------------------------------------
    # Memory Context
    # ------------------------------------------------------------------

    def _build_memory_context(
        self,
        memory: StoryMemory
    ) -> str:

        return f"""
Story Summary:
{memory.summary}

Character States:
{self._format_dict(memory.character_states)}

Open Threads:
{self._format_list(memory.open_threads)}

Important Objects:
{self._format_list(memory.important_objects)}

Conflicts:
{self._format_list(memory.conflicts)}

Theme Progression:
{memory.theme_progress}
"""

    # ------------------------------------------------------------------
    # Response Parsing
    # ------------------------------------------------------------------

    def _parse_response(
        self,
        response: str
    ) -> dict:

        try:

            cleaned = self._clean_json(response)

            data = json.loads(cleaned)

            return self._validate_response(data)

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):
            return self._default_response()

    def _validate_response(
        self,
        data: dict
    ) -> dict:

        if not isinstance(data, dict):
            return self._default_response()

        assessment = data.get(
            "final_assessment",
            {}
        )

        if not isinstance(assessment, dict):
            assessment = {}

        validated_assessment = {}

        score_fields = [
            "structure",
            "characterization",
            "pacing",
            "continuity",
            "dialogue",
            "emotional_progression",
            "thematic_coherence",
            "overall"
        ]

        for field in score_fields:

            try:
                score = int(
                    assessment.get(field, 0)
                )
            except (TypeError, ValueError):
                score = 0

            validated_assessment[field] = max(
                0,
                min(100, score)
            )

        return {
            "overall_assessment": data.get(
                "overall_assessment",
                ""
            ),

            "structural_issues": self._ensure_list(
                data.get("structural_issues", [])
            ),

            "character_issues": self._ensure_list(
                data.get("character_issues", [])
            ),

            "continuity_issues": self._ensure_list(
                data.get("continuity_issues", [])
            ),

            "pacing_issues": self._ensure_list(
                data.get("pacing_issues", [])
            ),

            "dialogue_issues": self._ensure_list(
                data.get("dialogue_issues", [])
            ),

            "thematic_issues": self._ensure_list(
                data.get("thematic_issues", [])
            ),

            "recommended_changes": self._ensure_list(
                data.get("recommended_changes", [])
            ),

            "chapter_edits": self._ensure_list(
                data.get("chapter_edits", [])
            ),

            "final_assessment": validated_assessment
        }

    def _default_response(self) -> dict:

        return {
            "overall_assessment": (
                "Final editing could not be completed."
            ),

            "structural_issues": [],
            "character_issues": [],
            "continuity_issues": [],
            "pacing_issues": [],
            "dialogue_issues": [],
            "thematic_issues": [],
            "recommended_changes": [],
            "chapter_edits": [],

            "final_assessment": {
                "structure": 0,
                "characterization": 0,
                "pacing": 0,
                "continuity": 0,
                "dialogue": 0,
                "emotional_progression": 0,
                "thematic_coherence": 0,
                "overall": 0
            }
        }

    def _clean_json(
        self,
        response: str
    ) -> str:

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

        return response.strip()

    def _format_list(
        self,
        values
    ) -> str:

        if not values:
            return "None"

        if isinstance(values, str):
            return values

        return "\n".join(
            f"- {value}"
            for value in values
        )

    def _format_dict(
        self,
        values
    ) -> str:

        if not values:
            return "None"

        if isinstance(values, str):
            return values

        return "\n".join(
            f"- {key}: {value}"
            for key, value in values.items()
        )

    def _ensure_list(
        self,
        value
    ) -> list:

        if isinstance(value, list):
            return value

        if value is None:
            return []

        return [value]
