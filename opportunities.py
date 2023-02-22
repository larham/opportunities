#!/usr/bin/env python

import configparser
import datetime
import getpass
import os
import shutil
import sys
import time
import re
import json
from dateutil import tz
import dateutil.parser
import natsort

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_setup import get_webdriver_for

# Program for parsing opportunities data from the Timecounts.com web site.

OPPORTUNITIES_URL = "https://timecounts.org/%s/opportunities/events"
LOGIN_URL = "https://timecounts.org/login"
EVENT_URL = 'https://timecounts.org/%s/events/%s'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
DOWNLOAD_DIR = os.path.dirname(os.path.abspath(
    __file__)) + "/opportunities/"
FAILED_LOGIN_RESULT = "/tmp/post_login_result.html"
UTC_ZONE = tz.gettz('UTC')
PAC_ZONE = tz.gettz('America/Los_Angeles')
OPPORTUNITIES_FILE_BASE = "opportunities-"


def main():
    """
    Download current opportunities, compare against last changed. 
    Only write to standard out if there is an error or a change.
    Only save a new file if there is a change.
    """
    browser = get_browser()
    user, password, org = get_user_pass()
    ensureDirs()

    prev_content = get_previously_downloaded_events()

    login(browser, LOGIN_URL, user, password)

    # redirect after login doesn't seem to happen?
    # perhaps this will fail too if login failed?
    browser.get(OPPORTUNITIES_URL % org)

    # todo was more clear this was useful when redirect happened
    if not is_logged_in(browser):
        print("login unsuccessful")
        sys.exit(1)

    content = str(browser.page_source)

    if not "Events" in content:  # todo is there a better validation?
        print("Cannot find 'Events' in content at: " + OPPORTUNITIES_URL)
        sys.exit(1)

    current_events = parseTimecounts(content)
    prev_events = parseTimecounts(prev_content)

    # this set comparison ignores any old events which were expired by date
    diff = set(current_events.keys()) - set(prev_events.keys())
    if diff:
        save_page(content)
        if not prev_events:
            sys.exit(0)  # first time running comparison

        for key in diff:
            event = current_events[key]
            time_str = event["pac_time"].strftime('%a., %b. %d, (%m/%d/%Y)')
            print(event["name"], "on", time_str, ',', EVENT_URL % (org, key))
            print()


def parseTimecounts(content):
    events = {}
    if not content:
        return events

    # regex to parse "App" json from Timecounts page
    # ASSUMES that all of json is contained on a single line
    match = re.search(
        r'var App = window.App = new TimecountsApp\((.*)\);', content)
    if not match:
        print("cannot find text in page starting with 'var App = window.App = new TimecountsApp'")
        sys.exit(1)

    found = match.group(1)
    parsed = json.loads(found)
    eventMap = parsed["dehydrated_store"]["api"]["models"]
    # print("found ", len(eventMap)-2, " events")
    for key, v in eventMap.items():
        if key[0:5] == "Event":
            name = v["attributes"]["name"]
            id = v["attributes"]["id"]
            utc = dateutil.parser.isoparse(v["attributes"]["start_at"])
            utc = utc.replace(tzinfo=UTC_ZONE)  # tell date it is utc
            pac_time = utc.astimezone(PAC_ZONE)
            # print(id, ":", name, pac_time)
            events[id] = {'name': name, 'pac_time': pac_time, 'id': id}
    return events


def ensureDirs():
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)


def prompt_login_creds():
    user = input("Username: ")
    password = getpass.getpass("Password: ")
    org = input("Organization (lower case, hyphens instead of spaces): ")
    return user, password, org


def login(browser, url, user, password):
    # print("attempting to log in...")
    browser.get(url)
    # wait for full rendering
    submit = WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))

    # print("submit element: %s" % browser.execute_script(
    #     'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', submit))

    email = browser.find_element(By.NAME, "email")
    email.send_keys(user)
    passwd = browser.find_element(By.NAME, "password")
    passwd.send_keys(password)
    submit.click()
    WebDriverWait(browser, 15).until(EC.url_changes(browser.current_url))
    # print("url after login: %s" % browser.current_url)


def pretty_datetime():
    value = datetime.datetime.now()
    return value.strftime('%Y-%m-%dT%H-%M-%S')


def save_page(content):
    filename = DOWNLOAD_DIR + "opportunities-%s.html" % pretty_datetime()
    files = os.listdir(DOWNLOAD_DIR)
    with open(filename, 'w+') as f:
        f.write(content)

    wait4download(DOWNLOAD_DIR, 10, len(files) + 1)
    return str(content)


def wait4download(directory, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        seconds += 1
    return seconds


def is_logged_in(browser):
    # a redirect to a page with a login means that you have NOT successfully logged in.
    # a page with a login has "Sign In" in text.
    success = "Sign in to Timecounts" not in str(browser.page_source)
    if success:
        with open('/tmp/opportunities_successful_login_result.html', 'w+') as f:
            f.write(browser.page_source)
    else:
        with open(FAILED_LOGIN_RESULT, 'w+') as f:
            f.write(browser.page_source)
            print("failed login result page is at %s" % FAILED_LOGIN_RESULT)

    return success


def get_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('no-sandbox')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument(f'user-agent={USER_AGENT}')
    # options.add_experimental_option("prefs", prefs)
    # browser.manage().timeouts().implicitlyWait(10, TimeUnit.SECONDS)
    return get_webdriver_for("chrome", options=options)


def get_user_pass():
    user = ""
    password = ""
    org = ""
    if len(sys.argv) > 1:
        if not os.path.exists(sys.argv[1]):
            print("cannot find file: %s" % sys.argv[1])
            sys.exit(1)
        config = configparser.RawConfigParser()
        config.read(sys.argv[1])
        try:
            user = config.get('Opportunities', 'username')
            password = config.get('Opportunities', 'password')
            org = config.get('Opportunities', 'org')
        except Exception:
            print("""
Expected file to have a header and 2 required entries like:

[Opportunities]
username=myemail@someserver.com
password=mysecretpassword
""")
            sys.exit(1)

    if user == "" or password == "" or org == "":
        user, password, org = prompt_login_creds()
    return user, password, org


def get_previously_downloaded_events():
    prev_content = None
    files = natsort.natsorted(os.listdir(DOWNLOAD_DIR))
    if len(files) > 0:
        last = files[-1]
        filename = DOWNLOAD_DIR + last
        with open(filename, 'r') as f:
            prev_content = f.read()

    # delete unused previous N;
    while len(files) > 24:
        os.remove(os.path.join(DOWNLOAD_DIR, files[0]))
    return prev_content


main()
