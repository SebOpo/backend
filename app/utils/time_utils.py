import datetime
import time


def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    # Usage example : random_date("1/1/2008 1:30 PM", "1/1/2009 4:50 AM", random.random())
    return str_time_prop(start, end, "%m/%d/%Y %I:%M %p", prop)


def utc_convert(timestamp: datetime.datetime):
    """
    This method is used for transforming python datetime format to include Z (Zulu/Zero offset) so JavaScript frontend
    can correctly understand it.
    See
    https://stackoverflow.com/questions/19654578/python-utc-datetime-objects-iso-format-doesnt-include-z-zulu-or-zero-offset
    for more info.

    :param datetime timestamp: The initial time we want to convert to a JS readable UTC format.
    :return: A converted string with Z at the end.
    """
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
