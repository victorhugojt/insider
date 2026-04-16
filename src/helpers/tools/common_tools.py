from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen


API_COLOMBIA_CITY_URL = "https://api-colombia.com/api/v1/City"
API_COLOMBIA_ATTRACTIONS_SEARCH_BASE = (
    "https://api-colombia.com/api/v1/TouristicAttraction/search"
)
API_COLOMBIA_FESTIVALS_SEARCH_BASE = (
    "https://api-colombia.com/api/v1/TraditionalFairAndFestival/search"
)

_colombia_cities_cache: list[dict[str, Any]] | None = None
_colombia_cities_raw_cache: list[dict[str, Any]] | None = None
_touristic_attractions_cache: dict[str, list[dict[str, Any]]] = {}
_festivals_cache: dict[str, list[dict[str, Any]]] = {}


def fetch_city_attractions_and_festivals(city_name: str) -> dict[str, list[dict[str, Any]]]:
    """Return touristic attractions and festivals for a city as:
        {'attractions': [...], 'festivals': [...]}
    """
    return {
        "attractions": fetch_touristic_attractions_by_keyword(city_name),
        "festivals": fetch_festivals_by_city(city_name),
    }


def _fetch_colombia_cities_raw() -> list[dict[str, Any]]:
    """Fetch and cache the full city objects from the API."""
    global _colombia_cities_raw_cache
    if _colombia_cities_raw_cache is not None:
        return _colombia_cities_raw_cache

    req = Request(API_COLOMBIA_CITY_URL, headers={"accept": "application/json"})
    with urlopen(req) as resp:  # type: ignore[call-arg]
        data = resp.read()
    parsed = json.loads(data.decode("utf-8"))
    if isinstance(parsed, list):
        _colombia_cities_raw_cache = [x for x in parsed if isinstance(x, dict)]
    else:
        _colombia_cities_raw_cache = []
    return _colombia_cities_raw_cache


def fetch_colombia_cities() -> list[dict[str, Any]]:
    """Fetch the list of Colombian cities from the public API.

    Results are cached in memory for the lifetime of the process so repeated
    calls do not hit the network.
    """
    global _colombia_cities_cache
    if _colombia_cities_cache is not None:
        return _colombia_cities_cache

    rows = _fetch_colombia_cities_raw()
    _colombia_cities_cache = [
        {
            "name": row.get("name"),
            "departmentId": row.get("departmentId"),
        }
        for row in rows
    ]
    return _colombia_cities_cache


def clear_colombia_cities_cache() -> None:
    """Drop the in-memory city list so the next fetch hits the API again."""
    global _colombia_cities_cache, _colombia_cities_raw_cache
    _colombia_cities_cache = None
    _colombia_cities_raw_cache = None


def _parse_attractions_response(parsed: Any) -> list[dict[str, Any]]:
    if isinstance(parsed, list):
        rows = [x for x in parsed if isinstance(x, dict)]
        return [
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "description": row.get("description"),
            }
            for row in rows
        ]
    if isinstance(parsed, dict):
        for key in ("data", "results", "items"):
            inner = parsed.get(key)
            if isinstance(inner, list):
                rows = [x for x in inner if isinstance(x, dict)]
                return [
                    {
                        "id": row.get("id"),
                        "name": row.get("name"),
                        "description": row.get("description"),
                    }
                    for row in rows
                ]
    return []


def fetch_touristic_attractions_by_keyword(keyword: str) -> list[dict[str, Any]]:
    """Search tourist attractions by keyword via the public API.

    Returns a list of attraction dictionaries. Results are cached in memory
    per normalized keyword for the lifetime of the process.
    """
    global _touristic_attractions_cache
    normalized = keyword.strip().lower()
    if not normalized:
        return []
    if normalized in _touristic_attractions_cache:
        return _touristic_attractions_cache[normalized]

    segment = quote(normalized, safe="")
    url = f"{API_COLOMBIA_ATTRACTIONS_SEARCH_BASE}/{segment}"
    req = Request(url, headers={"accept": "application/json"})
    with urlopen(req) as resp:  # type: ignore[call-arg]
        data = resp.read()
    parsed = json.loads(data.decode("utf-8"))
    result = _parse_attractions_response(parsed)
    _touristic_attractions_cache[normalized] = result
    return result


def clear_touristic_attractions_cache() -> None:
    """Drop all cached attraction search results."""
    global _touristic_attractions_cache
    _touristic_attractions_cache = {}


def _parse_festivals_response(parsed: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(parsed, list):
        rows = [x for x in parsed if isinstance(x, dict)]
    elif isinstance(parsed, dict):
        for key in ("data", "results", "items"):
            inner = parsed.get(key)
            if isinstance(inner, list):
                rows = [x for x in inner if isinstance(x, dict)]
                break
    return [
        {
            "name": row.get("name"),
            "description": row.get("description"),
            "month": row.get("month"),
        }
        for row in rows
    ]


def fetch_festivals_by_city(city: str) -> list[dict[str, Any]]:
    """Search traditional fairs and festivals by city name via the public API.

    Returns a list with only id, name and description for each festival.
    Results are cached in memory per normalized city for the lifetime of
    the process.
    """
    global _festivals_cache
    normalized = city.strip().lower()
    if not normalized:
        return []
    if normalized in _festivals_cache:
        return _festivals_cache[normalized]

    segment = quote(normalized, safe="")
    url = f"{API_COLOMBIA_FESTIVALS_SEARCH_BASE}/{segment}"
    req = Request(url, headers={"accept": "application/json"})
    with urlopen(req) as resp:  # type: ignore[call-arg]
        data = resp.read()
    parsed = json.loads(data.decode("utf-8"))
    result = _parse_festivals_response(parsed)
    _festivals_cache[normalized] = result
    return result


def clear_festivals_cache() -> None:
    """Drop all cached festival search results."""
    global _festivals_cache
    _festivals_cache = {}


def get_city_id_by_name(name: str) -> int | None:
    """Return the ID of the first city whose name matches (case-insensitive)."""
    target = name.strip().lower()
    if not target:
        return None

    for city in _fetch_colombia_cities_raw():
        city_name = str(city.get("name", "")).strip().lower()
        if city_name == target:
            try:
                return int(city.get("id"))
            except (TypeError, ValueError):
                return None

    return None

def main():
    print("== Test fetch_city_attractions_and_festivals ==")
    city_data = fetch_city_attractions_and_festivals("medellin")
    print(f"Found {len(city_data['attractions'])} attractions and {len(city_data['festivals'])} festivals.")
    print("\nAttractions:")
    print(json.dumps(city_data["attractions"], indent=2, ensure_ascii=False))
    print("\nFestivals:")
    print(json.dumps(city_data["festivals"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()