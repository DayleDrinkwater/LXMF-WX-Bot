import requests
from shapely.geometry import Point, Polygon

# Function to fetch weather warnings from NWS API
def fetch_nws_warnings(lat, lon, check_only):
    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            warnings = []
            for feature in data['features']:
                properties = feature['properties']
                warning = {
                    'event': properties['event'],
                    'headline': properties['headline'],
                    'description': properties['description'],
                    'instruction': properties['instruction']
                }
                warnings.append(warning)
                
            if check_only: return bool(warnings)      

            warnings_message = ""
            for warning in warnings:
                warnings_message += (
                    f"\n⚠️ {warning['event']}\n"
                    f"Headline: {warning['headline']}\n"
                    f"Description: {warning['description']}\n"
                    f"Instruction: {warning['instruction']}\n"
                )
            return warnings_message
        else:
            return "No weather warnings."
    else:
        return "Failed to fetch weather warnings."

# Function to fetch weather warnings from Meteoalarm API (EU Only)
def fetch_meteoalarm_warnings(lat, lon, country, check_only):
    country_name = country.replace(" ", "-").lower()
    url = f"https://feeds.meteoalarm.org/api/v1/warnings/feeds-{country_name}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        warnings = data.get('warnings', [])
        user_location = Point(lat, lon)
        relevant_warnings = []

        for warning in warnings:
            for area in warning['alert']['info'][0]['area']:
                if 'polygon' in area:
                    polygon_coords = [
                        tuple(map(float, coord.split(',')))
                        for coord in area['polygon'][0].split()
                    ]
                    polygon = Polygon(polygon_coords)
                    if polygon.contains(user_location):
                        relevant_warnings.append(warning)
                        break

        if check_only:
            return bool(relevant_warnings)
        if relevant_warnings:
            warnings_message = ""
            for warning in relevant_warnings:
                warnings_message += (
                    f"\n⚠️ [b] {warning['alert']['info'][0]['headline']} [/b] \n"
                    f"\n"
                    f"{warning['alert']['info'][0]['parameter'][0]['value']} ({warning['alert']['info'][0]['parameter'][1]['value']})\n"
                    f"From: {warning['alert']['info'][0]['effective']}\n"
                    f"Until: {warning['alert']['info'][0]['expires']}\n"
                    f"Message: {warning['alert']['info'][0]['description']}\n"
                    f"Instruction: {warning['alert']['info'][0]['instruction']}\n"
                )
            return warnings_message
        else:
            return "No weather alerts."
    else:
        return "Failed to fetch weather warnings."

# Function to determine which warning system to use based on location
def fetch_weather_warnings(lat, lon, country=None, check_only=False):
    if country == 'United States':
        return fetch_nws_warnings(lat, lon, check_only)
    elif country in ['United Kingdom', 'Norway', 'Sweden']:
        return fetch_meteoalarm_warnings(lat, lon, country, check_only)
    else:
        return "Weather warnings are currently only available in the US, UK, Norway and Sweden."