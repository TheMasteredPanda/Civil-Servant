from enum import Enum

INTERVALS = (
            ('weeks', 604800),
            ('days', 86400),
            ('hours', 3600),
            ('minutes', 60),
            ('seconds', 1)
        )
#The time units used to convert one value in a unit of time to another.
class TimeUnit(Enum):
    MILISECONDS = 'ms' 
    SECONDS = 's'
    MINUTES = 'm' 
    HOURS = 'h'
    DAYS = 'd' 

    @classmethod
    def from_name(cls, name: str):
        for unit in cls:
            if  unit.name == name.upper():
                return unit

#Used to convert a value in one unit of time to another unit of time.
def convert(value: float, time_unit: TimeUnit, to_time_unit: TimeUnit):
    if time_unit == TimeUnit.MILISECONDS:
        if to_time_unit == 0:
            value = value * 1000
        if to_time_unit in (TimeUnit.SECONDS,TimeUnit.MINUTES,TimeUnit.HOURS,TimeUnit.DAYS):
            value = value / 1000
        if to_time_unit in (TimeUnit.MINUTES,TimeUnit.HOURS,TimeUnit.DAYS):
            value = value / 60
        if to_time_unit in (TimeUnit.HOURS,TimeUnit.DAYS):
            value = value / 60
        if to_time_unit == TimeUnit.DAYS:
            value = value / 24
        return value

    if time_unit == TimeUnit.SECONDS:
        if to_time_unit in (TimeUnit.MILISECONDS):
            value = value * 1000
        if to_time_unit == 0:
            value = value * 1000

        if to_time_unit in (TimeUnit.MINUTES,TimeUnit.HOURS,TimeUnit.DAYS):
            value = value / 60
        if to_time_unit in (TimeUnit.HOURS,TimeUnit.DAYS):
            value = value / 60
        if to_time_unit == TimeUnit.DAYS:
            value = value / 24
        return value

    if time_unit == TimeUnit.MINUTES:
        if to_time_unit in (TimeUnit.SECONDS,TimeUnit.MILISECONDS):
            value = value * 60
        if to_time_unit == TimeUnit.MILISECONDS:
            value = value * 1000;

        if to_time_unit in (TimeUnit.HOURS,TimeUnit.DAYS):
            value = value / 60
        if to_time_unit == TimeUnit.DAYS:
            value = value / 24
        return value

    if time_unit == TimeUnit.HOURS:
        if to_time_unit in (TimeUnit.MINUTES,TimeUnit.SECONDS,TimeUnit.MILISECONDS):
            value = value * 60
        if to_time_unit in (TimeUnit.SECONDS,TimeUnit.MILISECONDS):
            value = value * 60
        if to_time_unit in (TimeUnit.MILISECONDS):
            value = value * 1000
        if to_time_unit == 0:
            value = value * 1000
        if to_time_unit == TimeUnit.DAYS:
            value = value / 24
        return value

    if time_unit == TimeUnit.DAYS:
        if to_time_unit in (TimeUnit.HOURS,TimeUnit.MINUTES,TimeUnit.SECONDS,TimeUnit.MILISECONDS):
            value = value * 24
        if to_time_unit in (TimeUnit.MINUTES,TimeUnit.SECONDS,TimeUnit.MILISECONDS):
            value = value * 60
        if to_time_unit in (TimeUnit.SECONDS,TimeUnit.MILISECONDS):
            value = value * 60
        if to_time_unit in (TimeUnit.MILISECONDS):
            value = value * 1000
        if to_time_unit == TimeUnit.MILISECONDS:
            value = value * 1000
        return value

#Formats time into a string. 
# https://stackoverflow.com/questions/4048651/python-function-to-convert-seconds-into-minutes-hours-and-days
def format_time(seconds: int):
    result = []

    for name, count in INTERVALS: 
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result)

