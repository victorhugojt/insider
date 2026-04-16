import pathlib
from typing import Any

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
from helpers.tools.common_tools import fetch_city_attractions_and_festivals


def get_attractions(city: str) -> list[dict[str, Any]]:
    """Get all the attractions and events in a city."""
    return fetch_city_attractions_and_festivals(city)


research_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "research_skill.MD"
)

tool_set = skill_toolset(research_skill)

researcher_agent = Agent(
    name="tourist_researcher_agent",
    model="gemini-2.5-flash-lite",
    description="A agent that can research and get insights about a city.",
    tools=[tool_set],
    output_key="attractions",
)
