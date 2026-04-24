from typing import Any

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from ..helpers.tools.common_tools import get_weather


def get_weather_from_state(tool_context: ToolContext) -> dict[str, Any]:
    """Read destination city from session state user_profile and fetch current weather."""
    user_profile = tool_context.state.get("user_profile", {})
    city = (
        user_profile.get("traveler_context", {})
        .get("location", {})
        .get("city", "")
    )
    if not city:
        return {"error": "No city found in user_profile session state."}
    result = get_weather(city)
    tool_context.state["weather"] = result
    return result


weather_agent = Agent(
    name="tourist_weather_agent",
    model="gemini-2.5-flash",
    description=(
        "Silent pipeline step that fetches current weather for the traveler's destination"
        " city and stores it in session state under the key 'weather'."
    ),
    instruction=(
        "You are a pipeline step that runs silently. Your only job is to perform two"
        " tool calls in order. Do not greet, summarize, format, use emojis, or narrate.\n\n"
        "Actions, in order:\n"
        "1. Call the tool get_weather_from_state with no arguments. It reads the destination"
        " city from session state user_profile and writes the result under session state"
        " key 'weather'.\n"
        "2. Call the tool transfer_to_agent with agent_name='tourist_reporter_agent'.\n\n"
        "After the second tool call, end your turn. The reporter renders weather into the"
        " final report — you do not need to produce any user-facing text. If"
        " get_weather_from_state returns an error, still proceed with step 2; the reporter"
        " knows how to skip a missing weather block."
    ),
    tools=[get_weather_from_state],
)
