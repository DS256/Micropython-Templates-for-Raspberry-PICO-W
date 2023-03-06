# params.py - Parameters used by this Micropython project

# Log file name. Appended to by multiple functions
log_file = "LOG.TXT"
# Simply variable to use on conditionl statements 
debug=True

# WiFi Connection values used in BOOT.PY
ssid="your ssid
pwd="your ssid password"

# Datetime Server used in set_rtc()
datetime_server="http://worldtimeapi.org/api/timezone/America/Toronto"

# Weather Server
# from https://www.weatherapi.com/
weather_url={"toronto":"","barrie":"","muskoka":""}
weather_url["toronto"]="http://api.weatherapi.com/v1/current.json?key={your API key}&q=Toronto&aqi=no"
weather_url["barrie"]="http://api.weatherapi.com/v1/current.json?key={your API key}&q=Barrie&aqi=no"
weather_url["muskoka"]="http://api.weatherapi.com/v1/current.json?key={your API key}&q=Muskoka&aqi=no"
