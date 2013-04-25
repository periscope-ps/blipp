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
        conflicting_measurements = []
        for resource in measurement["configuration"]["resources"]:
            meas_for_resource = unis.get("/measurements?resources.ref=" + resource["ref"])
            filter(lambda m: False if m["id"] == measurement["id"] else True, meas_for_resource)
            conflicting_measurements.extend(meas_for_resource)

        # aggregate all conflicting times
        conflicting_times = []
        for meas in conflicting_measurements:
            conflicting_times.extend(meas["scheduled_times"])
        # and convert them to datetime objects
        for tobj in conflicting_times:
            tobj["start"] = dateutil.parser.parse(tobj["start"])
            tobj["end"] = dateutil.parser.parse(tobj["end"])

        # get duration, every and current time in appropriate formats
        td_duration = datetime.timedelta(seconds=duration)
        td_every = datetime.timedelta(seconds=every)
        now = datetime.datetime.utcnow()
        now = pytz.utc.localize(now)

        # sort conflicting intervals by start time
        conflicting_times = sorted(conflicting_times, key=lambda t: t["start"])

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


def datetime_to_dtstring(dt):
    '''convert datetime object to a date-time string that UNIS will accept '''
    st = dt.isoformat()
    st = st[:st.index('+')]
    st += 'Z'
    st = re.sub("\.[0-9]+", "", st)
    return st
