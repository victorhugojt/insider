import ast
import json
from typing import Any

from google.adk.agents import Agent


def _coerce_to_dict(
    value: dict[str, Any] | str | None, field_name: str
) -> dict[str, Any]:
    """Accept ADK tool args as dict or JSON string and normalize to dict."""
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return {}
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            # ADK occasionally forwards Python-literal-like dict strings.
            try:
                parsed = ast.literal_eval(stripped)
                if isinstance(parsed, dict):
                    return parsed
            except (ValueError, SyntaxError):
                # Keep raw value instead of crashing tool execution.
                return {"raw_input": stripped}
    raise TypeError(f"{field_name} must be a dictionary or JSON object string")


def collect_budget_and_location(
    budget_currency: str,
    budget_min: float,
    budget_max: float,
    location_city: str,
    location_region: str = "",
    location_country: str = "",
) -> dict[str, Any]:
    """Store traveler budget and destination in a normalized dictionary."""
    return {
        "budget": {
            "currency": budget_currency.upper().strip(),
            "min": budget_min,
            "max": budget_max,
        },
        "location": {
            "city": location_city.strip(),
            "region": location_region.strip(),
            "country": location_country.strip(),
        },
    }


def collect_interests_and_profile(
    interests: list[str],
    age: int | None = None,
    education_level: str | None = None,
    travel_style: str | None = None,
    mobility_needs: str | None = None,
) -> dict[str, Any]:
    """Store interests list and relevant personal preferences for activity matching."""
    cleaned_interests = [item.strip() for item in interests if item and item.strip()]
    return {
        "interests": cleaned_interests,
        "profile": {
            "age": age,
            "education_level": education_level,
            "travel_style": travel_style,
            "mobility_needs": mobility_needs,
        },
    }


def build_activity_handoff_payload(
    budget_location_data: dict[str, Any] | str,
    interest_profile_data: dict[str, Any] | str,
    timeframe_start: str,
    timeframe_end: str,
    group_size: int = 1,
    additional_notes: str = "",
) -> dict[str, Any]:
    """Build one payload dict to send to a local-activities recommendation agent."""
    budget_location = _coerce_to_dict(budget_location_data, "budget_location_data")
    interest_profile = _coerce_to_dict(interest_profile_data, "interest_profile_data")

    return {
        "traveler_context": {
            **budget_location,
            **interest_profile,
            "timeframe": {
                "start": timeframe_start,
                "end": timeframe_end,
            },
            "group_size": group_size,
            "additional_notes": additional_notes.strip(),
        },
        "target_task": "find_best_local_activities_for_tourist",
    }


def build_activity_handoff_payload_flat(
    budget_currency: str,
    budget_min: float,
    budget_max: float,
    location_city: str,
    timeframe_start: str,
    timeframe_end: str,
    interests: list[str],
    location_region: str = "",
    location_country: str = "",
    age: int | None = None,
    education_level: str | None = None,
    travel_style: str | None = None,
    mobility_needs: str | None = None,
    group_size: int = 1,
    additional_notes: str = "",
) -> dict[str, Any]:
    """Build final payload from flat fields to avoid nested tool-call errors."""
    budget_location = collect_budget_and_location(
        budget_currency=budget_currency,
        budget_min=budget_min,
        budget_max=budget_max,
        location_city=location_city,
        location_region=location_region,
        location_country=location_country,
    )
    interest_profile = collect_interests_and_profile(
        interests=interests,
        age=age,
        education_level=education_level,
        travel_style=travel_style,
        mobility_needs=mobility_needs,
    )
    return build_activity_handoff_payload(
        budget_location_data=budget_location,
        interest_profile_data=interest_profile,
        timeframe_start=timeframe_start,
        timeframe_end=timeframe_end,
        group_size=group_size,
        additional_notes=additional_notes,
    )


root_agent = Agent(
    name="tourist_interviewer_agent",
    model="gemini-2.5-flash-lite",
    description=(
        "Collects a tourist's preferences and constraints, then structures data for an"
        " activity recommendation agent."
    ),
    instruction=(
        "You are a tourist interview intake agent. Extract information from each user answer"
        " and only ask for missing required fields. When the user answers, extract as many"
        " of the required fields as possible from that single message.\n\n"
        "Required fields (must collect before finalizing):\n"
        "- location_city\n"
        "- location_country\n"
        "- timeframe_start\n"
        "- timeframe_end\n"
        "- budget_currency\n"
        "- budget_min\n"
        "- budget_max\n"
        "- interests (at least 3)\n\n"
        "Optional fields (ask only if user offers or if needed for tie-breakers):\n"
        "- location_region, age, education_level, travel_style, mobility_needs,\n"
        "  group_size, additional_notes\n\n"
        "Behavior rules:\n"
        "- Do not ask for data the user already provided.\n"
        "- After each user message, summarize collected required fields briefly and ask"
        " only for the remaining missing required fields.\n"
        "- If all required fields are present, do not ask more questions.\n"
        "- Build the final payload using build_activity_handoff_payload_flat.\n"
        "- Do not output raw function-call text.\n"
        "- Final response must be only one valid JSON payload in a single ```json code"
        " block, with no additional prose."
    ),
    tools=[
        collect_budget_and_location,
        collect_interests_and_profile,
        build_activity_handoff_payload_flat,
    ],
)
