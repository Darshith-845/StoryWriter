import json

from models.story import Story
from models.chapter import Chapter
from models.character import Character


class StoryDirector:

    def __init__(self, llm):
        self.llm = llm

    def create_story(self, topic: str) -> Story:
        """
        Main entry point.

        Generates the complete planning phase of the novel
        and returns a fully initialized Story object.
        """

        foundation = self._generate_foundation(topic)

        narrative = self._generate_narrative(topic)

        outline = self._generate_outline(
            topic,
            foundation,
            narrative
        )

        return self._build_story(
            topic,
            foundation,
            narrative,
            outline
        )

    def _generate_foundation(self, topic: str) -> dict:

        prompt = f"""
You are an expert story designer.

Topic:
{topic}

Generate:

- Story title
- World description
- Theme
- Writing style
- 2-6 major characters

Return ONLY valid JSON.

{{
    "title":"",
    "world":"",
    "theme":"",
    "style":"",
    "characters":[
        {{
            "name":"",
            "role":"",
            "personality":"",
            "motivation":"",
            "backstory":"",
            "strengths":[],
            "weaknesses":[]
        }}
    ]
}}
"""

        response = self.llm.generate(
            prompt,
            json_mode=True
        )

        return json.loads(response)

    def _generate_narrative(self, topic: str) -> dict:

        prompt = f"""
Choose the best narrative style.

Topic:

{topic}

Return ONLY JSON.

{{
    "perspective":"",
    "tense":"",
    "voice":"",
    "distance":"",
    "structure":""
}}
"""

        response = self.llm.generate(
            prompt,
            json_mode=True
        )

        return json.loads(response)

    def _generate_outline(
        self,
        topic,
        foundation,
        narrative
    ) -> dict:

        prompt = f"""
Design an eight chapter novel.

Topic:
{topic}

World:
{foundation["world"]}

Characters:
{foundation["characters"]}

Theme:
{foundation["theme"]}

Narrative:
{narrative}

Return ONLY JSON.

{{
    "chapters":[
        {{
            "number":1,
            "title":"",
            "goal":"",
            "revelation":"",
            "ending_hook":""
        }}
    ]
}}
"""

        response = self.llm.generate(
            prompt,
            json_mode=True
        )

        return json.loads(response)

    def _build_story(
        self,
        topic,
        foundation,
        narrative,
        outline
    ) -> Story:

        characters = []

        for c in foundation["characters"]:

            characters.append(
                Character(
                    name=c["name"],
                    role=c["role"],
                    personality=c["personality"],
                    motivation=c["motivation"],
                    backstory=c["backstory"],
                    strengths=c["strengths"],
                    weaknesses=c["weaknesses"]
                )
            )

        chapters = []

        for ch in outline["chapters"]:

            chapters.append(
                Chapter(
                    number=ch["number"],
                    title=ch["title"],
                    goal=ch["goal"],
                    revelation=ch["revelation"],
                    ending_hook=ch["ending_hook"]
                )
            )

        story = Story(
            title=foundation["title"],
            topic=topic,
            world=foundation["world"],
            theme=foundation["theme"],
            writing_style=foundation["style"],
            narrative=narrative,
            characters=characters,
            chapters=chapters
        )

        return story