from datetime import datetime, timedelta

import pytz


def get_yesterday_in_jakarta():
    tz = pytz.timezone("Asia/Jakarta")
    return (datetime.now(tz) - timedelta(days=1)).date()


def get_now_in_jakarta():
    tz = pytz.timezone("Asia/Jakarta")
    return datetime.now(tz)
