#!/usr/bin/python

import re
import datetime
from datetime import timedelta
import json
import pymongo
import blipp.unis_client
from copy import deepcopy

base_measurement = {
    "$schema": "http://unis.incntre.iu.edu/schema/20130416/measurement#",
    "name": "test measurement 1",
    "service": "http://unis.incntre.iu.edu/services/43287a890f90e908db288",
    "configuration": {
	"$schema": "http://unis.incntre.iu.edu/schema/20130419/blippmeasurement/ping#",
	"address": "stout.incntre.iu.edu",
	"collection_schedule": "adaptive.simple_avoid",
	"schedule_params": {"every": 300, "duration":30}
    },
    "eventTypes": [
	"ps:tools:blipp:linux:net:ping:ttl",
	"ps:tools:blipp:linux:net:ping:rtt"
    ],
    "resources": [
	{ "ref": "a",
	  "usage": { "bandwidth": 10 }
	},
	{ "ref": "b",
	  "usage": { "bandwidth": 10 }
	},
	{ "ref": "c",
	  "usage": { "bandwidth": 10 }
	}
    ]
}

meas_file_base_name = "test_meas_#.json"


def generate_schedule(start_time=None, length=10, duration=30, interval=300):
    if not start_time:
        start_time = datetime.datetime.utcnow()
    td_duration = timedelta(seconds=duration)
    td_interval = timedelta(seconds=interval)

    schedule = []
    for i in range(length):
        s_e = {"start": chop_dec(start_time.isoformat()),
               "end": chop_dec((start_time + td_duration).isoformat())
           }
        schedule.append(s_e)
        start_time += td_interval
    return schedule

def gen_schedules():
    t = datetime.datetime.utcnow()
    td = timedelta(seconds=90)
    schedules = []
    for i in range(3):
        schedules.append(generate_schedule(start_time=t))
        t+=td

    return schedules

def get_test_measurements():
    schedules = gen_schedules()
    measurements = []
    for i in range(len(schedules)):
        #f = open(meas_file_base_name.replace('#', str(i)), 'w')
        bm = deepcopy(base_measurement)
        bm["scheduled_times"] = schedules[i]
        measurements.append(bm)
    return measurements
#        f.write(json.dumps(base_measurement))
#        f.close()


def setup_db():
    c = pymongo.MongoClient()
    c.drop_database("periscope_db")
    unis = blipp.unis_client.UNISInstance({"unis_url":"http://localhost:8888"})
    meass = get_test_measurements()
    for meas in meass:
        unis.post("/measurements", data=meas)

def chop_dec(astr):
    astr = re.sub("\.[0-9]+", "", astr)
    if not astr[-1] == "Z":
        return astr + "Z"
    return astr

if __name__=="__main__":
    setup_db()
