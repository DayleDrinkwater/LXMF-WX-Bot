import requests
from maidenhead import to_location
from lxmfbot.lxmfbot import LXMFBot
from datetime import datetime
import re
import base64
from PIL import Image
from io import BytesIO
from weather import get_lat_lon, fetch_weather
from wxwarnings import fetch_weather_warnings
from sat import latlon_to_sector

# Create an instance of LXMFBot
bot = LXMFBot("Weather Bot - Send 'Help' for more info",announce=36000)


def send_help_message(msg):
    help_message = (
        "To use this bot, send a message with a command followed by a gridsquare or location.\n"
        "The bot will respond with the requested weather information for that location.\n"
        "\n"
        "Commands:\n"
        "  - 'now <gridsquare/location>': Get the current weather.\n"
        "  - 'forecast <gridsquare/location>': Get a 7-day weather forecast.\n"
        "  - 'warnings <gridsquare/location>': Get current weather warnings (US Only).\n"
        "  - 'satellite <gridsquare/location>': Receive the latest satellite image.\n"
        "\n"
        "Send 'Help' or '?' to see this message again.\n"
        "Weather data by Open-Meteo.com\n"
        "https://github.com/DayleDrinkwater/LXMF-WX-Bot"
    )
    msg.reply(help_message)



def handle_now_request(location, msg):
    lat, lon, location_name, country = get_lat_lon(location)
    if lat is None or lon is None:
        msg.reply("Invalid location. Please provide a valid place name.")
        return
    weather_info = fetch_weather(lat, lon, option='now')
    warnings_info = fetch_weather_warnings(lat, lon, country, check_only=True)
    if warnings_info not in ["Failed to fetch weather warnings.", "No weather warnings."] and warnings_info == True:
        weather_info += "\n⚠️ Weather warning in your area, send 'warnings <location>' for more info."
    msg.reply(f"Current weather for {location_name}:\n{weather_info}\nWeather data by Open-Meteo.com")



def handle_forecast_request(location, msg):
    lat, lon, location_name, country_code= get_lat_lon(location)
    if lat is None or lon is None:
        msg.reply("Invalid location. Please provide a valid place name.")
        return
    forecast_info = fetch_weather(lat, lon, option='forecast')
    warnings_info = fetch_weather_warnings(lat, lon, country_code)
    if warnings_info not in ["Failed to fetch weather warnings.", "No weather warnings."]:
        forecast_info += "\n⚠️ Weather warning in your area, send 'warnings <location>' for more info."
    msg.reply(f"Weather forecast for {location_name}:\n{forecast_info}\nWeather data by Open-Meteo.com")



def handle_warnings_request(location, msg):
    lat, lon, location_name, country = get_lat_lon(location)
    if lat is None or lon is None:
        msg.reply("Invalid location. Please provide a valid place name.")
        return
    warnings_info = fetch_weather_warnings(lat, lon, country)
    msg.reply(f"Weather warnings for {location_name}:\n{warnings_info}")



def handle_satellite_request(location, msg):
    lat, lon, location_name = get_lat_lon(location)
    if lat is None or lon is None:
        msg.reply("Invalid location. Please provide a valid place name.")
        return
    sector_url = latlon_to_sector(lat, lon)
    response = requests.get(sector_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=50)
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        msg.reply(f"Satellite image for {location_name} fetched successfully.", image=image_base64)
    else:
        msg.reply(f"Failed to fetch satellite image for {location_name}. Try again in a few seconds.")

# Define a function to handle received messages
@bot.received
def handle_msg(msg):
    content = msg.content.strip()
    
    # Validate the entire input
    if not re.match(r'^[a-zA-Z0-9\s?,]+$', content):
        msg.reply("Invalid input. Only alphanumeric characters and spaces are allowed.")
        return
    
    if content.lower() in ['help', '?']:
        send_help_message(msg)
    else:
        try:
            command, *args = content.split()
            command = command.lower()
            location = ' '.join(args)  # Join the remaining parts to form the location
            
            handlers = {
                'now': handle_now_request,
                'forecast': handle_forecast_request,
                'warnings': handle_warnings_request,
                'satellite': handle_satellite_request,
            }
            if command in handlers:
                handlers[command](location, msg)  # Pass the location as a single argument
            else:
                msg.reply("Invalid command. Send 'Help' or '?' for a list of commands.")
        except Exception as e:
            msg.reply(f"Error: {str(e)}")

# Run the bot
bot.run()