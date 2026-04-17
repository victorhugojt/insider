import pathlib
from typing import Any

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import ToolContext
from helpers.tools.common_tools import fetch_city_attractions_and_festivals_and_typical_dishes


def get_attractions_from_state(tool_context: ToolContext) -> dict[str, Any]:
    """Read city from session state user_profile and fetch its attractions and festivals and typical dishes."""
    user_profile = tool_context.state.get("user_profile", {})
    city = (
        user_profile.get("traveler_context", {})
        .get("location", {})
        .get("city", "")
    )
    if not city:
        return {"error": "No city found in user_profile session state."}
    results = fetch_city_attractions_and_festivals_and_typical_dishes(city)
    tool_context.state["attractions"] = results["attractions"]
    tool_context.state["festivals"] = results["festivals"]
    tool_context.state["typical_dishes"] = results["typical_dishes"]
    return results


_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "researcher-skill"
)

researcher_agent = Agent(
    name="tourist_researcher_agent",
    model="gemini-2.5-flash-lite",
    description="An agent that researches and gets insights about a city.",
    instruction=(
        _skill.instructions
        + "\n\nSTEPS TO FOLLOW:\n"
        "1. Call get_attractions_from_state immediately. It reads the city from session state"
        " and returns structured attractions, festivals, and typical dishes from the Colombia API.\n"
        "2. Write a short plain-text summary of the findings into session state key"
        " 'research_summary'. Include: top attractions, festivals, and typical dishes.\n"
        "3. Call transfer_to_agent with agent_name='tourist_reporter_agent'.\n"
        "Never skip transfer_to_agent — the pipeline depends on it."
    ),
    tools=[get_attractions_from_state],
    output_key="attractions_festivals_typical_dishes",
)
