from slack_weather_status import settings


bind = "{0}:{1}".format(settings.HOST, settings.PORT)
workers = 2
worker_class = "gevent"
pidfile = settings.PID_FILE
