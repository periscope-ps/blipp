# =============================================================================
#  periscope-ps (blipp)
#
#  Copyright (c) 2013-2016, Trustees of Indiana University,
#  All rights reserved.
#
#  This software may be modified and distributed under the terms of the BSD
#  license.  See the COPYING file for details.
#
#  This software was created at the Indiana University Center for Research in
#  Extreme Scale Technologies (CREST).
# =============================================================================
import random
import calendar
import dateutil.parser
import datetime
import pytz
import time
import re
from pprint import pprint
from pprint import pformat
from blipp import utils
import blipp.settings

from unis import Runtime
from unis.models import Measurement, Service

logger = blipp.settings.get_logger('adaptive')

def simple_avoid(service: Service, measurement: Measurement) -> None:
    config = measurement.configuration
    every = config.schedule_params.every
    duration = config.schedule_params.duration
    num_to_schedule = getattr(config.schedule_params, 'num_to_schedule', 10)
    max_wait = getattr(config.schedule_params, 'max_wait', 3)
    td_duration = datetime.timedelta(seconds=duration)
    td_every = datetime.timedelta(seconds=every)
    unis = utils.get_unis()

    # Wait until resources have been added
    while not hasattr(measurement.configuration, "resources"):
        time.sleep(every/2)
    conflicting_times = None

    while True:
        wait_time = random.random()*max_wait
        logger.info(f"Starting random wait [{wait_time}] for '{config.name}'")
        # wait randomly then regenerate schedule
        time.sleep(wait_time)

        start_scheduler = time.time()

        conflicting_times = get_conflicting_times(
            get_conflicting_measurements(unis, measurement))

        # build schedule, avoiding all conflicting time slots
        now = datetime.datetime.utcnow()
        now = pytz.utc.localize(now)
        schedule = build_basic_schedule(now, td_every, td_duration,
                                        num_to_schedule, conflicting_times)

        # update schedule in UNIS
        measurement.scheduled_times = schedule
        unis.flush()

        logger.debug(f"Completed measurement generation [duration: {time.time()-start_scheduler}]")

        conflicting_times = check_schedule(unis, measurement)
        if conflicting_times:
            logger.info(f"Confict detected in '{config.name}'")
        else:
            # generate finishing times
            for t in schedule:
                yield calendar.timegm(
                    dateutil.parser.parse(t["start"]).utctimetuple())
            # when the schedule is exhausted, loop back to the top and recalculate


#TODO measurement is oftype Measurement (rest of functions in module)
def check_schedule(unis: Runtime, measurement: Measurement) -> list[dict]:
    '''
    Check schedule generated for measurement. If there is a conflicting
    time, return list of scheduled times from measurements that have
    resource conflicts with this measurement. Else return None.
    '''
    cm = get_conflicting_measurements(unis, measurement)
    ct = get_conflicting_times(cm)
    schedule = measurement.scheduled_times
    i = 0
    for c in ct:
        while dateutil.parser.parse(schedule[i].end) <= c['start']:
            i += 1
        if dateutil.parser.parse(schedule[i].start) < c['end']:
            logger.warn(f"{pformat(schedule[i].to_JSON()}"))
            logger.warn(f"start: {datetime_to_dtstring(c['start'])}, end: {datetime_to_dtstring(c['end'])}")
            return ct
    return None

def build_basic_schedule(start, td_every,
                         td_duration, num_to_schedule: int, conflicting_times: list[dict]) -> list[dict]:
    # build schedule, avoiding all conflicting time slots
    schedule = []
    cur = start
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
    return schedule

def get_conflicting_measurements(unis: Runtime, m: Measurement) -> list[Measurement]:
    conflict = []
    for r in  m.configuration.resources:
        for x in unis.measurements.where(lambda x: any([v.ref == r.ref for v in x.configuration.resources])):
            if x.id != m.id:
                conflict.append(x)
    return conflict

def get_conflicting_times(conflicting_measurements: list[Measurements]) -> list[dict]:
    conflict = []
    for m in conflicting_measurements:
        [conflict.append({'start': x.start, 'end': x.end}) for x in getattr(m, 'scheduled_times', [])]
    for c in conflict:
        c['start'] = dateutil.parser.parse(c['start'])
        c['end'] = dateutil.parser.parse(c['end'])
    return sorted(conflict, key=lambda t: t['start'])

def datetime_to_dtstring(dt):
    '''convert datetime object to a date-time string that UNIS will accept '''
    st = dt.isoformat()
    st = st[:st.index('+')]
    st += 'Z'
    st = re.sub("\.[0-9]+", "", st)
    return st

#### Everything below is experimental and untested ####

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

def polite_avoid(config=None: Service, **kwargs):
    max_score = 0.9
    while True:
        unis = utils.get_unis()
        every = config.schedule_params.every
        duration = config.schedule_params.duration
        num_to_schedule = 100
        measurement = unis.measurements.first_where(lambda x : x.configuration.name == config.name && \
                                                    x.service.selfRef == config.serviceRef)

        # Wait until resources have been added
        while not hasattr(measurement.configuration, "resources"):
            time.sleep(every/2)

        # Get all measurements with resource conflicts
        conflicting_measurements = get_conflicting_measurements(unis,
                                                                measurement)
        # Get list of conflicting time objects sorted by start time
        conflicting_times = get_conflicting_times(conflicting_measurements)

        now = datetime.datetime.utcnow()
        now = pytz.utc.localize(now)

        schedule = build_basic_schedule(now, every, duration,
                                        num_to_schedule, conflicting_times)

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
        measurement.scheduled_times = schedule
        unis.flush()

        # generate finishing times
        for t in schedule:
            yield calendar.timegm(
                dateutil.parser.parse(t["start"]).utctimetuple())
