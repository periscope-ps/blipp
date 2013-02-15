from optparse import OptionParser
from blipp_conf import BlippConfigure
import settings
import probe_arbiter
import pprint
import cProfile


logger = settings.get_logger('start_blipp')

def get_options():
    parser = OptionParser()
    parser.add_option("-c", "--config-file",
                      dest="config_file",
                      help="path to configuration file if it exists")
    parser.add_option("-u", "--unis-url",
                      dest="unis_url",
                      help="URL for UNIS url in form 'http://dev.incntre.iu.edu:8888")
    parser.add_option("-i", "--service-id",
                      dest="service_id",
                      help="service id for blipp configuration already in UNIS",
                      default=None)
    parser.add_option("-n", "--node-id",
                      dest="node_id",
                      help="This machine's id in UNIS",
                      default=None)

    (options, args) = parser.parse_args()
    return options



def main(options=None):
    options = get_options() if not options else options
    bconf = BlippConfigure(file_loc=options.config_file,
                           unis_url=options.unis_url,
                           service_id=options.service_id, service_name='blipp',
                           node_id=options.node_id)

    bconf.refresh_config()
    config = bconf.config

    logger.info('', config=pprint.pformat(config))

    probe_arbiter.main(bconf)



if __name__=="__main__":
    main()
#    cProfile.run('main(get_options())', 'blippprof')

