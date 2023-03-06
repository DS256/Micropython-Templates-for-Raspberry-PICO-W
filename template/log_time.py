from time import localtime
# ======== log_time()
# Create a date/time string to start a new LOG_FILE entry
# If called after the time has been set, it will be the UTC time.
# If called before time has been set, not sure what the time will be

# Pad with zeros for single digit to 2 chacters

def pad(val):
    return ("00"+str(val))[-2:]

def log_time(func):
    now = localtime() # RTC time set in set_rtc()
    txt = "\n"+\
        pad(now[0])+"/"+pad(now[1])+"/"+pad(now[2])+\
        " "+pad(now[3])+":"+pad(now[4])+" ["+func+"] "
    return txt