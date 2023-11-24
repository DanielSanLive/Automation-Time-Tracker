from __future__ import print_function
import time
from os import system
from activity import *
import json
import datetime
import sys

active_window_name = ""
activity_name = ""
start_time = datetime.datetime.now()
activeList = ActivityList([])
first_time = True

def url_to_name(url):
    string_list = url.split('/')
    return string_list[2]

def get_active_window():
    _active_window_name = None
    if sys.platform in ['Windows', 'win32', 'cygwin']:
        from win32 import win32gui
        window = win32gui.GetForegroundWindow()
        _active_window_name = win32gui.GetWindowText(window)
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        try:
            from AppKit import NSWorkspace
            _active_window_name = (NSWorkspace.sharedWorkspace()
                                   .activeApplication()['NSApplicationName'])
        except ImportError:
            print("Error: AppKit module not available on non-Mac platforms.")
    else:
        print("sys.platform={platform} is not supported."
              .format(platform=sys.platform))
        print(sys.version)
    return _active_window_name

def get_firefox_url():
    _active_window_name = None
    if sys.platform in ['Windows', 'win32', 'cygwin']:
        from win32 import win32gui
        window = win32gui.GetActiveWindow()
        if window and isinstance(window, int):
            # Ensure window is not None and is an integer (a valid window handle)
            try:
                window = win32gui.WindowFromHandle(window)
            except:
                return None
        if window and window.title.startswith("Mozilla Firefox"):
            return window.title.replace(" - Mozilla Firefox", "")
        else:
            return None  # Not a Firefox window
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        try:
            from AppKit import NSAppleScript
            text_of_my_script = """tell app "firefox" to get the URL of the active tab of window 1"""
            s = NSAppleScript.initWithSource_(
                NSAppleScript.alloc(), text_of_my_script)
            results, err = s.executeAndReturnError_(None)
            return results.stringValue()
        except ImportError:
            print("Error: NSAppleScript module not available on non-Mac platforms.")
    else:
        print("sys.platform={platform} is not supported."
              .format(platform=sys.platform))
        print(sys.version)
    return _active_window_name


try:
    activeList.initialize_me()
except Exception:
    print('no json')

try:
    while True:
        previous_site = ""
        new_window_name = get_active_window()
        firefox_url = get_firefox_url()

        if firefox_url is not None:
            new_window_name = url_to_name(firefox_url)

        if active_window_name != new_window_name:
            print(active_window_name)
            activity_name = active_window_name

            if not first_time:
                end_time = datetime.datetime.now()
                time_entry = TimeEntry(start_time, end_time, 0, 0, 0, 0)
                time_entry._get_specific_times()

                exists = False
                for activity in activeList.activities:
                    if activity.name == activity_name:
                        exists = True
                        activity.time_entries.append(time_entry)

                if not exists:
                    activity = Activity(activity_name, [time_entry])
                    activeList.activities.append(activity)
                with open('activities.json', 'w') as json_file:
                    json.dump(activeList.serialize(), json_file,
                              indent=4, sort_keys=True)
                    start_time = datetime.datetime.now()
            first_time = False
            active_window_name = new_window_name

        time.sleep(1)

except KeyboardInterrupt:
    with open('activities.json', 'w') as json_file:
        json.dump(activeList.serialize(), json_file, indent=4, sort_keys=True)