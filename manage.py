# -*- coding: utf-8 -*-
import argparse
import os
import signal
import subprocess
import sys

# Project defaults
from utils import utils

# ===== LOAD CONFIGURATION FILE =====
CONFIG_FILE = "conf/conf.json"
CFG, log, = utils.init_main_data(CONFIG_FILE)
if CFG is None or log is None:
    print("Unable to load {}".format(CONFIG_FILE))
    sys.exit(2)
DEFAULT_IP = "{}:{}".format(CFG['network']['host'], CFG['network']["port"])
FLASK_APP = 'server/__init__.py'


class Command:
    def __init__(self, name, descr, runcmd, env=None, conf=None):
        if conf is None:
            conf = {}
        if env is None:
            env = {}
        self.name = name
        self.descr = descr
        self.runcmd = runcmd
        self.env = env
        self.conf = conf

    def run(self, conf):
        cmd = self.runcmd(conf)
        env = os.environ
        env.update(conf)
        env.update(self.env)
        subprocess.call(cmd, env=env, shell=True)


class CommandManager:
    def __init__(self):
        self.commands = {}

    def add(self, command):
        self.commands[command.name] = command

    def configure(self, conf):
        self.conf = conf

    def run(self, command):
        if command in self.commands:
            self.commands[command].run(self.conf)
        else:
            log.debug("invalid command specified\n")
            log.debug(self.availableCommands())

    def availableCommands(self):
        commands = sorted(self.commands.values(), key=lambda c: c.name)
        space = max([len(c.name) for c in commands]) + 2
        description = 'available subcommands:\n'
        for c in commands:
            description += '  ' + c.name + ' ' * (space - len(c.name)) + c.descr + '\n'
        return description


cm = CommandManager()

cm.add(Command(
    "build",
    "compiles python files in project into .pyc binaries",
    lambda c: 'python -m compileall .'))

cm.add(Command(
    "start",
    "runs server with gunicorn in a production setting",
    lambda c: 'gunicorn -b {0}:{1} server:app'.format(c['host'], c['port']),
    {
        'FLASK_APP': FLASK_APP,
        'FLASK_DEBUG': 'false'
    }))

cm.add(Command(
    "run",
    "runs dev server using Flask's native debugger & backend reloader",
    lambda c: 'python -m flask run --host={0} --port={1} --debugger --reload'.format(c['host'], c['port']),
    {
        'FLASK_APP': FLASK_APP,
        'FLASK_DEBUG': 'true'
    }))

cm.add(Command(
    "livereload",
    "runs dev server using livereload for dynamic webpage reloading",
    lambda c: 'python -m flask run',
    {
        'FLASK_APP': FLASK_APP,
        'FLASK_LIVE_RELOAD': 'true',
    }))

cm.add(Command(
    "debug",
    "runs dev server in debug mode; use with an IDE's remote debugger",
    lambda c: 'python -m flask run --host={0} --port={1} --no-debugger --no-reload'.format(c['host'], c['port']),
    {
        'FLASK_APP': FLASK_APP,
        'FLASK_DEBUG': 'true'
    }))

cm.add(Command(
    "test",
    "runs all tests inside of `tests` directory",
    lambda c: 'python -m unittest discover -s tests -p "*.py"'))

# Create and format argument parser for CLI
parser = argparse.ArgumentParser(description=cm.availableCommands(),
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("subcommand", help="subcommand to run (see list above)")
parser.add_argument("ipaddress", nargs='?', default=DEFAULT_IP,
                    help="address and port to run on (i.e. {0})".format(DEFAULT_IP))


def livereload_check():
    check = subprocess.call("lsof -n -i4TCP:{}".format(CFG['network']["port"]), shell=True)
    if check == 0:
        output = subprocess.check_output("ps -ef | egrep 'python manage.py|gunicorn' | egrep -v grep | awk '{print $3}'", shell=True).decode().strip()
        for _pid in output.split("\n"):
            pypid = int(_pid)
            os.kill(pypid, signal.SIGKILL)
            log.debug("Discovered rogue Python process: {0}".format(pypid))
            log.debug("Killing PID {0}...".format(pypid))
    else:
        log.debug(" No rogue Python process running")


# Take in command line input for configuration
try:
    args = parser.parse_args()
    cmd = args.subcommand
    addr = args.ipaddress.split(':')
    cm.configure({
        'host': addr[0],
        'port': addr[1],
    })
    cm.run(cmd)
except KeyboardInterrupt:
    if 'FLASK_LIVE_RELOAD' in os.environ and os.environ['FLASK_LIVE_RELOAD'] == 'true':
        livereload_check()
except:
    if len(sys.argv) == 1:
        log.debug(cm.availableCommands())
    sys.exit(0)
