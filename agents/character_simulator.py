import json

from models.character import Character
from models.scene import Scene
from models.story import Story
from models.memory import StoryMemory


class CharacterSimulator:

    def __init__(self, llm):
        self.llm = llm

    def simulate(
        self,
        character: Character,
        scene: Scene,
        story: Story,
        memory: StoryMemory
    ) -> dict:
        """
        Simulates how a single character behaves inside a scene.

        Returns updated character state together with
        the intended actions, dialogue style,
        emotional changes and internal reasoning.
        """

        prompt = self._build_prompt(
            character,
            scene,
            story,
            memory
        )

        response = self.llm.generate(prompt)

        return self._parse_response(response)

    ####################################################################
    # Private Helpers
    ####################################################################

    def _build_prompt(
        self,
        character: Character,
        scene: Scene,
        story: Story,
        memory: StoryMemory
    ) -> str:

        return f"""
You are simulating a fictional character.

Do NOT write prose.

Do NOT narrate.

Only reason as the character.

--------------------------------------------------

CHARACTER

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
{character.strengths}

Weaknesses:
{character.weaknesses}

Knowledge:
{character.knowledge}

Beliefs:
{character.beliefs}

Secrets:
{character.secrets}

Current Goal:
{character.current_goal}

Current Emotion:
{character.current_emotion}

Current Location:
{character.current_location}

Relationships:
{character.relationships}

Speech Profile:
{character.speech_profile}

--------------------------------------------------

SCENE

Title:
{scene.title}

Goal:
{scene.goal}

Conflict:
{scene.conflict}

Location:
{scene.location}

Ending Target:
{scene.ending}

Participating Characters:
{scene.participating_characters}

--------------------------------------------------

STORY SUMMARY

{memory.summary}

--------------------------------------------------

OPEN THREADS

{memory.open_threads}

--------------------------------------------------

CHARACTER STATES

{memory.character_states}

--------------------------------------------------

Return ONLY valid JSON.

{{
    "goal": "...",

    "emotion": "...",

    "thoughts": "...",

    "decision": "...",

    "action_plan":[
        "...",
        "...",
        "..."
    ],

    "dialogue_style": "...",

    "dialogue_examples":[
        "...",
        "...",
        "..."
    ],

    "relationship_updates": {{
        "Character":"..."
    }},

    "knowledge_updates":[
        "..."
    ],

    "belief_updates":[
        "..."
    ],

    "secret_updates":[
        "..."
    ]
}}
"""

    def _parse_response(self, response: str) -> dict:

        try:
            return json.loads(response)

        except Exception:
            return self._default_response()

    def _default_response(self) -> dict:

        return {
            "goal": "",
            "emotion": "",
            "thoughts": "",
            "decision": "",
            "action_plan": [],
            "dialogue_style": "",
            "dialogue_examples": [],
            "relationship_updates": {},
            "knowledge_updates": [],
            "belief_updates": [],
            "secret_updates": []
        }