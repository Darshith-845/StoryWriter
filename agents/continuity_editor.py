from models.story import Story
from models.scene import Scene
from models.memory import StoryMemory


class MemoryManager:

    def __init__(self, llm):
        self.llm = llm

    def update(
        self,
        story: Story,
        scene: Scene,
        memory: StoryMemory,
        critic_result: dict
    ) -> StoryMemory:
        """
        Update long-term story memory after a scene.

        The Memory Manager extracts only information that should
        persist beyond the current scene.

        It does not generate prose and does not evaluate the scene.
        """

        prompt = self._build_prompt(
            story,
            scene,
            memory,
            critic_result
        )

        response = self.llm.generate(prompt)

        return self._parse_response(
            response,
            memory
        )

    # ------------------------------------------------------------------
    # Prompt Construction
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        story: Story,
        scene: Scene,
        memory: StoryMemory,
        critic_result: dict
    ) -> str:

        story_context = self._build_story_context(story)
        scene_context = self._build_scene_context(scene)
        memory_context = self._build_memory_context(memory)
        critic_context = self._build_critic_context(critic_result)

        return f"""
You are the Memory Manager of an autonomous long-form
fiction generation system.

Your responsibility is to maintain persistent narrative memory.

You have just received a completed scene.

Your task is to determine what information from this scene
must remain available for future scenes.

Do NOT write prose.

Do NOT rewrite the scene.

Do NOT critique the scene.

Do NOT invent events.

Only extract and update persistent story state.

============================================================
STORY CONTEXT
============================================================

{story_context}

============================================================
COMPLETED SCENE
============================================================

{scene_context}

============================================================
EXISTING LONG-TERM MEMORY
============================================================

{memory_context}

============================================================
CRITIC INFORMATION
============================================================

{critic_context}

The Critic information is provided only as supporting context.

Do not treat criticism as an event that happened in the story.

============================================================
MEMORY RULES
============================================================

1. Preserve important information from previous memory.

2. Add genuinely new information introduced by the scene.

3. Remove information that is no longer active.

4. Update character states when the scene changes them.

5. Track newly discovered information.

6. Track important decisions.

7. Track important objects.

8. Track active conflicts.

9. Track unresolved plot threads.

10. Track changes in relationships.

11. Track meaningful changes in character goals.

12. Track meaningful emotional changes.

13. Preserve important consequences from previous events.

14. Do not store every minor detail.

15. Do not store ordinary descriptions that have no future
    narrative importance.

16. Do not invent information that does not appear in the
    scene or existing memory.

17. Do not reveal secrets merely because they exist in memory.

18. Keep memory compact and useful for future reasoning.

============================================================
CHARACTER STATE
============================================================

For each character whose state changed, update:

- location
- current goal
- current emotion
- relationships
- relevant knowledge
- beliefs
- important consequences

Do not reset unchanged fields.

============================================================
OPEN THREADS
============================================================

Add unresolved narrative questions, conflicts, promises,
mysteries, goals, or consequences.

Remove threads that have been clearly resolved.

Do not mark a thread as resolved simply because it was
mentioned.

============================================================
IMPORTANT OBJECTS
============================================================

Track objects that may matter later.

Examples:

- letters
- weapons
- documents
- keys
- photographs
- artifacts
- locations containing important objects

Do not store ordinary objects.

============================================================
CONFLICTS
============================================================

Track active conflicts between:

- characters
- characters and organizations
- characters and circumstances
- internal character struggles

Remove conflicts that have clearly ended.

============================================================
THEME PROGRESSION
============================================================

Update the thematic progression only when the scene
meaningfully changes or develops the story's themes.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "summary": "...",

    "last_scene_summary": "...",

    "character_states": {{

        "Character Name": {{
            "location": "...",
            "goal": "...",
            "emotion": "...",
            "knowledge_updates": [],
            "belief_updates": [],
            "relationship_updates": {{
                "Character": "..."
            }}
        }}

    }},

    "open_threads": [
        "..."
    ],

    "important_objects": [
        "..."
    ],

    "conflicts": [
        "..."
    ],

    "theme_progress": "..."
}}

The returned memory must represent the COMPLETE updated
memory state, not only the changes from this scene.

Do not include explanations outside the JSON object.
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

Generated Prose:
{scene.prose}
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

Conflicts:
{self._format_list(memory.conflicts)}

Theme Progression:
{memory.theme_progress}
"""

    def _build_critic_context(
        self,
        critic_result: dict
    ) -> str:

        if not critic_result:
            return "No critic result available."

        return f"""
Overall Score:
{critic_result.get("overall_score", 0)}

Passed:
{critic_result.get("passed", False)}

Strengths:
{self._format_list(
    critic_result.get("strengths", [])
)}

Issues:
{self._format_list(
    critic_result.get("issues", [])
)}

Revision Instructions:
{self._format_list(
    critic_result.get("revision_instructions", [])
)}
"""

    def _parse_response(
        self,
        response: str,
        previous_memory: StoryMemory
    ) -> StoryMemory:

        import json

        try:
            cleaned = self._clean_json(response)

            data = json.loads(cleaned)

            return self._build_memory(
                data,
                previous_memory
            )

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):
            return previous_memory

    def _build_memory(
        self,
        data: dict,
        previous_memory: StoryMemory
    ) -> StoryMemory:

        if not isinstance(data, dict):
            return previous_memory

        summary = data.get(
            "summary",
            previous_memory.summary
        )

        last_scene_summary = data.get(
            "last_scene_summary",
            previous_memory.last_scene_summary
        )

        character_states = data.get(
            "character_states",
            previous_memory.character_states
        )

        open_threads = data.get(
            "open_threads",
            previous_memory.open_threads
        )

        important_objects = data.get(
            "important_objects",
            previous_memory.important_objects
        )

        conflicts = data.get(
            "conflicts",
            previous_memory.conflicts
        )

        theme_progress = data.get(
            "theme_progress",
            previous_memory.theme_progress
        )

        return StoryMemory(
            summary=summary,
            last_scene_summary=last_scene_summary,
            character_states=character_states,
            open_threads=open_threads,
            important_objects=important_objects,
            conflicts=conflicts,
            theme_progress=theme_progress
        )

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

