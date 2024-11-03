import requests

# Function to fetch weather warnings from NWS API
def fetch_nws_warnings(lat, lon):
    # Example implementation, replace with actual API call
    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            return "⚠️ Weather warning in your area."
        else:
            return "No weather warnings."
    else:
        return "Failed to fetch weather warnings."