import requests
from maidenhead import to_location
from datetime import datetime
import re

#checks to see if the location is a Maidenhead Gridsquare or a location name, returns the latitude and longitude of the location
def get_lat_lon(location):
    if is_gridsquare(location):
        lat, lon = gridsquare_to_latlon(location)
        location_name = location
    else:
        lat, lon, location_name = location_name_to_latlon(location)
    return lat, lon, location_name

# Function to convert Maidenhead gridsquare to latitude and longitude
def gridsquare_to_latlon(gridsquare):
    lat, lon = to_location(gridsquare)
    return lat, lon

def location_name_to_latlon(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location_name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'LXMFWxBot/1.0 (https://github.com/DayleDrinkwater/LXMF-WX-Bot)'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon']), data[0]['display_name']
    return None, None, None

def is_gridsquare(location):
    """
    Determine if the provided location is a Maidenhead gridsquare.
    
    Args:
    location (str): The location string provided by the user.
    
    Returns:
    bool: True if the location is a gridsquare, False otherwise.
    """
    gridsquare_pattern = r'^[A-R][A-R][0-9][0-9][A-X][A-X]?$'
    return bool(re.match(gridsquare_pattern, location.upper()))


# Dictionary to map weather options to their respective API URLs
WEATHER_API_URLS = {
    'now': "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
    'forecast': "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
}

# Helper function to get the appropriate URL based on the weather option
def get_weather_url(lat, lon, option):
    if option in WEATHER_API_URLS:
        return WEATHER_API_URLS[option].format(lat=lat, lon=lon)
    else:
        raise ValueError(f"Unknown weather option: {option}")

# Function to fetch weather data from Open-Meteo API
def fetch_weather(lat, lon, option):
    url = get_weather_url(lat, lon, option)
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if option == 'now':
            current_weather = data['current_weather']
            return (
                f"Temperature: {current_weather['temperature']}°C, "
                f"Wind Speed: {current_weather['windspeed']} km/h, "
                f"Condition: {get_weather_condition(current_weather['weathercode'])}"
            )
        if option == 'forecast':
            daily = data['daily']
            forecast_message = "7-Day Forecast:\n"
            for i in range(7):
                date = datetime.strptime(daily['time'][i], '%Y-%m-%d')
                day_name = date.strftime('%A')
                weather_code = daily['weathercode'][i]
                weather_condition = get_weather_condition(weather_code)
                forecast_message += (
                    f"{day_name}: Max Temp: {daily['temperature_2m_max'][i]}°C, "
                    f"Min Temp: {daily['temperature_2m_min'][i]}°C, Condition: {weather_condition}\n"
                )
            return forecast_message
    else:
        return "Failed to fetch weather data."
    

    # Function to map weather codes to conditions
def get_weather_condition(code):
    weather_conditions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle: Light",
        53: "Drizzle: Moderate",
        55: "Drizzle: Dense intensity",
        56: "Freezing Drizzle: Light",
        57: "Freezing Drizzle: Dense intensity",
        61: "Rain: Slight",
        63: "Rain: Moderate",
        65: "Rain: Heavy intensity",
        66: "Freezing Rain: Light",
        67: "Freezing Rain: Heavy intensity",
        71: "Snow fall: Slight",
        73: "Snow fall: Moderate",
        75: "Snow fall: Heavy intensity",
        77: "Snow grains",
        80: "Rain showers: Slight",
        81: "Rain showers: Moderate",
        82: "Rain showers: Violent",
        85: "Snow showers: Slight",
        86: "Snow showers: Heavy",
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_conditions.get(code, "Unknown")