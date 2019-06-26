import sys
import csv
import cPickle as pickle
import subprocess

'''----------------------------------------------------------------------------
Project:    RASCAL: Robotic Autonomous Space Cadet Adminstration Lackey
File:       util.py
Author:     @WhitneyOnTheWeb

Original:   ZacSweers FB Modbot (2014 / Py2)

General utility functions for RASCAL operation
----------------------------------------------------------------------------'''
__author__ = 'Whitney King'


'''-------------------------------------
Global Variables
================
'''
isHeroku = False            # is bot running on heroku?
isPickled = False           # is there a .pkl for properties?
prop_file = 'properties'    # properties pickle name


'''-------------------------------------
Class: Color

Text color formatting for logging output
'''
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


'''-------------------------------------
Method: load_list

Generate list of values to be used by RASCAL
- Reads from a .txt file into a list variable

Input:
    <lfile>: name of file containing list with
             syntax (one per line):
             value
Return:
    <list>: with values from file
'''
def load_list(lfile):
    vals = []
    with open('./files/{}'.format(lfile), 'r') as f:
        lst = csv.reader(f)     # get text from file
        for val in lst:         # read each value
            vals.append(val)    # add value to list
    f.close()                   # close file when done
    return vals


'''-------------------------------------
Method: get_settings

Generate settings dictionary with key-value
pairs stored as items in a .txt file

Input:
    <pfile>: name of file with settings using
             syntax (one per line):
             key: value
Return:
    <dict>:  dictionary with settings
             key-value pairs
'''
def get_settings(pfile):
    prop = {}
    with open('./files/{}'.format(pfile), 'r') as keys:
        for key in keys:
            k, v = key.split(': ')
            if v.endswith('\n'): v = v[:-1]
            prop[k] = v
    keys.close()
    return prop


'''-------------------------------------
Method: init_properties

Initializes property values for RASCAL,
then uploads them in chosen format
'''
def init_properties():
    test_dict = get_settings('properties.txt')
    save_properties(test_dict)

    saved_dict = load_properties()
    assert test_dict == saved_dict


'''-------------------------------------
Method: save_properties

Save RASCAL properties to either:
 - memcache (heroku)
 - pickle (local file)
 - text file

Input:
    <data>: dict of property key-value pairs
'''
def save_properties(data):
    if isHeroku:        # save to heroku
        mc.set('properties', data)
    else:               # save to .pkl
        with open(prop_file, 'w+') as f:
            pickle.dump(data, f)
        f.close()
                        # save to .txt
    # with open('./files/properties.txt', 'w') as f:


'''-------------------------------------
Method: load_properties

Loads saved property values from either:
 - memcache (heroku)
 - pickle (local file)
 - text file

 Return:
    <dict>:  dictionary with properties
             key-value pairs
'''
def load_properties():
    if isHeroku:        # load from heroku
        obj = mc.get('properties')
        if not obj:
            return {}
        else:
            return obj
    else:               # load from .pkl
        if os.path.isfile(prop_file):
            with open(prop_file, 'r+') as f:
                data = pickle.load(f)
                return data
        else:           # load from .txt
            return get_settings('properties.txt')


'''-------------------------------------
Method: set_property

Sets key in property dictionary to a
user defined value, updates value in
properties text file

Input:
    <props>:    dict containing properties
    <key>:      key to add or update
    <value>     value to set
'''
def set_property(props, key, value):
    # Add if needed for RASCAL operation
    pass



'''-------------------------------------
Method: log

Checks for Color class, then prints log output

Input:
    <message>: logging message to display
'''
def log(message, *colorargs):
    if len(colorargs) > 0:
        print(colorargs[0] + message + Color.END)
    else:
        print (message)



'''-------------------------------------
Method: notify

Currently sends notifications on Mac

- Needs updates for Windows/Linux
'''
def notify():
    if sys.platform == "darwin":
        try:
            subprocess.call(
                ["terminal-notifier", "-message", "Tests done", "-title",
                 "FB_Bot", "-sound", "default"])
        except OSError:
            print('If you have terminal-notifier, this would notify')


'''-------------------------------------
Method: read_lines

Reads in multi-line strings based on "newline" type
http://stackoverflow.com/a/16260159/3034339

- Needs to be validated
'''
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