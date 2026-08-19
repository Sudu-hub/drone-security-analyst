import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class SecurityAnalystAgent:
    """
    Security Analyst Agent.

    Answers questions using the structured observations
    produced by the VLM and the security event context.
    """

    def __init__(
        self,
        model: str = "openrouter/free"
    ):

        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set."
            )

        self.model = model

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
            max_retries=0,
            default_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "Drone Security Analyst"
            }
        )

    # =========================================================
    # BUILD CONTEXT
    # =========================================================

    def build_context(
        self,
        vehicle_tracker,
        alerts
    ):

        context = {
            "vehicles": [],
            "alerts": alerts
        }

        for (
            vehicle_key,
            observations
        ) in vehicle_tracker.vehicles.items():

            color, make, model = vehicle_key

            vehicle = {
                "color": color,
                "make": make,
                "model": model,
                "observations": observations,
                "entry_count": sum(
                    1
                    for observation in observations
                    if observation.get("activity")
                    == "entering"
                ),
                "exit_count": sum(
                    1
                    for observation in observations
                    if observation.get("activity")
                    == "exiting"
                )
            }

            context["vehicles"].append(vehicle)

        return context

    # =========================================================
    # FORMAT CONTEXT
    # =========================================================

    def _format_context(
        self,
        context
    ):

        lines = []

        lines.append(
            "VEHICLE HISTORY:"
        )

        vehicles = context.get(
            "vehicles",
            []
        )

        if not vehicles:

            lines.append(
                "No vehicles detected."
            )

        else:

            for vehicle in vehicles:

                vehicle_name = (
                    f"{vehicle.get('color')} "
                    f"{vehicle.get('make')} "
                    f"{vehicle.get('model')}"
                )

                lines.append(
                    f"- {vehicle_name}"
                )

                lines.append(
                    f"  Entries: "
                    f"{vehicle.get('entry_count', 0)}"
                )

                lines.append(
                    f"  Exits: "
                    f"{vehicle.get('exit_count', 0)}"
                )

                for observation in vehicle.get(
                    "observations",
                    []
                ):

                    lines.append(
                        f"  "
                        f"{observation.get('timestamp')} | "
                        f"{observation.get('location')} | "
                        f"{observation.get('activity')}"
                    )

        lines.append("")
        lines.append(
            "SECURITY ALERTS:"
        )

        alerts = context.get(
            "alerts",
            []
        )

        if not alerts:

            lines.append(
                "No security alerts."
            )

        else:

            for alert in alerts:

                lines.append(
                    f"- "
                    f"{alert.get('alert_type')} | "
                    f"{alert.get('severity')} | "
                    f"{alert.get('location')} | "
                    f"{alert.get('message')}"
                )

        return "\n".join(lines)

    # =========================================================
    # ASK
    # =========================================================

    def ask(
        self,
        question: str,
        context: dict
    ):

        formatted_context = (
            self._format_context(
                context
            )
        )

        system_prompt = """
You are a Drone Security Analyst.

Answer using ONLY the provided security context.

Rules:
- Do not invent information.
- Be concise.
- Mention timestamps when useful.
- Mention locations when useful.
- Report vehicle entry/exit counts when asked.
- Report alert severity when relevant.
- If information is unavailable, say so.

Answer in plain text.
"""

        user_prompt = f"""
SECURITY CONTEXT

{formatted_context}

USER QUESTION

{question}

Answer using only the security context.
"""

        print()
        print(
            "--- Security Agent Request ---"
        )

        print(
            f"Model: {self.model}"
        )

        print(
            f"Question: {question}"
        )

        try:

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

                temperature=0.1,

                max_completion_tokens=70
            )

        except Exception as exc:

            print()
            print(
                "❌ OpenRouter connection/request failed"
            )

            print(
                f"Error type: {type(exc).__name__}"
            )

            print(
                f"Error: {exc}"
            )

            print()

            raise RuntimeError(
                "Could not connect to OpenRouter "
                "for the Security Analyst Agent."
            ) from exc

        # =====================================================
        # DEBUG RESPONSE
        # =====================================================

        print()
        print(
            "--- Security Agent Response ---"
        )

        print(
            f"Finish reason: "
            f"{response.choices[0].finish_reason}"
        )

        content = (
            response.choices[0]
            .message
            .content
        )

        print(
            f"Content: {repr(content)}"
        )

        print(
            "-------------------------------"
        )

        if content is None:

            raise ValueError(
                "Security Agent returned None."
            )

        content = content.strip()

        if not content:

            raise ValueError(
                "Security Agent returned empty response."
            )

        return content