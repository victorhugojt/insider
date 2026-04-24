from google.adk.agents import Agent

from .interviewer_agent.agent import root_agent as interviewer_agent
from .researcher_agent.agent import researcher_agent
from .reporter_agent.agent import reporter_agent
from .weather_agent.agent import weather_agent


root_agent = Agent(
    name="insider_pipeline",
    model="gemini-2.5-flash-lite",
    description=(
        "Orchestrates a tourist activity pipeline: interview → research → report."
    ),
    instruction=(
        "You are the pipeline entry point. On the very first user message, immediately"
        " transfer to tourist_interviewer_agent. Do not greet the user or say anything"
        " — just transfer."
    ),
    sub_agents=[interviewer_agent, researcher_agent, reporter_agent, weather_agent],
)
