'''
Usage:
  blippd [options]

Options:
  -c FILE --config-file=FILE  The json formatted config file.
  -u URL --unis-url=URL       Where UNIS is running.
  -n NID --node-id=NID        ID of the node entry in UNIS that this blipp instance is running on.
  -s SID --service-id=SID     ID of the service entry in UNIS that this blipp should pull config from.
'''

from blipp_conf import BlippConfigure
import settings
import arbiter
import pprint
import docopt
import json
from copy import deepcopy
from utils import merge_dicts, delete_nones
# import cProfile

logger = settings.get_logger('blippd')

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
                "unis-url": options.get("--unis-url", None),

            }
        }
    }
    delete_nones(cconf)
    merge_dicts(conf, cconf)

    if options['--config-file']:
        fconf = get_file_config(options['--config-file'])
        merge_dicts(conf, fconf)

    bconf = BlippConfigure(initial_config=conf, node_id=options['--node-id'])

    bconf.refresh_config()

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
