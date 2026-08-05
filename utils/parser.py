import json
import re


class Parser:

    @staticmethod
    def extract_json(text: str):
        """
        Extracts the first valid JSON object from an LLM response.
        """

        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found.")

        json_text = text[start:end + 1]

        return json.loads(json_text)