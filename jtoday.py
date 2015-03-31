#!/usr/local/bin/python3
__author__ = 'a.reksc@gmail.com'
__version__ = "0.1.3"

import os
import sys
import json
from http.client import HTTPSConnection
from base64 import b64encode
import urllib.parse
import argparse
import datetime
from bs4 import BeautifulSoup

config = {}
selected_project = False
selected_user = False
selected_date = False

report = ""

def header():
    print("jtoday - jira timesheet parser")
    print("------------------------------")

def project_not_found():
    print("I don't know this project, Dave.")

def report_error():
    print("Error retrieving report - please check your config file")

def load_config():
    global config
    with open(os.path.join(os.path.dirname(__file__), 'jtoday.config.json'), 'r') as f:
        config = json.load(f)

def init():
    global selected_project, selected_user, selected_date, report

    load_config()

    parser = argparse.ArgumentParser(description=header())
    parser.add_argument('-u','--user', help='JIRA username to track',required=False)
    parser.add_argument('-p','--project', help='project ID (AUTOTEN, NCM, NEMTWO)', required=False)
    parser.add_argument('-d','--date', help="date to generate worklog for [DD.MM.YY]", required=False)
    parser.add_argument('--version', '-v', help='display version', action="store_true")
    args = parser.parse_args()

    if args.version:
        print("jtoday.py v" + __version__)
        sys.exit()

    if args.project:
        selected_project = resolve_project(args.project)
        if selected_project is False:
            project_not_found()
            sys.exit()

    selected_user = args.user or config['username']

    if args.date:
        selected_date = datetime.datetime.strptime(args.date, "%d.%m.%y").date().strftime('%d/%b/%y')
    else:
        selected_date = datetime.date.today().strftime('%d/%b/%y')

    report = fetch_report(build_url())

def output_result():
    print(selected_user + " @ " + selected_date)
    print(report)

def build_url():
    params = {'startDate': selected_date,
              'endDate': selected_date,
              'targetUser': selected_user,
              'targetGroup': '',
              'excludeTargetGroup': '',
              'projectRoleId': '',
              'projectid': selected_project if selected_project is not False else '',
              'filterid': '',
              'priority': '',
              'weekends': 'true',
              'showDetails': 'true',
              'groupByField': '',
              'moreFields': '',
              'reportingDay': '',
              'selectedProjectId': selected_project if selected_project is not False else '',
              'reportKey': 'jira-timesheet-plugin:report',
              'Next': 'Next'
    }
    return config['report_path'] + '?' + urllib.parse.urlencode(params)


def fetch_report(report_url):
    response = do_request(report_url)
    report = get_table(response.read())
    return get_work_breakdown(report) if selected_project is False else get_work_total(report)


def do_request(url):
    client = HTTPSConnection(config['jira_host'])
    client.request('GET', url, headers = { 'Authorization' : 'Basic %s' %  b64encode(bytes(config['username'] + ':' + config['password'], "UTF-8")).decode("ascii") })
    return client.getresponse()


def get_table(html):
    soup = BeautifulSoup(html)
    if soup is None:
        report_error()
        sys.exit()
    table = soup.find('table', attrs = {'class': 'aui'})
    if table is None:
        report_error()
        sys.exit()
    return table.find('tbody')

def get_work_total(table):
    row = table.findAll('tr', { 'style' : "background-color: #E0F0FF" })[0]
    total_col = row.findAll('td')[2]
    return "Total: " + str(total_col.find(text=True))

def get_work_breakdown(table):
    projects = ""
    rows = table.findAll("tr")
    for row in rows:
        data = row.find_all("td")
        project_name = data[0].get_text().strip()
        hours_on_project = data[3].get_text().strip() if project_name != "Total" else data[2].get_text().strip()
        projects += "\r\n" + hours_on_project + " | " + project_name
        if project_name == "Total":
            break

    return projects or "Nothing logged"

def resolve_project(id):
    return config['projects'][id] if id in config['projects'] else False

init()
output_result()