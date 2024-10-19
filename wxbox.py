import requests
from maidenhead import to_location
from lxmfbot.lxmfbot import LXMFBot
from datetime import datetime

# Function to convert Maidenhead gridsquare to latitude and longitude
def gridsquare_to_latlon(gridsquare):
    lat, lon = to_location(gridsquare)
    return lat, lon

# Dictionary to map weather options to their respective API URLs
WEATHER_API_URLS = {
    'default': "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
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
        if option == 'default':
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

# Create an instance of LXMFBot
bot = LXMFBot("Test-WeatherBot")

# Define a function to handle received messages
@bot.received
def handle_msg(msg):
    content = msg.content.strip()
    if content.lower() in ['help', '?']:
        help_message = (
            "To use this bot, send a message with a gridsquare location.\n"
            "The bot will respond with the current weather information for that location.\n"
            "Example: 'FN31pr'\n"
            "Send 'forecast <gridsquare>' to get a 7-day weather forecast.\n"
            "Send 'Help' or '?' to see this message again."
        )
        msg.reply(help_message)
    elif content.lower().startswith('forecast'):
        try:
            gridsquare = content.split()[1]
            lat, lon = gridsquare_to_latlon(gridsquare)
            forecast_info = fetch_weather(lat, lon, option='forecast')
            msg.reply(forecast_info)
        except Exception as e:
            msg.reply(f"Error: {str(e)}")
    else:
        try:
            lat, lon = gridsquare_to_latlon(content)
            weather_info = fetch_weather(lat, lon, option='default')
            msg.reply(weather_info)
        except Exception as e:
            msg.reply(f"Error: {str(e)}")

# Run the bot
bot.run()