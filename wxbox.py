import requests
from maidenhead import to_location
from lxmf_bot.lxmfbot import LXMFBot

# Function to convert Maidenhead gridsquare to latitude and longitude
def gridsquare_to_latlon(gridsquare):
    lat, lon = to_location(gridsquare)
    return lat, lon

# Function to fetch weather data from Open-Meteo API
def fetch_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['current_weather']
        return f"Temperature: {weather['temperature']}°C, Wind Speed: {weather['windspeed']} km/h"
    else:
        return "Failed to fetch weather data."

# Create an instance of LXMFBot
bot = LXMFBot("weatherbot")

# Define a function to handle received messages
@bot.received
def handle_msg(msg):
    gridsquare = msg.content.strip()
    try:
        lat, lon = gridsquare_to_latlon(gridsquare)
        weather_info = fetch_weather(lat, lon)
        msg.reply(weather_info)
    except Exception as e:
        msg.reply(f"Error: {str(e)}")

# Run the bot
bot.run()