import requests

# Function to fetch weather warnings from NWS API
def fetch_nws_warnings(lat, lon):
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
            return warnings
        else:
            return "No weather warnings."
    else:
        return "Failed to fetch weather warnings."