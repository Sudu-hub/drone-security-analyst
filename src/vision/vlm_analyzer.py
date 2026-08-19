import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class VLMAnalyzer:
    """
    AI-based frame analyzer.

    Current prototype:
        Text frame description -> structured observation

    Production extension:
        Image frame -> VLM -> structured observation
    """

    def __init__(
        self,
        model: str = "qwen/qwen3.6-27b"
    ):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. "
                "Add it to your .env file."
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        self.model = model

    def analyze_description(
        self,
        description: str,
        timestamp: str,
        location: str
    ) -> dict:

        system_prompt = """
You are a drone security analyzer.

Analyze the frame description and return ONLY valid JSON.

Extract:
- object type
- color
- make
- model
- activity
- confidence

Object types:
person, vehicle, animal, unknown

Activities:
entering, exiting, parked, standing, walking,
loitering, moving, unknown

Rules:
- Never invent information.
- Unknown make/model must be null.
- Confidence must be between 0 and 1.
- Return only JSON.

Format:
{
  "objects": [
    {
      "type": "vehicle",
      "color": "blue",
      "make": "Ford",
      "model": "F150",
      "activity": "entering",
      "confidence": 0.94
    }
  ]
}
"""

        user_prompt = f"""
Frame timestamp: {timestamp}

Location:
{location}

Frame description:
{description}

Return the structured JSON analysis.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            # Force JSON output
            response_format={
                "type": "json_object"
            },

            # Keep response deterministic
            temperature=0.1,

            # Give reasoning + answer enough room
            max_tokens=300,

            # Disable Qwen thinking for this simple extraction task
            extra_body={
                "reasoning": {
                    "enabled": False
                }
            }
        )

        message = response.choices[0].message

        content = message.content

        # Debug information
        print("\n--- OpenRouter Debug ---")
        print("Model:", self.model)
        print("Finish reason:", response.choices[0].finish_reason)
        print("Content:", repr(content))
        print("------------------------\n")

        if not content:
            raise ValueError(
                "VLM returned an empty response. "
                f"Finish reason: {response.choices[0].finish_reason}"
            )

        try:
            result = json.loads(content)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"VLM returned invalid JSON:\n{content}"
            ) from exc

        # Add telemetry context
        result["timestamp"] = timestamp
        result["location"] = location

        return result

    def validate_result(self, result: dict) -> bool:

        if not isinstance(result, dict):
            return False

        if "objects" not in result:
            return False

        if not isinstance(result["objects"], list):
            return False

        for obj in result["objects"]:

            if not isinstance(obj, dict):
                return False

            if "type" not in obj:
                return False

            if "activity" not in obj:
                return False

            confidence = obj.get("confidence")

            if confidence is not None:

                if not isinstance(
                    confidence,
                    (int, float)
                ):
                    return False

                if not 0 <= confidence <= 1:
                    return False

        return True