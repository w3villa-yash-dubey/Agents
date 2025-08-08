import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import requests 
import os
from dotenv import load_dotenv 

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city using OpenWeatherMap."""
    print(f"[LOG] Fetching weather for: {city}")

    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather?q={city}"
            f"&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or data.get("cod") != 200:
            return {
                "status": "error",
                "error_message": f"Weather information for '{city}' is not available.",
            }

        temp_c = data["main"]["temp"]
        temp_f = round((temp_c * 9/5) + 32, 2)
        weather_desc = data["weather"][0]["description"]

        report = (
            f"The weather in {city} is {weather_desc} with a temperature of "
            f"{temp_c}°C ({temp_f}°F)."
        )
        return {"status": "success", "report": report}

    except Exception as e:
        return {"status": 'error', "error_message": str(e)}


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    print(f"[LOG] Fetching current time for: {city}")

    # Basic city-to-timezone mapping (could be replaced with geolocation API)
    city_timezones = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
        "delhi": "Asia/Kolkata"
    }

    tz_identifier = city_timezones.get(city.lower())
    if not tz_identifier:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}."
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city.\n"
        "If the user asks for the weather in a state, region, or country without giving a city, "
        "you MUST respond by asking: 'Which city in that state are you asking about?'.\n"
        "Do not call the weather tool until the user provides a specific city name."
    ),
    tools=[get_weather, get_current_time],
)

