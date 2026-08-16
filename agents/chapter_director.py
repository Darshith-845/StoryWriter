import json

from models.story import Story
from models.chapter import Chapter
from models.memory import StoryMemory


class ChapterDirector:
    def __init__(self, llm):
        self.llm = llm

    def direct(
        self,
        story: Story,
        chapter: Chapter,
        memory: StoryMemory
    ) -> dict:

        prompt = self._build_prompt(
            story,
            chapter,
            memory
        )

        response = self.llm.generate(
            prompt,
            json_mode=True
        )

        return self._parse_response(response)

    # ------------------------------------------------------------------
    # Prompt Construction
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        story: Story,
        chapter: Chapter,
        memory: StoryMemory
    ) -> str:

        story_context = self._build_story_context(story)
        chapter_context = self._build_chapter_context(chapter)
        memory_context = self._build_memory_context(memory)
        character_context = self._build_character_context(story)

        return f"""
You are the Chapter Director in an autonomous long-form
fiction generation system.

Your job is to direct the dramatic execution of ONE chapter.

You are responsible for deciding:

- what the chapter should accomplish
- how the chapter should emotionally progress
- how tension should escalate
- which major beats should occur
- how characters should change during the chapter
- what information should be revealed
- how the chapter should build toward its ending hook

You are NOT the Scene Planner.

You must NOT create individual scenes.

You must NOT write prose.

You must NOT write dialogue.

You must NOT simulate individual characters.

Your output is a structured chapter direction plan that
will be passed to the Scene Planner.

============================================================
STORY CONTEXT
============================================================

{story_context}

============================================================
CHARACTERS
============================================================

{character_context}

============================================================
CURRENT STORY MEMORY
============================================================

{memory_context}

============================================================
CURRENT CHAPTER
============================================================

{chapter_context}

============================================================
CHAPTER DIRECTION TASK
============================================================

Create a detailed dramatic plan for this chapter.

The chapter should have a clear progression such as:

- Initial state
- Inciting development
- Escalation
- Turning point
- Consequence
- Ending hook

Do not force every chapter to use exactly this structure.
Choose the progression that best serves the chapter.

============================================================
CHAPTER OBJECTIVE
============================================================

The chapter must fulfill:

Goal:
{chapter.goal}

Revelation:
{chapter.revelation}

Ending Hook:
{chapter.ending_hook}

The chapter should advance the larger story rather than
function as an isolated event.

============================================================
CHARACTER PROGRESSION
============================================================

Determine how the important participating characters
should change during this chapter.

Consider:

- current emotional state
- current goals
- fears
- beliefs
- knowledge
- relationships
- conflicts
- decisions they need to make

A character should not change simply because the chapter
requires it. Changes must follow from events and decisions.

============================================================
TENSION AND ESCALATION
============================================================

Determine how tension should develop across the chapter.

Identify:

- what creates tension at the beginning
- what makes the situation more difficult
- what information changes the situation
- what decision raises the stakes
- what consequence leads toward the ending hook

Avoid artificial escalation.

============================================================
INFORMATION CONTROL
============================================================

Determine:

- what the reader should learn
- what characters should learn
- what should remain hidden
- what should be foreshadowed
- what should not yet be revealed

Be especially careful with secrets.

A secret known only to one character must not
accidentally become common knowledge.

============================================================
THEMATIC PROGRESSION
============================================================

Explain how this chapter contributes to the story's
central theme.

The theme should emerge naturally through character
choices and consequences rather than through explicit
lecturing.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "chapter_number": {chapter.number},

    "chapter_purpose": "...",

    "dramatic_arc": {{
        "opening_state": "...",
        "inciting_development": "...",
        "escalation": "...",
        "turning_point": "...",
        "consequence": "...",
        "ending_state": "..."
    }},

    "major_beats": [
        {{
            "order": 1,
            "description": "...",
            "purpose": "...",
            "emotional_effect": "..."
        }}
    ],

    "emotional_progression": {{
        "starting_emotion": "...",
        "middle_emotion": "...",
        "ending_emotion": "..."
    }},

    "character_progression": {{
        "Character Name": {{
            "starting_state": "...",
            "change": "...",
            "ending_state": "..."
        }}
    }},

    "information_flow": {{
        "reader_learns": [],
        "characters_learn": [],
        "secrets_preserved": [],
        "foreshadowing": []
    }},

    "active_conflicts": [
        "..."
    ],

    "thematic_progression": "...",

    "stakes": {{
        "initial_stakes": "...",
        "escalated_stakes": "...",
        "ending_stakes": "..."
    }},

    "ending_transition": "..."
}}

Rules:

- major_beats must be ordered.
- Every major beat must contribute to the chapter purpose.
- The final major beat must prepare the planned ending hook.
- Do not invent characters that do not exist.
- Do not contradict established story memory.
- Do not resolve major story threads unless the chapter
  specifically requires resolution.
- Preserve the established narrative style and structure.
- Do not write prose.
- Do not write dialogue.
- Do not output Markdown.

Return only the JSON object.
"""

    def _build_story_context(
        self,
        story: Story
    ) -> str:

        return f"""
Title:
{getattr(story, "title", "")}

Topic:
{getattr(story, "topic", "")}

World:
{getattr(story, "world", "")}

Theme:
{getattr(story, "theme", "")}

Writing Style:
{getattr(story, "writing_style", "")}

Narrative:
{getattr(story, "narrative", {})}
"""

    def _build_character_context(
        self,
        story: Story
    ) -> str:

        if not story.characters:
            return "No characters available."

        sections = []

        for character in story.characters:

            sections.append(
                f"""
Name:
{character.name}

Role:
{character.role}

Personality:
{character.personality}

Motivation:
{character.motivation}

Backstory:
{character.backstory}

Strengths:
{self._format_list(character.strengths)}

Weaknesses:
{self._format_list(character.weaknesses)}

Knowledge:
{self._format_list(character.knowledge)}

Beliefs:
{self._format_list(character.beliefs)}

Secrets:
{self._format_list(character.secrets)}

Current Location:
{character.current_location}

Current Goal:
{character.current_goal}

Current Emotion:
{character.current_emotion}

Relationships:
{self._format_dict(character.relationships)}

Speech Profile:
{self._format_dict(character.speech_profile)}
"""
            )

        return "\n".join(sections)

    def _build_chapter_context(
        self,
        chapter: Chapter
    ) -> str:

        return f"""
Chapter Number:
{chapter.number}

Title:
{chapter.title}

Goal:
{chapter.goal}

Revelation:
{chapter.revelation}

Ending Hook:
{chapter.ending_hook}
"""

    def _build_memory_context(
        self,
        memory: StoryMemory
    ) -> str:

        return f"""
Summary:
{memory.summary}

Last Scene Summary:
{memory.last_scene_summary}

Character States:
{self._format_dict(memory.character_states)}

Open Threads:
{self._format_list(memory.open_threads)}

Important Objects:
{self._format_list(memory.important_objects)}

Conflicts:
{self._format_list(memory.conflicts)}

Theme Progress:
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

        dramatic_arc = data.get(
            "dramatic_arc",
            {}
        )

        emotional_progression = data.get(
            "emotional_progression",
            {}
        )

        character_progression = data.get(
            "character_progression",
            {}
        )

        information_flow = data.get(
            "information_flow",
            {}
        )

        stakes = data.get(
            "stakes",
            {}
        )

        if not isinstance(dramatic_arc, dict):
            dramatic_arc = {}

        if not isinstance(emotional_progression, dict):
            emotional_progression = {}

        if not isinstance(character_progression, dict):
            character_progression = {}

        if not isinstance(information_flow, dict):
            information_flow = {}

        if not isinstance(stakes, dict):
            stakes = {}

        return {
            "chapter_number": data.get(
                "chapter_number",
                0
            ),

            "chapter_purpose": data.get(
                "chapter_purpose",
                ""
            ),

            "dramatic_arc": {
                "opening_state": dramatic_arc.get(
                    "opening_state",
                    ""
                ),
                "inciting_development": dramatic_arc.get(
                    "inciting_development",
                    ""
                ),
                "escalation": dramatic_arc.get(
                    "escalation",
                    ""
                ),
                "turning_point": dramatic_arc.get(
                    "turning_point",
                    ""
                ),
                "consequence": dramatic_arc.get(
                    "consequence",
                    ""
                ),
                "ending_state": dramatic_arc.get(
                    "ending_state",
                    ""
                )
            },

            "major_beats": self._ensure_list(
                data.get("major_beats", [])
            ),

            "emotional_progression": {
                "starting_emotion": emotional_progression.get(
                    "starting_emotion",
                    ""
                ),
                "middle_emotion": emotional_progression.get(
                    "middle_emotion",
                    ""
                ),
                "ending_emotion": emotional_progression.get(
                    "ending_emotion",
                    ""
                )
            },

            "character_progression":
                character_progression,

            "information_flow": {
                "reader_learns": self._ensure_list(
                    information_flow.get(
                        "reader_learns",
                        []
                    )
                ),
                "characters_learn": self._ensure_list(
                    information_flow.get(
                        "characters_learn",
                        []
                    )
                ),
                "secrets_preserved": self._ensure_list(
                    information_flow.get(
                        "secrets_preserved",
                        []
                    )
                ),
                "foreshadowing": self._ensure_list(
                    information_flow.get(
                        "foreshadowing",
                        []
                    )
                )
            },

            "active_conflicts": self._ensure_list(
                data.get(
                    "active_conflicts",
                    []
                )
            ),

            "thematic_progression": data.get(
                "thematic_progression",
                ""
            ),

            "stakes": {
                "initial_stakes": stakes.get(
                    "initial_stakes",
                    ""
                ),
                "escalated_stakes": stakes.get(
                    "escalated_stakes",
                    ""
                ),
                "ending_stakes": stakes.get(
                    "ending_stakes",
                    ""
                )
            },

            "ending_transition": data.get(
                "ending_transition",
                ""
            )
        }

    def _default_response(self) -> dict:

        return {
            "chapter_number": 0,

            "chapter_purpose": "",

            "dramatic_arc": {
                "opening_state": "",
                "inciting_development": "",
                "escalation": "",
                "turning_point": "",
                "consequence": "",
                "ending_state": ""
            },

            "major_beats": [],

            "emotional_progression": {
                "starting_emotion": "",
                "middle_emotion": "",
                "ending_emotion": ""
            },

            "character_progression": {},

            "information_flow": {
                "reader_learns": [],
                "characters_learn": [],
                "secrets_preserved": [],
                "foreshadowing": []
            },

            "active_conflicts": [],

            "thematic_progression": "",

            "stakes": {
                "initial_stakes": "",
                "escalated_stakes": "",
                "ending_stakes": ""
            },

            "ending_transition": ""
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

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "No JSON object found."
            )

        return response[start:end + 1].strip()

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