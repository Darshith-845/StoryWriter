import requests
import time 
import os
import re 

MODEL = "gemma:2b-instruct-q4_0"


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
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
        "num_predict": 400,
        "temperature": 0.7
    }
    }
    response = requests.post(url, json=payload, timeout=300)
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        return ""
    
def writer(topic, previous_text=""):
    prompt = f"""
You are writing a long-form story.

Story so far:
{previous_text}

Continue the story about:
{topic}

Write the next section (~200 words).
"""
    return safe_generate(prompt)


def world_builder(topic):
    prompt = f"""
Design a rich setting for a story about:
{topic}
Keep it under 150 words.
"""
    return safe_generate(prompt)

def character_builder(topic):
    prompt = f"""
Create 2–3 compelling characters for a story about:
{topic}
Keep under 200 words.
"""
    return safe_generate(prompt)

def plot_planner(topic, world, characters):
    prompt = f"""
Using this setting:
{world}

And these characters:
{characters}

Create a 5-part plot outline.
"""
    return safe_generate(prompt)

def section_writer(topic, world, characters, outline, previous_sections):
    prompt = f"""
Setting:
{world}

Characters:
{characters}

Outline:
{outline}

Story so far:
{previous_sections}

Write the next section (~200 words).
"""
    return safe_generate(prompt)

def section_critic(section):
    prompt = f"""
Critique this section briefly.
Give Score: X (1–10)

Section:
{section}
"""
    return safe_generate(prompt)

def section_editor(section, feedback):
    prompt = f"""
Improve this section using the critique.

Critique:
{feedback}

Section:
{section}
"""
    return safe_generate(prompt)

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
    return safe_generate(prompt)

def log(text):
    with open("stories/log.txt", "a") as f:
        f.write(text + "\n\n")

def safe_generate(prompt):
    load = os.getloadavg()[0]  # 1-min load avg
    if load > os.cpu_count() - 1:
        time.sleep(5)
    return generate(prompt)

def summarize(text):
    prompt = f"Summarize this in 200 words:\n{text}"
    return safe_generate(prompt)

def build_story(topic, story_id):

    # 1. Build foundation
    world = world_builder(topic)
    characters = character_builder(topic)
    outline = plot_planner(topic, world, characters)

    story_sections = []
    summary_memory = ""

    for i in range(10):  # 5 sections

        context = summary_memory + "\n\n" + "\n\n".join(story_sections[-2:])
        section = section_writer(
            topic=topic,
            world=world,
            characters=characters,
            outline=outline,
            previous_sections=context 
        )

        feedback = section_critic(section)

        score = extract_score(feedback)
        attempts = 0
        while score < 6 and attempts < 2:
            section = section_writer(topic, world, characters, outline, context)
            feedback = section_critic(section)
            score = extract_score(feedback)
            attempts += 1
            
        if score < 8:
            improved = section_editor(section, feedback)
        else:
            improved = section

        story_sections.append(improved)

        combined = "\n\n".join(story_sections)
        summary_memory = summarize(combined)
        
        log(f"Section {i} complete.\nScore feedback:\n{feedback}")
        time.sleep(2)

    final_story = "\n\n".join(story_sections)

    with open(f"stories/story_{story_id}.txt", "w") as f:
        f.write(final_story)

    return final_story
        
def main():
    topic = "A machine that secretly writes stories at night."
    story_count = 0

    while story_count>10:
        topic = f"Night story #{story_count}"
        try:
            build_story(topic, story_count)
        except Exception as e:
            log(str(e))
            time.sleep(5)
        story_count += 1
        time.sleep(10)
    
if __name__ == "__main__":
    main()
