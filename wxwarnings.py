import requests
from shapely.geometry import Point, Polygon, MultiPolygon
import xml.etree.ElementTree as ET
import json
import os
import csv
import datetime

# --- Meteoalarm geocodes are loaded once and only used for Meteoalarm warnings ---
METEOALARM_GEOCODES_PATH = os.path.join(os.path.dirname(__file__), "geocodes.json")
METEOALARM_GEOCODES = None
if os.path.exists(METEOALARM_GEOCODES_PATH):
    with open(METEOALARM_GEOCODES_PATH, "r") as f:
        METEOALARM_GEOCODES = json.load(f).get("features", [])

METEOALARM_ALIASES_PATH = os.path.join(os.path.dirname(__file__), "geocodes-aliases.csv")
METEOALARM_ALIASES = {}
if os.path.exists(METEOALARM_ALIASES_PATH):
    with open(METEOALARM_ALIASES_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Only use the first alias for each code
            if row["CODE"] not in METEOALARM_ALIASES:
                METEOALARM_ALIASES[row["CODE"]] = row["ALIAS_CODE"]

# Function to fetch weather warnings from NWS API (US only)
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
            if check_only:
                return bool(warnings)
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

# Function to fetch weather warnings from Meteoalarm Atom feed (EU only, uses geocodes)
def fetch_meteoalarm_warnings(lat, lon, country_code, check_only=False):
    if not METEOALARM_GEOCODES:
        return "Meteoalarm geocodes data not loaded."

    user_location = Point(lon, lat)
    region_code = None

    matching_regions = []
    for feature in METEOALARM_GEOCODES:
        geom = feature.get("geometry")
        code = feature.get("properties", {}).get("code")
        if not geom or not code:
            continue
        if geom["type"] == "Polygon":
            poly = Polygon(geom["coordinates"][0])
            if poly.contains(user_location):
                matching_regions.append((code, poly.area))
        elif geom["type"] == "MultiPolygon":
            multipoly = MultiPolygon([Polygon(coords[0]) for coords in geom["coordinates"]])
            if multipoly.contains(user_location):
                matching_regions.append((code, multipoly.area))

    if matching_regions:
        region_code = min(matching_regions, key=lambda x: x[1])[0]
    else:
        region_code = None

    if region_code in METEOALARM_ALIASES:
        print(f"DEBUG: region_code {region_code} replaced with alias {METEOALARM_ALIASES[region_code]}")
        region_code = METEOALARM_ALIASES[region_code]

    print(f"DEBUG: Found region_code={region_code} for lon={lon}, lat={lat}")

    if not region_code:
        return "Weather alerts not available for this location."

    feed_url = f"https://feeds.meteoalarm.org/api/v1/warnings/feeds-{country_code.lower().replace(' ', '-')}"
    resp = requests.get(feed_url)
    if resp.status_code != 200:
        return "Failed to fetch weather warnings."

    data = resp.json()
    # Use a dict to keep only the latest alert for each (event, region_code)
    latest_alerts = {}

    for warning_obj in data.get("warnings", []):
        alert = warning_obj.get("alert", {})
        sent = alert.get("sent")
        try:
            sent_dt = datetime.datetime.fromisoformat(sent.replace("Z", "+00:00")) if sent else datetime.datetime.min
        except Exception:
            sent_dt = datetime.datetime.min
        for info in alert.get("info", []):
            event = info.get('event', 'Warning')
            for area in info.get("area", []):
                for geocode in area.get("geocode", []):
                    if geocode.get("value") == region_code:
                        key = (event, region_code)
                        # Only keep the latest alert for this event/region
                        if key not in latest_alerts or sent_dt > latest_alerts[key]['sent_dt']:
                            latest_alerts[key] = {
                                'info': info,
                                'sent_dt': sent_dt
                            }

    # Group warnings by language
    warnings_by_language = {}

    for alert in latest_alerts.values():
        info = alert['info']
        lang = info.get('language', 'unknown')
        warning_text = (
            f"\n⚠️ {info.get('event', 'Warning')}\n"
            f"Headline: {info.get('headline', '')}\n"
            f"Description: {info.get('description', '')}\n"
            f"Instruction: {info.get('instruction', '')}\n"
            f"Severity: {info.get('severity', '')}\n"
            f"Certainty: {info.get('certainty', '')}\n"
            f"Effective: {info.get('effective', '')}\n"
            f"Onset: {info.get('onset', '')}\n"
            f"Expires: {info.get('expires', '')}\n"
            f"Web: {info.get('web', '')}\n"
        )
        warnings_by_language.setdefault(lang, []).append(warning_text)

    if check_only:
        return any(warnings_by_language.values())
    if warnings_by_language:
        result = ""
        for lang, warnings in warnings_by_language.items():
            result += f"\n=== {lang} ===\n"
            result += "\n".join(warnings)
        return result
    else:
        print("DEBUG: No warnings matched region_code.")
        return "No weather alerts."

# Function to determine which warning system to use based on location
def fetch_weather_warnings(lat, lon, country=None, check_only=False):
    if country == 'United States':
        return fetch_nws_warnings(lat, lon, check_only)
    else:
        return fetch_meteoalarm_warnings(lat, lon, country, check_only)