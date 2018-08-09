import os
from os import path

APP_NAME = "slack-weather-status"
USER = "slack-weather-status"
DEFAULT_ROOT = path.join("/home", USER, APP_NAME)
PROJECT_ROOT = os.environ.get("PROJECT_ROOT", DEFAULT_ROOT)
PID_FILE = path.join(PROJECT_ROOT, "tmp", "slack-weather-status.pid")

DEFAULT_CITY = "Tokyo"
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

SLACK_SCOPES = ["users.profile:write"]

SLACK_CLIENT_ID = os.environ.get("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.environ.get("SLACK_CLIENT_SECRET")

REDIS_URL = os.environ.get("REDIS_URL")

REDIS_KEY_PREFIX = "slack-weather/user-"

IPSTACK_API_KEY = os.environ.get("IPSTACK_API_KEY")

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = os.environ.get("PORT", 5005)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

WEATHER_MAPPING = {
    "雨": "rain",
    "くもり": "clouds",
    "晴れ": "clear",
    "雪": "snow",
}

EMOJIS = dict(
    rain=":umbrella_with_rain_drops:",
    clouds=":cloud:",
    clear=":sunshine:",
    haze=":fog:",
    mist=":fog:",
    snow=":snowflake:",
)
