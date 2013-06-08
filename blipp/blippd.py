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
# import cProfile

logger = settings.get_logger('blippd')

def get_options():
    options = docopt.docopt(__doc__)
    return options

def main(options=None):
    options = get_options() if not options else options
    bconf = BlippConfigure(file_loc=options['--config-file'],
                           unis_url=options['--unis-url'],
                           service_id=options['--service-id'],
                           service_name='blipp',
                           node_id=options['--node-id'])

    bconf.refresh_config()

    config = bconf.config
    logger.info('main', config=pprint.pformat(config))

    arbiter.main(bconf)

if __name__=="__main__":
    main()
#    cProfile.run('main(get_options())', 'blippprof')
