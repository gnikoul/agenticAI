import os
from pathlib import Path
import subprocess
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

def get_safe_path(relative_path: str) -> Path:
    base = Path("backend/agent_workspace").resolve()
    path = (base / relative_path).resolve()

    if not path.is_relative_to(base):
        raise ValueError("Access outside workspace is forbidden.")

    return path

def get_time():
    """Get the current time of the computer.
    
        Args:
            

        Returns:
            The current time of the computer."""
    current_time = datetime.now().strftime("%H:%M")
    return str(current_time)

def launch_steam():
    """Launches the steam program"""
    steam_path = r"/mnt/d/Program Files (x86)/Steam/steam.exe"

    try:
        subprocess.Popen([steam_path])
        return "Steam launched successfully."
    except FileNotFoundError:
        return f"Steam executable not found: {steam_path}"
    except Exception as e:
        return f"Failed to launch Steam: {e}"

def get_temperature(city: str) -> str:
    """Get the current temperature for a city
    
    Args:
        city: The name of the city

    Returns:
        The current temperature for the city
    """
    temperatures = {
        'New York': '22°C',
        'London': '15°C',
    }
    return temperatures.get(city, 'Unknown')

def web_search(query: str) -> str:
    """Search the web for current information."""

    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    if not TAVILY_API_KEY:
        return "Web search is unavailable: TAVILY_API_KEY is not configured."

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": 5,
            },
            timeout=10,
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            return "No search results found."

        return "\n\n".join(
            f"Title: {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Content: {r['content']}"
            for r in results
        )

    except requests.RequestException as e:
        return f"Web search failed: {e}"
    
available_functions = [
    get_temperature,
    launch_steam,
    web_search,
    get_time
]

function_registry = {
    'get_temperature': get_temperature,
    'launch_steam': launch_steam,
    'web_search': web_search,
    'get_time': get_time
}

