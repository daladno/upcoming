from __future__ import unicode_literals

import json
from datetime import datetime, timedelta
import logging
import sys

import caldav
import icalendar
import pytz

CONFIG_FILE = "conf.json"
CONFIG_DEFAULTS = {
    "filter": {
        "calendars": [],
        "interval": [-7, 365]
    },
    "display": {
        "timezone": "UTC",
        "event_format": "{start:%d %b %Y}\t{summary}"
    },
}


_logger = logging.getLogger(__name__)


def main():
    setup_logging()
    try:
        conf = read_config(CONFIG_FILE)
        if '-ls' in sys.argv:
            list_calendars(conf)
        else:
            events = download_upcoming_events(conf)
            display_events(events, conf)
    except Exception as ex:
        uprint(ex)
        _logger.exception('traceback has been silenced:')


def setup_logging():
    logging.basicConfig(filename="errors.log")


def list_calendars(conf):
    calendars = connect(conf['url'])
    if len(calendars) > 0:
        for calendar in calendars:
            uprint(calendar)
    else:
        uprint('No calendars')


def read_config(conf_filename):
    try:
        with open(conf_filename) as fd:
            conf = json.load(fd)
            if 'url' not in conf:
                raise ValueError('No url is set')
            return conf
    except IOError as err:
        raise IOError('Config file reading error: {}'.format(err))
    except ValueError as err:
        raise ValueError('Config json parsing error: {}'.format(err))


def download_upcoming_events(conf):
    calendars_to_display, interval = configure_filters(conf)
    calendars = connect(conf['url'])
    events = []
    if len(calendars) > 0:
        for calendar in calendars:
            if is_in_display_list(calendar, calendars_to_display):
                results = calendar.date_search(interval[0], interval[1])
                for event in results:
                    events.append(event)
    return [parse_event(event) for event in events]


def connect(url):
    try:
        client = caldav.DAVClient(url)
        principal = client.principal()
        return principal.calendars()
    except caldav.lib.error.AuthorizationError:
        raise IOError('Access denied to server, maybe wrong pass')
    except Exception as err:
        desc = str(err) or 'i just dont know what went wrong'
        raise IOError('Network error: {}'.format(desc))


def configure_filters(conf):
    filter = conf.get('filter', CONFIG_DEFAULTS['filter'])
    calendars_to_display = filter.get('calendars',
                                      CONFIG_DEFAULTS['filter']['calendars'])
    if calendars_to_display is not None:
        calendars_to_display = [unicode(c) for c in calendars_to_display]
    interval_rel = filter.get('interval',
                              CONFIG_DEFAULTS['filter']['interval'])
    now = datetime.utcnow()
    try:
        interval_rel[0]+1, interval_rel[1]+1  # make sure they're ints
        interval_abs = (
            now + timedelta(days=interval_rel[0]),
            now + timedelta(days=interval_rel[1]),
        )
    except IndexError:
        raise ValueError('Wrong time interval in config file')
    except TypeError:
        raise ValueError('Strange time interval values in config file')
    return calendars_to_display, interval_abs


def is_in_display_list(calendar, display_list):
    if bool(display_list):
        calendar = unicode(calendar)
        return True if any(
            i in calendar
            for i in display_list
        ) else False
    else:
        return True


def parse_event(caldav_event):
    cal = icalendar.Calendar.from_ical(caldav_event.get_data())
    return cal.subcomponents[0]


def display_events(events, conf):
    ev_format, timezone = configure_display(conf)
    contexts = to_template_contexts(events, timezone)
    if len(contexts):
        try:
            for ctx in contexts:
                uprint(ev_format.format(**ctx))
        except KeyError as err:
            raise ValueError('Wrong event_format line in conf file, at {}'
                             .format(err))

    else:
        uprint("No events")


def configure_display(conf):
    sec_display = conf.get('display', CONFIG_DEFAULTS['display'])
    ev_format = sec_display.get('event_format',
                                CONFIG_DEFAULTS['display']['event_format'])
    tz_name = sec_display.get('timezone',
                              CONFIG_DEFAULTS['display']['timezone'])
    try:
        timezone = pytz.timezone(tz_name)
    except:
        raise ValueError('Unknown timezone in conf file: "{}"'.format(tz_name))
    return ev_format, timezone


def to_template_contexts(events, timezone):
    contexts = [
        to_template_context(ev, timezone)
        for ev in events
        if is_well_formed_event(ev)
    ]
    contexts.sort(key=lambda c: c['start'])
    return contexts


def to_template_context(event, timezone):
    return {
        'start': localize(event['dtstart'], timezone),
        'end': localize(event['dtend'], timezone),
        'summary': event['summary']
    }


def localize(date_field, timezone):
    return timezone.localize(
        datetime.combine(date_field.dt, datetime.min.time())
    )


def is_well_formed_event(event):
    return (
        'dtstart' in event and
        'dtend' in event and
        'summary' in event
    )


def uprint(str):
    u_str = unicode(str)
    bytes_str = u_str.encode('utf-8', errors='ignore')
    print(bytes_str)


if __name__ == '__main__':
    main()
