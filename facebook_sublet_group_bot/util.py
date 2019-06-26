import sys
import subprocess

'''
Project:    RASCAL: Robotic Autonomous Space Cadet Adminstration Lackey
File:       util.py
Author:     Whitney King (@WhitneyOnTheWeb)
Fork:       Zac Sweers FB Modbot (2014 / Py2)

Log:
    - 26/06/2019 (v1.0):
      - Forked repro of old bot used for automodding roommate search FB groups
      - Restructure from Python 2 -> 3.7
      - Add scaffolding for Windows/Mac features
      - Redesign for generalized group administration features
      - Design customized TOCA group administrative features
'''

# Color Class:
# Terminal Display Colors
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# Log Method:
# Checks for Color, then adds log
def log(message, *colorargs):
    if len(colorargs) > 0:
        print(colorargs[0] + message + Color.END)
    else:
        print (message)


# Notify Method:
# Currently just notifies on Mac, needs update for Windows/Linux
def notify_mac():
    if sys.platform == "darwin":
        try:
            subprocess.call(
                ["terminal-notifier", "-message", "Tests done", "-title",
                 "FB_Bot", "-sound", "default"])
        except OSError:
            print("If you have terminal-notifier, this would be a notification")


# Read_Lines Method:
# Reads in multi-line strings based on "newline" type
# http://stackoverflow.com/a/16260159/3034339
def read_lines(f, newline):
    buf = ""
    while True:
        while newline in buf:
            pos = buf.index(newline)
            yield buf[:pos]
            buf = buf[pos + len(newline):]
        chunk = f.read(4096)
        if not chunk:
            yield buf
            break
        buf += chunk