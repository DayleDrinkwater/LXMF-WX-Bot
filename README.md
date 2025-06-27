# LXMF-WX-Bot

LXMF-WX-Bot is a weather bot that provides current weather, forecasts, weather warnings, and satellite images based on a given location or Maidenhead gridsquare. This data is sent via LXMF / Reticulum.

It is very much a work in progress / bad.

## Features

- Get current weather information
- Receive a 7-day weather forecast
- Get current weather warnings (US / Europe only)
- Receive the latest satellite images (certain regions only)

## Commands

- `now <gridsquare/location>`: Get the current weather.
- `forecast <gridsquare/location>`: Get a 7-day weather forecast.
- `warnings <gridsquare/location>`: Get current weather warnings (US / Europe).
- `satellite <gridsquare/location>`: Receive the latest satellite image.

Send `Help` or `?` to see the help message again.

## Installation

To install the required dependencies, run:

```sh
pip install lxmf rns pillow appdirs maidenhead shapely