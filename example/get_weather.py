# get_weather(): Get Local Weather

# I chose to use https://www.weatherapi.com/ because they had a free
# plan and an easy to use API generator with live response.
# Other services that support Python were too heavy with libraries for
# use in MP in my opinion.

from urequests import get as req_get
from json import loads as json_loads
from sys import print_exception
from time import time as time_in_sec

from log_time import log_time
import params

def get_weather(city_url):
    try:
        # https://www.weatherapi.com/
        # e.g. http://api.weatherapi.com/v1/current.json?key={apikey}&q=Toronto&aqi=no
        payload = req_get(url=city_url)
        # Get text representation of string returned and convert the JSON string to Python dictionary object
        pl_dict=json_loads(payload.text)
        # If there was an error in the req_get() call, there will be an 'error' entry in the JSON payload
        if "error" in pl_dict:
            with open(params.log_file,"a") as f:
                f.write(log_time("get_weather")+"Error return from JSON call "+pl_dict["error"])
            raise RuntimeError('Unable to get weather')
        curr=pl_dict["current"]
        cond=curr["condition"]
        last_upd=curr["last_updated"]
        text=cond["text"]
        return {"temp": str(curr["temp_c"]),"feels": str(curr["feelslike_c"]),\
                "last_upd":last_upd,"cond":text,"last_call":time_in_sec()}
        
    except Exception as err:
        with open(params.log_file,"a") as f:
            f.write(log_time("get_weather")+"Exception caught\n")
            print_exception(err,f)
        raise RuntimeError('get_weather failed')       