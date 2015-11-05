import time
import sys
from dateutil import tz, parser

def scheduled(service, measurement):
    time_slots = list(measurement["scheduled_times"])
    params = measurement["configuration"]["schedule_params"]
    every = float(params["every"])
    while len(time_slots) > 0:
        time_slot = time_slots.pop(0)
        now = time.time()
        this_start = time.mktime(parser.parse(time_slot["start"]).astimezone(tz.tzlocal()).timetuple())
        this_end = time.mktime(parser.parse(time_slot["end"]).astimezone(tz.tzlocal()).timetuple())
        
        while now < this_end:
            yield max(now, this_start)
            now = max(time.time(), now + every)

def onetime(service, measurement):
    params = measurement["configuration"]["schedule_params"]
    start_time = params.get("start_time", time.time())
    yield start_time

def simple(service, measurement):
    params = measurement["configuration"]["schedule_params"]
    start_time = params.get("start_time", time.time())
    end_time = params.get("end_time", sys.maxint)
    every = float(params["every"])
    if not start_time:
        start_time = time.time()

    while start_time<end_time:
        start_time += every
        yield start_time

# def recursive_rep(tup_list, start_time=None):
#     if not start_time:
#         start_time = time.time()

