import requests
import time 
import os
import re 
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=API_KEY
)

def apply_narrative_voice(story_text):
    prompt = f"""
Rewrite the following story using a first-person narrator who has internalized the city's optimization language.

Rules:
- Do NOT change plot, structure, or events.
- Only modify voice, tone, and vocabulary.
- In early sections, describe emotional events using bureaucratic, technical, system-style language.
- Gradually reduce this language as the narrator restores forbidden memories.
- Maintain subtlety. Avoid melodrama.
- Keep sentence flow natural.

Story:
{story_text}
"""

    return generate(prompt)

def txt_to_docx_kdp(input_path, output_path, title, author):
    document = Document()

    # ---- Title Page ----
    title_paragraph = document.add_paragraph()
    title_run = title_paragraph.add_run(title)
    title_run.bold = True
    title_run.font.size = Pt(24)
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    document.add_paragraph()  # spacer

    author_paragraph = document.add_paragraph()
    author_run = author_paragraph.add_run(f"By {author}")
    author_run.font.size = Pt(14)
    author_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    document.add_page_break()

    # ---- Body ----
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chapter_count = 1
    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Optional: treat blank lines between sections as chapters
        if stripped.lower().startswith("chapter"):
            document.add_heading(stripped, level=1)
        else:
            paragraph = document.add_paragraph(stripped)
            paragraph.paragraph_format.space_after = Pt(12)

    # ---- Save File ----
    document.save(output_path)

def extract_score(feedback):
    """
    Extracts a score (1–10) from model feedback text.
    Returns integer score or 0 if not found.
    """

    # 1. Look for explicit "Score: X" style
    match = re.search(r"score\s*[:\-]?\s*(\d{1,2})\s*(?:/10)?",
                      feedback,
                      re.IGNORECASE)

    if match:
        score = int(match.group(1))
        return max(1, min(score, 10))

    # 2. Fallback: find standalone number 1–10
    match = re.search(r"\b(10|[1-9])\b", feedback)
    if match:
        return int(match.group(1))

    return 0

def generate(prompt):

    while True:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            time.sleep(30)
            return response.text

        except Exception as e:
            print("Rate limited:", e)
            print("Sleeping 60 seconds...")
            time.sleep(60)
    
def writer(topic, previous_text=""):
    prompt = f"""
You are writing a long-form story.

Story so far:
{previous_text}

Continue the story about:
{topic}

Write the next section (~1000 words).
"""
    return generate(prompt)


def world_builder(topic):
    prompt = f"""
Design a rich setting for a story about:
{topic}
Keep it under 150 words.
"""
    return generate(prompt)

def character_builder(topic):
    prompt = f"""
Create 2–3 compelling characters for a story about:
{topic}
Keep under 200 words.
"""
    return generate(prompt)

def plot_planner(topic, world, characters, theme):
    prompt = f"""

Theme:
{theme}

Using this setting:
{world}

And these characters:
{characters}

Create a detailed 12-part plot outline with escalating stakes and character arc progression.
"""
    return generate(prompt)

def section_writer(topic, world, characters, outline, style, previous_sections, current_section, total_sections):

    prompt = f"""
Setting:
{world}

Characters:
{characters}

Outline:
{outline}

Style Guide:
{style}

Story so far:
{previous_sections}

You are writing section {current_section} of {total_sections}.

Story progression rules:

- Early sections establish mystery and world.
- Middle sections escalate conflict and reveal memory inconsistencies.
- Final sections resolve the emotional and thematic arc.
- The final section MUST conclude the story completely.

Current section:
{current_section}/{total_sections}

Write ONLY this section.
Do not restart the story.
Do not summarize future events.
"""
    return generate(prompt)

def section_critic(section):
    prompt = f"""
Critique this section briefly.
Give Score: X (1–10)
 
Section:
{section}
"""
    return generate(prompt)

def section_editor(section, feedback):
    prompt = f"""
Improve this section using the critique.

Critique:
{feedback}

Section:
{section}
"""
    return generate(prompt)

def improve_story(original_story, feedback):
    prompt = f"""
You are a professional editor.

Improve the story using this critique:

Critique:
{feedback}

Original Story:
{original_story}

Rewrite the story with stronger emotional depth and tighter structure.
"""
    return generate(prompt)

def macro_editor(full_story):
    prompt = f"""
You are a professional developmental editor.

Review the full story and improve:

- Character consistency
- Thematic depth
- Emotional arc progression
- Pacing across sections
- Remove repetition

Rewrite the full story with stronger narrative cohesion.

Story:
{full_story}
"""
    return generate(prompt)

def style_guide(topic):
    prompt = f"""
Define a consistent writing style for a story about:
{topic}

Include:
- Tone
- Narrative voice
- Sentence style
- Emotional mood
Keep it short.
"""
    return generate(prompt)

def theme_builder(topic, world, characters):
    prompt = f"""
Based on this world and characters:

World:
{world}

Characters:
{characters}

Define the central theme and emotional question of the story.
"""
    return generate(prompt)

def log(text):
    with open("stories/log.txt", "a") as f:
        f.write(text + "\n\n")

def summarize(text):
    prompt = f"Summarize this in 200 words:\n{text}"
    return generate(prompt)

def build_story(topic, story_id):
    i = 0;
    # 1. Build foundation
    print("Building the world")
    world = world_builder(topic)
    print("Building the characters")
    characters = character_builder(topic)
    print("Building the theme")
    theme = theme_builder(topic, world, characters)
    print("Buidling the outline")
    outline = plot_planner(topic, world, characters, theme)
    print("Building the style")
    style = style_guide(topic)
    story_sections = []
    summary_memory = ""

    for i in range(5):  # 5 sections
        recent_sections = "\n\n".join(story_sections[-2:])
        context = f"""
Theme:
{theme}

Story Memory:
{summary_memory}

Recent Sections:
{recent_sections}"""
        
        section = section_writer(
            world=world,
            topic=topic,
            characters=characters,
            outline=outline,
            style=style,
            previous_sections=context,
            current_section=i + 1,
            total_sections=5
        )

        feedback = section_critic(section)

        score = extract_score(feedback)
        attempts = 0
        while score < 6 and attempts < 2:
            section = section = section_writer(
    topic=topic,
    world=world,
    characters=characters,
    outline=outline,
    style=style,
    previous_sections=context,
    current_section=i ,
    total_sections=5
)
            feedback = section_critic(section)
            score = extract_score(feedback)
            attempts += 1
            
        if score < 8:
            improved = section_editor(section, feedback)
        else:
            improved = section

        story_sections.append(improved)
        combined = "\n\n".join(story_sections)
        if i % 3 == 0:
            summary_memory = summarize(combined)
        
        log(f"Section {i} complete.\nScore feedback:\n{feedback}")
        time.sleep(2)

    final_story = "\n\n".join(story_sections)
    macro_rewritten_story = macro_editor(final_story)
    final_story = apply_narrative_voice(macro_rewritten_story)

    with open(f"stories/story_{story_id}.txt", "w") as f:
        print("Inside the file")
        f.write(final_story)

    return final_story
        
def main():
    topic = """In a near-future metropolis, the city infrastructure quietly edits citizens’ memories to maintain social harmony. Minor heartbreak? Deleted. Political anger? Softened. One archivist discovers her own childhood has been rewritten dozens of times and starts restoring forbidden memories across the population. Theme fuel: identity vs comfort
Hook: The antagonist isn’t evil. It’s municipal optimization."""
    story_count = 0

    while story_count<1:
        try:
            build_story(topic, story_count)
        except Exception as e:
            log(str(e))
            time.sleep(5)
        
        txt_to_docx_kdp(
            input_path=f"stories/story_{story_count}.txt",
            output_path=f"stories/story_{story_count}.docx",
            title="The Midnight Machine",
            author="Your Name"
        )

        story_count += 1
        time.sleep(10)

    print("The story is ready ")
    
if __name__ == "__main__":
    main()
