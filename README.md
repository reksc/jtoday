#jtoday.py

##### jira timesheet parser

##Installation

```
brew install python3
pip3 install beautifulsoup4
cd jtoday_directory
chmod +x jtoday.py
```

Open ```jtoday.config.json``` file and provide the jira server path, your username and password.

##Usage

```
./jtoday.py [-d DD.MM.YY] [-u user.name] [-p PID]

```

Default params:

- user: current jira user (specified in config file)
- date: today
- project: all

####Arguments
```[--date -d] DD.MM.YY``` - generate report for a given date

```[--user -u] user.name``` - generate report for a given user

```[--project -p] PID``` - generate report for a given project (PID's are set up in the config file)

e.g.

```
jtoday -u john.doe -d 18.02.15 -p AUTOTEN
```

