import os

APP_NAME = "slack-weather"

DEFAULT_CITY = "Tokyo"
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
EMOJIS = dict(
    rain=":umbrella_with_rain_drops:",
    clouds=":cloud:",
    clear=":sunshine:",
    haze=":fog:",
    snow=":snowflake:",
)

SLACK_SCOPES = ["users.profile:write"]

SLACK_CLIENT_ID = os.environ.get("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.environ.get("SLACK_CLIENT_SECRET")

REDIS_URL = os.environ.get("REDIS_URL")

REDIS_KEY_PREFIX = "slack-weather/user-"

IPSTACK_API_KEY = os.environ.get("IPSTACK_API_KEY")