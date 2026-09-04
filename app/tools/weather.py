from langchain_core.tools import tool

# CONCEPT:
# The LLM does not execute this code directly.
# When the LLM decides it needs weather information, it returns a "Tool Call" command.
# Our application code intercepts this command, runs this Python function, and feeds 
# the return value (the string) back to the LLM.

@tool
def get_weather(location: str) -> str:
    """
    Get the current weather for a specific location.
    Use this tool when the user asks about the weather, temperature, or climate of a city.
    """
    loc_lower = location.lower()
    
    if "hyderabad" in loc_lower:
        return "It is currently 28°C (82°F) and cloudy in Hyderabad, with a 20% chance of rain."
    elif "new york" in loc_lower or "ny" in loc_lower:
        return "It is currently 22°C (72°F) and sunny in New York. A great day to go outside!"
    elif "london" in loc_lower:
        return "It is currently 15°C (59°F) and raining heavily in London. You should carry an umbrella."
    elif "tokyo" in loc_lower:
        return "It is currently 26°C (79°F) and clear in Tokyo."
    else:
        return f"Weather data for '{location}' is not available right now, but it is likely pleasant."
