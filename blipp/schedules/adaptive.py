import random
import blipp.unis_client
import calendar
import dateutil.parser
import datetime
import pytz
import time
import re
from pprint import pprint

def simple_avoid(config=None, **kwargs):
    while True:
        every = config["schedule_params"]["every"]
        duration = config["schedule_params"]["duration"]
        unis = blipp.unis_client.UNISInstance(config)
        num_to_schedule = 100
        measurement = unis.get(config["measurement"])

        # Wait until resources have been added
        while "resources" not in measurement["configuration"]:
            time.sleep(every/2)
            measurement = unis.get(config["measurement"])

        # Get all measurements with resource conflicts
        conflicting_measurements = get_conflicting_measurements(unis, measurement)

        # Get list of conflicting time objects sorted by start time
        conflicting_times = get_conflicting_times(conflicting_measurements)

        # get duration, every and current time in appropriate formats
        td_duration = datetime.timedelta(seconds=duration)
        td_every = datetime.timedelta(seconds=every)
        now = datetime.datetime.utcnow()
        now = pytz.utc.localize(now)

        # build schedule, avoiding all conflicting time slots
        schedule = []
        for t in conflicting_times:
            while (t["start"] - now) > td_duration:
                schedule.append({"start":datetime_to_dtstring(now), "end":datetime_to_dtstring(now+td_duration)})
                now += td_every
                if len(schedule) >= num_to_schedule:
                    break
            now = t["end"]

        # finish building schedule if there are no more conflicts
        while len(schedule) < num_to_schedule:
            s = datetime_to_dtstring(now)
            e = datetime_to_dtstring(now+td_duration)
            schedule.append({"start":s, "end":e})
            now += td_every

        # update schedule in UNIS
        measurement["scheduled_times"] = schedule
        del measurement["ts"]
        unis.put("/measurements/" + measurement["id"], data=measurement)

        # generate finishing times
        for t in schedule:
            yield calendar.timegm(dateutil.parser.parse(t["start"]).utctimetuple())
        # when the schedule is exhausted, loop back to the top and recalculate

def polite_avoid(config=None, **kwargs):
    max_score = 0.9
    while True:
        every = config["schedule_params"]["every"]
        duration = config["schedule_params"]["duration"]
        unis = blipp.unis_client.UNISInstance(config)
        num_to_schedule = 100
        measurement = unis.get(config["measurement"])

        # Wait until resources have been added
        while "resources" not in measurement["configuration"]:
            time.sleep(every/2)
            measurement = unis.get(config["measurement"])

        # Get all measurements with resource conflicts
        conflicting_measurements = get_conflicting_measurements(unis, measurement)
        # Get list of conflicting time objects sorted by start time
        conflicting_times = get_conflicting_times(conflicting_measurements)

        now = datetime.datetime.utcnow()
        now = pytz.utc.localize(now)

        schedule = build_basic_schedule(now, every, duration, num_to_schedule, conflicting_times)

        # detect congestion and drop a time if we're doing fairly well
        full_schedule = conflicting_times + schedule
        full_schedule = sorted(full_schedule, key=lambda t: t["start"])
        if detect_congestion(duration, full_schedule):
            s = score_schedule(now, full_schedule, every, num_to_schedule)
            if s > max_score:
                drop_at_random(schedule)
            else:
                max_score *= 0.9
        else:
            if max_score < 0.9:
                max_score /= 0.9

        # update schedule in UNIS
        measurement["scheduled_times"] = schedule
        del measurement["ts"]
        unis.put("/measurements/" + measurement["id"], data=measurement)

        # generate finishing times
        for t in schedule:
            yield calendar.timegm(dateutil.parser.parse(t["start"]).utctimetuple())

def build_basic_schedule(start, every, duration, num_to_schedule, conflicting_times):
    # get duration, every and current time in appropriate formats
    td_duration = datetime.timedelta(seconds=duration)
    td_every = datetime.timedelta(seconds=every)
    now = start

    # build schedule, avoiding all conflicting time slots
    schedule = []
    cur = now
    for t in conflicting_times:
        while (t["start"] - cur) > td_duration:
            schedule.append({"start":datetime_to_dtstring(cur),
                             "end":datetime_to_dtstring(cur+td_duration)})
            cur += td_every
            if len(schedule) >= num_to_schedule:
                break
        cur = t["end"]
     # finish building schedule if there are no more conflicts
    while len(schedule) < num_to_schedule:
        s = datetime_to_dtstring(cur)
        e = datetime_to_dtstring(cur+td_duration)
        schedule.append({"start":s, "end":e})
        cur += td_every

def detect_congestion(duration, times):
    td_duration = datetime.timedelta(seconds=duration)
    if len(times) == 0:
        return False
    for i in range(len(times)-1):
        if times[i+1]["start"] - times[i]["end"] > td_duration:
            return False
    return True

def detect_congestion_thresh(threshold, times):
    '''
    threshold between 0 and 1
    return True if times take up more than threshold*total_time_span
    '''
    total_time = times[0]["start"] = times[-1]["end"]
    max_time = threshold * total_time
    acc = 0
    for time in times:
        acc += time["end"] - time["start"]
    return acc > max_time

def drop_at_random(schedule):
    a = len(schedule)
    to_drop = random.randint(0, a-1)
    del schedule[to_drop]

def get_conflicting_measurements(unis, measurement):
    conflicting_measurements = []
    for resource in measurement["configuration"]["resources"]:
        meas_for_resource = unis.get("/measurements?resources.ref=" + resource["ref"])
        filter(lambda m: False if m["id"] == measurement["id"] else True, meas_for_resource)
        conflicting_measurements.extend(meas_for_resource)
    return conflicting_measurements

def get_conflicting_times(conflicting_measurements):
    # aggregate all conflicting times
    conflicting_times = []
    for meas in conflicting_measurements:
        conflicting_times.extend(meas["scheduled_times"])
    # and convert them to datetime objects
    for tobj in conflicting_times:
        tobj["start"] = dateutil.parser.parse(tobj["start"])
        tobj["end"] = dateutil.parser.parse(tobj["end"])

    # sort conflicting intervals by start time
    conflicting_times = sorted(conflicting_times, key=lambda t: t["start"])
    return conflicting_times

def score_schedule(start, schedule, every, n2s):
    '''
    Score a schedule based on how closely it meets it's criteria. Best
    score is 1, worst is negative infinity. 0 happens when it misses
    each time it should run by a full "every". Or if it misses a
    single time by n2s*every.
    '''
    target = start
    total = 1
    for pair in schedule:
        missed_by = pair["start"] - target
        total -= missed_by/(every * n2s)
    return total


def datetime_to_dtstring(dt):
    '''convert datetime object to a date-time string that UNIS will accept '''
    st = dt.isoformat()
    st = st[:st.index('+')]
    st += 'Z'
    st = re.sub("\.[0-9]+", "", st)
    return st
