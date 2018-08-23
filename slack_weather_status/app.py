import logging
from os import path
from urllib.parse import urlencode

import redis
import requests
from flask import Flask, redirect, request, render_template

from slack_weather_status import settings


db = redis.from_url(settings.REDIS_URL)


app = Flask(settings.APP_NAME)


def get_city(address=None):
    if address is None:
        address = request.remote_addr
    url = "http://api.ipstack.com/{0}".format(address)
    res = requests.get(url, params=dict(access_key=settings.IPSTACK_API_KEY))
    if res.status_code != 200:
        raise ValueError("could not get city, got {0}".format(res.status_code))
    return res.json()["city"]


def get_redirect_url(action):
    params = dict(
        client_id=settings.SLACK_CLIENT_ID,
        scope=",".join(settings.SLACK_SCOPES),
        redirect_uri=path.join(request.url_root, "oauth/callback"),
        state=action,
    )
    return "https://slack.com/oauth/authorize?" + urlencode(params)


@app.before_first_request
def setup_logging():
    logging.basicConfig(level=logging.INFO, format=settings.LOG_FORMAT)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register():
    return redirect(get_redirect_url("register"))


@app.route("/unregister")
def unregister():
    return redirect(get_redirect_url("unregister"))


@app.route("/oauth/callback")
def oauth_callback():
    params = dict(
        client_id=settings.SLACK_CLIENT_ID,
        client_secret=settings.SLACK_CLIENT_SECRET,
        code=request.args["code"],
        redirect_uri=path.join(request.url_root, "oauth/callback"),
    )
    res = requests.post("https://slack.com/api/oauth.access", data=params)
    data = res.json()
    ok = data.pop("ok")
    if res.status_code != 200 or not ok:
        return "not ok: {0}".format(data.get("error")), 500
    user_key = settings.REDIS_KEY_PREFIX + "{team_id}-{user_id}".format(**data)
    if request.args.get("state", "register") == "register":
        city = get_city()
        if city:
            data["city"] = city
        db.hmset(user_key, data)
        logging.info("registered user %s with ip %s: %s", user_key, request.remote_addr, data)
        status = "registered"
    else:
        status = "unregistered"
        db.delete(user_key)
        logging.info("unregistered user %s", user_key)
    return render_template("index.html", status=status)
