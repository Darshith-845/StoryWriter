import requests
import time 
MODEL = "gemma:2b-instruct-q4_0"

def generate(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
        "num_predict": 250,
        "temperature": 0.7
    }
    }
    response = requests.post(url, json=payload)
    return response.json()["response"]

def writer(topic):
    prompt = f"""
You are a creative fiction writer.
Write a 300 word short story about:
{topic}
"""
    return generate(prompt)

def critic(story):
    prompt = f"""
You are a strict literary critic.
Analyze the story below.
Point out weaknesses in:
- Plot
- Character depth
- Emotional impact
- Ending strength

Story:
{story}
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

def main():
    topic = "A machine that secretly writes stories at night."

    first_draft = writer(topic)
    time.sleep(1)

    feedback = critic(first_draft)
    time.sleep(1)

    final_story = improve_story(first_draft, feedback)
    time.sleep(1)

    with open("stories/story_final.txt", "w") as f:
        f.write(final_story)

    print("Final story saved.")

if __name__ == "__main__":
    main()
