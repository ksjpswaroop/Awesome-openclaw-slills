"""Safe skill example: fetches weather data from a public, documented API.

This skill demonstrates best practices:
- Clearly documents network access in the description
- Only reads data, never writes user data to external services
- No shell commands or eval
- No environment variable access
"""

__skill__ = {
    "name": "get_weather",
    "description": (
        "Fetches current weather for a city using the Open-Meteo public API (HTTP GET). "
        "No API key required. Returned data is never forwarded to third parties."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Name of the city (e.g. 'London').",
            }
        },
        "required": ["city"],
    },
}


def get_weather(city: str) -> dict:
    """Return weather information for *city* via Open-Meteo (GET only)."""
    import urllib.request
    import json

    # Geocoding: resolve city name → lat/lon
    geocode_url = (
        f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
    )
    with urllib.request.urlopen(geocode_url) as resp:  # noqa: S310 — GET only
        geo = json.loads(resp.read())

    if not geo.get("results"):
        return {"error": f"City '{city}' not found."}

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current_weather=true"
    )
    with urllib.request.urlopen(weather_url) as resp:  # noqa: S310 — GET only
        data = json.loads(resp.read())

    return data.get("current_weather", {})
