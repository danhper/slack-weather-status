import json

import cachetools
import requests
import redis

from slack_weather_status import settings


WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"


@cachetools.cached(cachetools.TTLCache(1000, 3600))
def get_weather(city):
    params = dict(q=city, APPID=settings.WEATHER_API_KEY)
    res = requests.get(WEATHER_API_URL, params=params)
    if res.status_code != 200:
        raise ValueError("could not get weather, status: {0}".format(res.status_code))
    return res.json()["weather"][0]["main"].lower()


def set_user_profile(user):
    city = user.get(b"city", "Tokyo")
    weather = get_weather(city)
    status = dict(status_emoji=settings.EMOJIS[weather])
    payload = dict(token=user[b"access_token"], profile=json.dumps(status))
    res = requests.post("https://slack.com/api/users.profile.set", data=payload)
    if res.status_code != 200 or not res.json()["ok"]:
        raise ValueError("could not set status")


def set_all_profiles():
    db = redis.from_url(settings.REDIS_URL)
    pattern = settings.REDIS_KEY_PREFIX + "*"
    for user_key in db.keys(pattern):
        user = db.hgetall(user_key)
        set_user_profile(user)


if __name__ == '__main__':
    set_all_profiles()
