import json

from models.scene import Scene
from utils.parser import Parser


class ScenePlanner:

    def __init__(self, llm):
        self.llm = llm

    def plan_scenes(
        self,
        story,
        chapter,
        memory
    ):

        prompt = self._build_prompt(
            story,
            chapter,
        )

        response = self.llm.generate(
            prompt,
            json_mode=True
        )

        return self._parse(response)

    def _build_prompt(
        self,
        story,
        chapter
    ):
        memory = story.memory

        return f"""
You are the Scene Planner of an autonomous novel writing system.

Your ONLY responsibility is planning.

Do NOT write prose.

Do NOT write dialogue.

------------------------------------------------

TITLE

{story.title}

WORLD

{story.world}

THEME

{story.theme}

STYLE

{story.writing_style}

NARRATIVE

{story.narrative}

------------------------------------------------

CHARACTERS

{story.characters}

------------------------------------------------

MEMORY

Summary:
{memory.summary}

Character States:
{memory.character_states}

Open Threads:
{memory.open_threads}

Important Objects:
{memory.important_objects}

Conflicts:
{memory.conflicts}

Theme Progress:
{memory.theme_progress}

------------------------------------------------

CURRENT CHAPTER

Number:
{chapter.number}

Title:
{chapter.title}

Goal:
{chapter.goal}

Revelation:
{chapter.revelation}

Ending Hook:
{chapter.ending_hook}

------------------------------------------------

Break this chapter into 4–7 scenes.

For each scene generate:

- number
- title
- location
- objective
- conflict
- ending
- participating_characters

Rules:

- Every scene must advance the story.
- Every scene must have a clear purpose.
- The ending of one scene should naturally transition into the next.
- The final scene must end with the chapter ending hook.
- Do not invent characters that do not exist.

Return ONLY JSON.

{{
    "scenes":[
        {{
            "number":1,
            "title":"",
            "location":"",
            "objective":"",
            "conflict":"",
            "ending":"",
            "participating_characters":[]
        }}
    ]
}}
"""

    def _parse(self, response):

        data = Parser.extract_json(response)

        scenes = []

        for scene in data["scenes"]:

            scenes.append(

                Scene(

                    number=scene["number"],

                    title=scene["title"],

                    location=scene["location"],

                    objective=scene["objective"],

                    conflict=scene["conflict"],

                    ending=scene["ending"],

                    participating_characters=scene[
                        "participating_characters"
                    ]
                )

            )

        return scenes