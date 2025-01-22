import requests
from maidenhead import to_location
from datetime import datetime
import re

# Returns the latitude, longitude, display name and country code of the location name
def get_lat_lon(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location_name,
        'format': 'json',
        'addressdetails': 1,
        'limit': 1
    }
    headers = {
        'User-Agent': 'LXMFWxBot/1.0 (https://github.com/DayleDrinkwater/LXMF-WX-Bot)',
        'Accept-Language': 'en-GB'
    }
    response = requests.get(url, params=params, headers=headers)
    print(f"Request URL: {response.url}")
    print(f"Response Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Data: {data}")
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            display_name = data[0]['display_name']
            address = data[0].get('address', {})
            country_code = address.get('country_code', '')
            country = address.get('country', '')
            print(f"Parsed Data - Lat: {lat}, Lon: {lon}, Display Name: {display_name}, Country Code: {country_code}")
            return lat, lon, display_name, country
        else:
            print("No data found for the given location.")
    else:
        print("Failed to fetch data from the API.")
    return None, None, None, None, None, None


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