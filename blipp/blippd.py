'''
Usage:
  blippd [options]

Options:
  -c FILE --config-file=FILE   The json formatted config file.
  -u URL --unis-url=URL        Where UNIS is running.
  -n NID --node-id=NID         ID of the node entry in UNIS that this blipp instance is running on.
  -s SID --service-id=SID      ID of the service entry in UNIS that this blipp should pull config from.
  -e ACTION --existing=ACTION  What to do with measurements already in UNIS (ignore|use) [default: ignore]
  -S ON --scheduler-mode=ON    Work as a remote scheduler mode on/off
'''

from blipp_conf import BlippConfigure
import settings
import arbiter
import pprint
import docopt
import json
from copy import deepcopy
from utils import merge_dicts, delete_nones
import blipp.unis_client
import time
import datetime
import pytz
# import cProfile

logger = settings.get_logger('ablippd')

def get_options():
    options = docopt.docopt(__doc__)
    return options

def main(options=None):

    options = get_options() if not options else options
    conf = deepcopy(settings.STANDALONE_DEFAULTS)
    cconf = {
        "id": options.get("--service-id", None),
        "name": "blipp",
        "properties": {
            "configurations": {
                "unis_url": options.get("--unis-url", None),

            }
        }
    }
    delete_nones(cconf)
    merge_dicts(conf, cconf)

    if options['--config-file']:
        fconf = get_file_config(options['--config-file'])
        merge_dicts(conf, fconf)

    bconf = BlippConfigure(initial_config=conf,
                           node_id=options['--node-id'],
                           pre_existing_measurements=options['--existing'])
    
    # this following 'if' may be deprecated. it turns a BLiPP instance into a scheduler
    if options['--scheduler-mode'] == "on":
        from schedules.adaptive import get_conflicting_measurements
        from schedules.adaptive import get_conflicting_times
        from schedules.adaptive import build_basic_schedule
    
        lastime = int(time.time() * 10e5)
        service = bconf.config
        unis = blipp.unis_client.UNISInstance(service)
        
        while True:
            # lookup db for new measurements requests
            # this query requires some modification on periscope to handle keyword exists
            unscheduled = unis.get("/measurements?ts=gte=" + str(lastime) + "&scheduled_times=exists=boolean:false")
            lastime = int(time.time() * 10e5)

            if len(unscheduled) > 0:
                # new measurements found, schedule them one by one
                for m in unscheduled:
                    # get all measurements containing time slot(s) ending after "now"
                    conflicting_times = get_conflicting_times(
                        get_conflicting_measurements(unis, m))

                    # build schedule, avoiding all conflicting time slots
                    now = datetime.datetime.utcnow()
                    now = pytz.utc.localize(now)
                    
                    schedule = build_basic_schedule(now, 
                        datetime.timedelta(m["configuration"]["schedule_params"]["every"]),
                        datetime.timedelta(m["configuration"]["schedule_params"]["duration"]),
                        m["configuration"]["schedule_params"].get('num_to_schedule', 10),
                        conflicting_times)

                    # update schedule in UNIS
                    m["scheduled_times"] = schedule
                    del m["ts"]
                    unis.put("/measurements/" + m["id"], data=m)
        
            # pulling interval 60s
            time.sleep(60)   
    
    bconf.initialize()
    # EK: don't need to refresh right away, right?
    #bconf.refresh()

    config = bconf.config
    logger.info('main', config=pprint.pformat(config))

    arbiter.main(bconf)

def get_file_config(filepath):
    try:
        with open(filepath) as f:
            conf = f.read()
            return json.loads(conf)
    except IOError as e:
        logger.exc('get_file_config', e)
        logger.error('get_file_config',
                     msg="Could not open config file... exiting")
        exit(1)
    except ValueError as e:
        logger.exc('get_file_config', e)
        logger.error('get_file_config',
                     msg="Config file is not valid json... exiting")
        exit(1)

if __name__=="__main__":
    main()
#    cProfile.run('main(get_options())', 'blippprof')
