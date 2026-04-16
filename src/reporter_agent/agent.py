from typing import Any
from google.adk.agents import Agent

reporter_agent = Agent(
    name="tourist_reporter_agent",
    model="gemini-2.5-flash-lite",
    description="A agent that can write a report about a city.",
    tools=[],
    output_key="report",
)