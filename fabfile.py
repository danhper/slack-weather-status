from os import path

from fabric.api import run, env, cd, put
from fabric.contrib import project, files

from slack_weather_status import settings

env.user = "slack-weather-status"
env.hosts = ["ssh.tuvistavie.com"]

REMOTE_DIR = settings.APP_NAME
PID_FILE = settings.PID_FILE


def deploy():
    project.rsync_project(
        local_dir="./",
        remote_dir=settings.APP_NAME,
        exclude=[".git", ".env", ".vscode", "__pycache__", "tmp", "logs", "build"],
        delete=True
    )
    with cd(REMOTE_DIR):
        run("mkdir -p tmp")
        run("mkdir -p logs")
        run("crontab config/crontab.txt")
        run("pipenv install --deploy")
        run("pipenv run python setup.py install")
        if files.exists(PID_FILE):
            pid = run("cat {0}".format(PID_FILE))
            run("kill -HUP {0}".format(pid))


def upload_env():
    put(".env", path.join(REMOTE_DIR, ".env"))
