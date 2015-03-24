a quick and dirty upcoming events reader for cron/conky/zenity
notifications, written in python


## Installation


    git clone <url>
    cd upcoming
    ./run.sh

All the dependencies should be downloaded during the first run. Then,
specify your server url in `conf.json` file and run the shell script again.


    vim conf.json
    ./run.sh


## Configuration

All configuration is done via `conf.json` file. Please note, that all the
parsing job is made using builtin python json reader, which is strict and
doesn't allow fancy stuff like comments and trailing commas.

`conf["url"]`   Url of caldav server, including username and password.

`conf["filter"]["calendars"]`   List of calendars urls to check for upcoming
and recent events. No need to specify full url, a substring is enough.
Example: `["birthdays", "sports", "gigs"]`. Run `./run.sh -ls` command to list all
calendar urls on server.  If empty list `[]` is provided, all calendars
available on the server are checked.

`conf["filter"]["interval"]`    Time interval relative to today, in days, to
check for upcoming and recent events.  Example: `[-7, 50]` past 7 days, today,
and the next 50 days. Both numbers can be negative or positive, floats allowed.

`conf["display"]["timezone"]`   Display events in specified timezone.
Examples: `"Asia/Omsk"`, `"Etc/GMT+7"`, `"UTC"`. For full list,
[see Wikipedia](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

`conf["display"]["event_format"]`   Event output format. By default, a day,
abbr month, and 4-digit year are displaying, followed by tab and event
summary line. Replace `%b` with `%m` for numeric month, `%Y` with `%y` for
two-digit year, delete `\t` to get rid of the tab. See python's 
[strftime()](https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior) and
[format()](https://docs.python.org/2/library/string.html#formatstrings) for full
syntax.


## Command line options

`-ls`   List calendars on server

`-u`    Update python's virtualenv
