import time
import sys


def simple(service, measurement):
    params = measurement["configuration"]["schedule_params"]
    start_time = params.get("start_time", time.time())
    end_time = params.get("end_time", sys.maxint)
    every = params["every"]
    if not start_time:
        start_time = time.time()

    while start_time<end_time:
        start_time += every
        yield start_time

# def recursive_rep(tup_list, start_time=None):
#     if not start_time:
#         start_time = time.time()
