# set_rtc(): Set the Real Time Clock on the PICO W

# This function is called by both BOOT.PY and MAIN.PY since the RTC needs to be
# updated every few hour.

# The PICO W has a RTC but not supported by a battery. That means that when the PICO loses
# power, so does the RTC. It will boot up with its 'epoch' of 2021-01-01 00:00:00.

# Getting the correct time in Micropyton is also complicated because MP does not support time zones.

# I found the link to a site that is called with the city of the time you want which returns both
# the UTC as well as the time in the local time zone

from urequests import get as req_get
from json import loads as json_loads
from machine import RTC
from sys import exit, print_exception
from log_time import log_time
import time
import params

def set_rtc():
    try:
        # http://worldtimeapi.org/
        # e.g. http://worldtimeapi.org/api/timezone/America/Toronto
        payload = req_get(url=params.datetime_server)
        # Get text representation of string returned and convert the JSON string to Python dictionary object
        pl_dict=json_loads(payload.text)
        # If there was an error in the req_get() call, there will be an 'error' entry in the JSON payload
        if "error" in pl_dict:
            with open(params.log_file,"a") as f:
                f.write(log_time("set_rtc")+"Error return from JSON call "+pl_dict["error"])
            raise RuntimeError('Unable to get date/time')

        # Get Day of Week for RTC setting
        dow=int(pl_dict['day_of_week'])

        # Get Current Date Time dictionary entry
        # Looks like this "2023-02-26T16:27:11.683448-05:00"
        dict_date_time=pl_dict['datetime']
        # Separate into [0]="2023-02-26" and [1]="16:27:11.683448-05:00"
        sep_date_time=dict_date_time.split("T")

        # Get date portion of date time
        ext_date=sep_date_time[0]
        ymd=ext_date.split("-")

        # Get time portion. Only need hour:min:second
        ext_time=sep_date_time[1]
        timestr=ext_time.split(".")[0]
        hms=timestr.split(":")

        # Set PICO RTC
        # https://docs.micropython.org/en/latest/library/machine.RTC.html#class-rtc-real-time-clock
        # https://mpython.readthedocs.io/en/master/library/micropython/machine/machine.RTC.html
        # ... it is recommended to perform time calibration every 7 hours.
        # https://github.com/micropython/micropython/issues/10578
        # ports/rtc: Inconsistencies between ports and the documentation
        
        # yr=int(ymd[0]) mt=int(ymd[1]) dy=int(ymd[2])
        # hr=int(hms[0]) min=int(hms[1]) sec=int(hms[2])
        
        rtc=RTC()
        rtc.datetime((int(ymd[0]), int(ymd[1]), int(ymd[2]), dow, \
                     int(hms[0]), int(hms[1]), int(hms[2]), 0))
        
    except Exception as err:
        with open(params.log_file,"a") as f:
            f.write(log_time("set_rtc")+"Exception caught\n")
            print_exception(err,f)
        raise RuntimeError('set_rtc failed')
        