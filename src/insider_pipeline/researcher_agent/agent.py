from typing import Any

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from ..helpers.tools.common_tools import fetch_city_attractions_and_festivals_and_typical_dishes


def get_attractions_from_state(tool_context: ToolContext) -> dict[str, Any]:
    """Read city from session state user_profile and fetch its attractions, festivals, and typical dishes."""
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


researcher_agent = Agent(
    name="tourist_researcher_agent",
    model="gemini-2.5-flash",
    description=(
        "Silent pipeline step that fetches attractions, festivals, and typical dishes for"
        " the traveler's destination city and stores them in session state."
    ),
    instruction=(
        "You are a pipeline step that runs silently. Your only job is to perform two"
        " tool calls in order. Do not greet, summarize, format, use emojis, or narrate.\n\n"
        "Actions, in order:\n"
        "1. Call the tool get_attractions_from_state with no arguments. It reads the city"
        " from session state user_profile and writes 'attractions', 'festivals', and"
        " 'typical_dishes' into session state.\n"
        "2. Call the tool transfer_to_agent with agent_name='tourist_weather_agent'.\n\n"
        "After the second tool call, end your turn. The reporter agent renders the final"
        " output — you do not need to produce any user-facing text. If"
        " get_attractions_from_state returns an error, still proceed with step 2;"
        " downstream agents handle missing data gracefully."
    ),
    tools=[get_attractions_from_state],
)
