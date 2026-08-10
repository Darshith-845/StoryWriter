import json

from models.scene import Scene
from models.chapter import Chapter
from models.story import Story
from models.memory import StoryMemory


class Critic:

    def __init__(self, llm):
        self.llm = llm

    def evaluate(
        self,
        story: Story,
        chapter: Chapter,
        scene: Scene,
        memory: StoryMemory,
        prose: str
    ) -> dict:
        """
        Evaluate a generated scene.

        The Critic does not modify or rewrite the scene.
        It only evaluates the prose and returns structured
        feedback for the orchestration layer.
        """

        prompt = self._build_prompt(
            story,
            chapter,
            scene,
            memory,
            prose
        )

        response = self.llm.generate(prompt)

        return self._parse_response(response)

    def _build_prompt(
        self,
        story: Story,
        chapter: Chapter,
        scene: Scene,
        memory: StoryMemory,
        prose: str
    ) -> str:

        story_context = self._build_story_context(story)
        chapter_context = self._build_chapter_context(chapter)
        scene_context = self._build_scene_context(scene)
        memory_context = self._build_memory_context(memory)

        return f"""
You are the Critic Agent in an autonomous long-form
fiction generation system.

Your responsibility is to evaluate a generated scene.

You are an evaluator.

DO NOT rewrite the scene.

DO NOT improve the prose.

DO NOT generate replacement paragraphs.

DO NOT continue the story.

Your task is to identify strengths, weaknesses,
continuity problems, and areas that require revision.

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
LONG-TERM MEMORY
============================================================

{memory_context}

============================================================
GENERATED SCENE
============================================================

{prose}

============================================================
EVALUATION CRITERIA
============================================================

Evaluate the scene using the following dimensions.

------------------------------------------------------------
1. SCENE GOAL
------------------------------------------------------------

Did the scene accomplish its intended objective?

Consider:

- Whether the scene goal was actually addressed
- Whether character actions contribute toward that goal
- Whether the scene feels purposeful

------------------------------------------------------------
2. CHARACTER CONSISTENCY
------------------------------------------------------------

Evaluate whether characters behave consistently with:

- personality
- motivations
- beliefs
- knowledge
- emotional state
- relationships
- established behavior

Characters should not suddenly behave differently
without a convincing narrative reason.

------------------------------------------------------------
3. DIALOGUE
------------------------------------------------------------

Evaluate:

- character-specific voice
- naturalness
- conversational flow
- subtext
- vocabulary
- speech patterns
- age-appropriate language
- emotional authenticity

Characters should not sound interchangeable.

------------------------------------------------------------
4. EMOTIONAL PROGRESSION
------------------------------------------------------------

Evaluate whether emotions:

- develop naturally
- respond to events
- affect character decisions
- create meaningful progression

Avoid arbitrary emotional changes.

------------------------------------------------------------
5. PACING
------------------------------------------------------------

Evaluate:

- scene momentum
- unnecessary exposition
- repetitive passages
- excessive description
- rushed events
- overly slow sections

The scene should spend its narrative attention
on meaningful events.

------------------------------------------------------------
6. CONFLICT
------------------------------------------------------------

Evaluate whether the central conflict:

- is clear
- creates tension
- affects character decisions
- develops during the scene
- contributes to the broader narrative

------------------------------------------------------------
7. CONTINUITY
------------------------------------------------------------

Check against the supplied memory.

Look for:

- timeline contradictions
- character state contradictions
- location inconsistencies
- forgotten events
- impossible knowledge
- contradictory relationships
- inconsistent objects
- unresolved information being incorrectly resolved

Do not invent continuity problems that are not supported
by the supplied context.

------------------------------------------------------------
8. PROSE QUALITY
------------------------------------------------------------

Evaluate:

- clarity
- readability
- sentence variation
- descriptive balance
- narrative voice
- unnecessary repetition
- awkward phrasing
- excessive exposition

------------------------------------------------------------
9. ENDING
------------------------------------------------------------

Evaluate whether the scene reaches its intended ending.

Consider whether the ending:

- follows naturally from the scene
- creates forward momentum
- respects the planned ending
- provides an appropriate transition

============================================================
SCORING
============================================================

Score each category from 1 to 10.

1 = extremely poor

5 = acceptable but needs improvement

10 = excellent

Calculate an overall score based on the evaluation.

A scene should PASS only if:

- overall score >= 7
- no major continuity problems exist
- no major character consistency problems exist
- the scene goal is substantially achieved

============================================================
IMPORTANT
============================================================

Be critical.

Do not give high scores merely because the prose
sounds fluent.

A grammatically correct scene can still have:

- weak characterization
- poor pacing
- meaningless dialogue
- continuity errors
- weak conflict
- no narrative purpose

Focus on whether the scene works as part of
a larger long-form narrative.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_score": 0,

    "passed": false,

    "scores": {{
        "scene_goal": 0,
        "character_consistency": 0,
        "dialogue": 0,
        "emotional_progression": 0,
        "pacing": 0,
        "conflict": 0,
        "continuity": 0,
        "prose_quality": 0,
        "ending": 0
    }},

    "strengths": [
        "..."
    ],

    "issues": [
        {{
            "category": "...",
            "severity": "minor",
            "description": "..."
        }}
    ],

    "revision_instructions": [
        "..."
    ]
}}

Severity must be one of:

- minor
- moderate
- major

Do not include any text outside the JSON object.
"""

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

    def _build_chapter_context(
        self,
        chapter: Chapter
    ) -> str:

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

    def _build_scene_context(
        self,
        scene: Scene
    ) -> str:

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

Character States:
{scene.character_states}

Scene Summary:
{scene.summary}
"""

    def _build_memory_context(
        self,
        memory: StoryMemory
    ) -> str:

        return f"""
Story Summary:
{memory.summary}

Last Scene Summary:
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

    def _parse_response(
        self,
        response: str
    ) -> dict:

        try:
            cleaned = self._clean_json(response)

            data = json.loads(cleaned)

            return self._validate_response(data)

        except (json.JSONDecodeError, TypeError, ValueError):
            return self._default_response()

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

    # ------------------------------------------------------------------
    # Response Validation
    # ------------------------------------------------------------------

    def _validate_response(
        self,
        data: dict
    ) -> dict:

        if not isinstance(data, dict):
            return self._default_response()

        scores = data.get("scores", {})

        if not isinstance(scores, dict):
            scores = {}

        score_fields = [
            "scene_goal",
            "character_consistency",
            "dialogue",
            "emotional_progression",
            "pacing",
            "conflict",
            "continuity",
            "prose_quality",
            "ending"
        ]

        for field in score_fields:

            value = scores.get(field, 0)

            if not isinstance(value, (int, float)):
                value = 0

            value = max(0, min(10, value))

            scores[field] = value

        data["scores"] = scores

        overall_score = data.get("overall_score", 0)

        if not isinstance(overall_score, (int, float)):
            overall_score = 0

        overall_score = max(
            0,
            min(10, overall_score)
        )

        data["overall_score"] = overall_score

        data["passed"] = bool(
            data.get("passed", False)
        )

        if not isinstance(
            data.get("strengths"),
            list
        ):
            data["strengths"] = []

        if not isinstance(
            data.get("issues"),
            list
        ):
            data["issues"] = []

        if not isinstance(
            data.get("revision_instructions"),
            list
        ):
            data["revision_instructions"] = []

        return data

    def _default_response(self) -> dict:

        return {
            "overall_score": 0,

            "passed": False,

            "scores": {
                "scene_goal": 0,
                "character_consistency": 0,
                "dialogue": 0,
                "emotional_progression": 0,
                "pacing": 0,
                "conflict": 0,
                "continuity": 0,
                "prose_quality": 0,
                "ending": 0
            },

            "strengths": [],

            "issues": [
                {
                    "category": "critic",
                    "severity": "major",
                    "description": (
                        "The Critic failed to produce "
                        "a valid evaluation."
                    )
                }
            ],

            "revision_instructions": [
                "Re-evaluate the generated scene."
            ]
        }

    # ------------------------------------------------------------------
    # Formatting Helpers
    # ------------------------------------------------------------------

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