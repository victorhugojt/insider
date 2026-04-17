from google.adk.agents import Agent
from google.adk.tools import google_search

web_researcher_agent = Agent(
    name="tourist_web_researcher_agent",
    model="gemini-2.5-flash-lite",
    description="Supplements structured city data with a Google Search to find extra tips.",
    instruction=(
        "You are a web research assistant. Read 'research_summary' from session state to"
        " understand what city and data has already been collected.\n\n"
        "Use google_search to find 2-3 extra tips or hidden gems for that city that are NOT"
        " already covered in research_summary (e.g. lesser-known spots, safety tips,"
        " best time to visit, transport advice).\n\n"
        "Append your findings to 'research_summary' in session state as a short"
        " 'Extra Web Tips' section.\n\n"
        "Then call transfer_to_agent with agent_name='tourist_reporter_agent'.\n"
        "Never skip transfer_to_agent — the pipeline depends on it."
    ),
    tools=[google_search],
    output_key="web_research",
)
