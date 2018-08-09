import json
import logging
import re

import cachetools
import requests
import redis
from bs4 import BeautifulSoup

from slack_weather_status import settings


WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
TOKYO_FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/regular_l.xml"


def get_openweathermap_weather(city):
    params = dict(q=city, APPID=settings.WEATHER_API_KEY)
    res = requests.get(WEATHER_API_URL, params=params)
    if res.status_code != 200:
        raise ValueError("could not get weather, status: {0}".format(res.status_code))
    return res.json()["weather"][0]["main"].lower()


def get_tokyo_weather():
    res = requests.get(TOKYO_FEED_URL)
    soup = BeautifulSoup(res.content.decode("utf8"), "lxml")
    selector = dict(text=re.compile(".*?東京都.*?"))
    tokyo_url = soup.find("content", **selector).find_parent("entry").find("link")["href"]
    feed_soup = BeautifulSoup(requests.get(tokyo_url).content.decode("utf-8"), "lxml")
    weather = feed_soup.find("jmx_eb:weather", type="天気").text
    if weather in settings.WEATHER_MAPPING:
        return settings.WEATHER_MAPPING[weather]
    logging.warning("weather %s not found in mappings", weather)
    return get_openweathermap_weather("Tokyo")


@cachetools.cached(cachetools.TTLCache(1000, 1800))
def get_weather(city):
    if city == "Tokyo":
        return get_tokyo_weather()
    return get_openweathermap_weather(city)


def set_user_profile(user):
    city = user.get(b"city", "Tokyo")
    weather = get_weather(city)
    if weather not in settings.EMOJIS:
        logging.warning("%s not found in emojis", weather)
        return
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
    logging.basicConfig(level=logging.INFO, format=settings.LOG_FORMAT)
    set_all_profiles()
