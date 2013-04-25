import time
import sys


def simple(every=None, start_time=None, end_time=sys.maxint, **kwargs):
    if not start_time:
        start_time = time.time()

    while start_time<end_time:
        start_time += every
        yield start_time

# def recursive_rep(tup_list, start_time=None):
#     if not start_time:
#         start_time = time.time()
