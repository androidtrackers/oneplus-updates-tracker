from datetime import datetime


def is_newer_datetime(old_datetime, new_datetime):
    return bool(
        datetime.strptime(new_datetime, '%d-%m-%Y') >= datetime.strptime(old_datetime, '%d-%m-%Y')
    )
