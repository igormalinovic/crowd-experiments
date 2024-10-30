import datetime

from enum import Enum

class AssetType(Enum):
    SNP500 = 1
    DIGITAL = 2
    OTHER = 3

class Interval(Enum):
    HOUR = 60
    DAY = 1440

def get_last_complete_period(interval: Interval) -> int:
        period_beginning = datetime.datetime.now(tz=datetime.timezone.utc)\
            .replace(minute=0, second=0, microsecond=0)
        if interval == Interval.DAY:
            period_beginning = period_beginning.replace(hour=0)
        return int(period_beginning.timestamp()) - interval.value * 60