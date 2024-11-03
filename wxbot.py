import requests
from maidenhead import to_location
from lxmfbot.lxmfbot import LXMFBot
from datetime import datetime
import re
import base64
from PIL import Image
from io import BytesIO
from weather import gridsquare_to_latlon, fetch_weather
from wxwarnings import fetch_nws_warnings
from sat import latlon_to_sector

# Create an instance of LXMFBot
bot = LXMFBot("Weather Bot - Send 'Help' for more info",announce=36000)


def send_help_message(msg):
    help_message = (
        "To use this bot, send a message with a gridsquare location.\n"
        "The bot will respond with the current weather information for that location.\n"
        "Example: 'IO83PK'\n"
        "\n"
        "Send 'now <gridsquare>' to get the current weather.\n"
        "Send 'forecast <gridsquare>' to get a 7-day weather forecast.\n"
        "\n"
        "Send 'warnings <gridsquare>' to get current weather warnings (US Only).\n"
        "\n"
        "Send 'satellite <gridsquare>' to receive the latest satellite image.\n"
        "\n"
        "\n"
        "Send 'Help' or '?' to see this message again.\n"
        "Weather data by Open-Meteo.com\n"
        "https://github.com/DayleDrinkwater/LXMF-WX-Bot"
    )
    msg.reply(help_message)

def handle_now_request(gridsquare, msg):
    lat, lon = gridsquare_to_latlon(gridsquare)
    weather_info = fetch_weather(lat, lon, option='now')
    warnings_info = fetch_nws_warnings(lat, lon)
    if warnings_info not in ["Failed to fetch weather warnings.", "No weather warnings."]:
        weather_info += "\n⚠️ Weather warning in your area, send 'warnings <gridsquare>' for more info."
    msg.reply(weather_info + "\nWeather data by Open-Meteo.com")

def handle_forecast_request(gridsquare, msg):
    lat, lon = gridsquare_to_latlon(gridsquare)
    forecast_info = fetch_weather(lat, lon, option='forecast')
    warnings_info = fetch_nws_warnings(lat, lon)
    if warnings_info not in ["Failed to fetch weather warnings.", "No weather warnings."]:
        forecast_info += "\n⚠️ Weather warning in your area, send 'warnings <gridsquare>' for more info."
    msg.reply(forecast_info + "\nWeather data by Open-Meteo.com")

def handle_warnings_request(gridsquare, msg):
    lat, lon = gridsquare_to_latlon(gridsquare)
    warnings_info = fetch_nws_warnings(lat, lon)
    msg.reply(warnings_info)

def handle_satellite_request(gridsquare, msg):

            lat, lon = gridsquare_to_latlon(gridsquare)
            sector_url = latlon_to_sector(lat, lon)
            response = requests.get(sector_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                buffered = BytesIO()
                image.save(buffered, format="JPEG", quality=50)
                image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                msg.reply(f"Satellite image fetched successfully.", image=image_base64)
            else:
                msg.reply("Failed to fetch satellite image. Try again in a few seconds.")

# Define a function to handle received messages
@bot.received
def handle_msg(msg):
    content = msg.content.strip()
    
    # Validate the entire input
    if not re.match(r'^[a-zA-Z0-9\s?]+$', content):
        msg.reply("Invalid input. Only alphanumeric characters and spaces are allowed.")
        return
    
    if content.lower() in ['help', '?']:
        send_help_message(msg)
    else:
        try:
            command, *args = content.split()
            command = command.lower()
            
            handlers = {
                'now': handle_now_request,
                'forecast': handle_forecast_request,
                'warnings': handle_warnings_request,
                'satellite': handle_satellite_request,
            }
            if command in handlers:
                handlers[command](*args, msg)
            else:
                msg.reply("Invalid command. Send 'Help' or '?' for a list of commands.")
        except Exception as e:
            msg.reply(f"Error: {str(e)}")

# Run the bot
bot.run()