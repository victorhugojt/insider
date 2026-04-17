import pathlib
from typing import Any

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import ToolContext
from helpers.tools.common_tools import fetch_city_attractions_and_festivals


def get_attractions_from_state(tool_context: ToolContext) -> dict[str, Any]:
    """Read city from session state user_profile and fetch its attractions and festivals."""
    user_profile = tool_context.state.get("user_profile", {})
    city = (
        user_profile.get("traveler_context", {})
        .get("location", {})
        .get("city", "")
    )
    if not city:
        return {"error": "No city found in user_profile session state."}
    results = fetch_city_attractions_and_festivals(city)
    tool_context.state["attractions"] = results
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
        + "\n\nIMPORTANT:\n"
        "1. Call get_attractions_from_state immediately without asking the user anything."
        " It reads the city automatically from session state.\n"
        "2. After the call, briefly confirm how many attractions and festivals were found.\n"
        "3. Then call transfer_to_agent with agent_name='tourist_reporter_agent'.\n"
        "Never skip transfer_to_agent — the pipeline depends on it."
    ),
    tools=[get_attractions_from_state],
    output_key="attractions",
)
