.. BLiPP In Depth documentation

.. image:: _static/CREST.png
    :align: center

BLiPP In depth
===================

BLiPP gets its configuration from 4 places

1. UNIS
2. Command line arguments
3. Configuration File
4. Hard coded defaults

UNIS configuration supersedes command line configuration, which supersedes the configuration file, which of course supersedes the hard coded defaults.

Blipp starts with its configuration as the defaults, merges the file configuration over them, overwrites that with anything specified on the command line, and then proceeds to get it’s UNIS configuration as described in the UNIS section below. It might seem complicated, but just remember... UNIS trumps all.

**Command Line Arguments**

1. `-u unis url` - tells blipp where to find a unis instance
2. `-i service id` - blipp can look its service representation and configuration up in UNIS at `unis_url/services/service_id`
3. `-n node id` - if you give blipp the unis id of the node it is running on, it will attempt to find its service configuration that way
4. `-c configuration file` - file path where blipp can load its configuration
5. `-q –no-query` - if this is specified blipp won’t ever query UNIS to find it’s service representation... if id is specified it will still do a direct GET on services for it, but if not it will create a new service in UNIS Blipp cannot start without either a configuration file or UNIS instance.

UNIS
------

BLiPP’s UNIS configuration is tucked under properties.configurations in the its UNIS service definition. BLiPP will try to find its configuration in UNIS in the following ways:

1. It will try a service id if it has one
2. It will query based on the service name (specified in the config file), defaulting to blipp, and the node its running on.
3. It will post whatever configuration it has from defaults, the config file, and the command line to UNIS, creating a new service definition

**Configuration File (All Options) (with comments)**

Configuration File::

    // sample config file for blipp - designed to match unis service definition
    // with blipp specific stuff under ["properties"]["configurations"]
    // service schema http://unis.incntre.iu.edu/schema/20120709/service
    // configuration schema is ###TODO
    // This conf file schema deviates from the service schema only in that it
    // may not require all fields that the schema does
    {
        "status": "ON", // blipp check's for OFF... anything else is ON
        "id": 12345678990, // UNIS adds this
        "selfRef": "https://dev.incntre.iu.edu/services/a733g252367890", // blipp doesn't use this... unis adds it
        "accessPoint": "", // not relevant to blipp (yet?)
        "serviceType": "http://some_schema_domain/blipp", // required to post - blipp puts in automatically
        "name": "blipp", // blipp uses this to query unis if no service_id is provided
        "ttl": 1000, // no plans to implement a lifetime right now
        "ts": 2098340983223, // unis inserts this when the config gets sent to it
        "description": "blipp desc", // will be added by defaults if not specified
        "runningOn":{ // this get's passed on to the probe config
	    "href":"http://dev.incntre.iu.edu/nodes/hikerbear",
	    "rel":"full"
        },
        "properties": {
	    "geni": {"slice_uuid": "someuuid387234deadbeef"}, // slice uuid used for geni auth
	    "configurations": {
	        "unis_url":"http://dev.incntre.iu.edu",
	        "config_file": "/usr/local/etc/blippconfig.json",
	        "unis_poll_interval": 300, // reload config from unis every 300 seconds
	        "use_ssl": false, // JSON boolean value
	        "ssl_cert": "cert_file", // location of cert for auth
	        "ssl_key": "key_file", // location of key for auth
	        // if a string, blipp will attempt to verify the server cert against the CA file
	        // if set to None or "", blipp will not attempt to do verification
	        // if true, web browser style certificate verification is done (handled by python requests)
	        "ssl_cafile": "ca_file",
	        "probe_defaults": { // default config for each probe... will be overridden by
	          	                // anything specified within the probe specific config below
		    "collection_schedule":"builtins.simple", // under schedules dir, look in file
		                                             // builtins for method "simple"
		    "schedule_params":{"every": 10},         // keyword args passed to schedule method
		                                             // in this case, collect every 10 s
		    "reporting_params": 10, // send data every 10 measurements collected
		    "collection_size":10000000, // collection size (bytes) to be created in MS
		    "collection_ttl":1500000, // collection ttl (seconds) for collection in MS
		    "ms_url":"http://dev.incntre.iu.edu" // MS can be specified per probe
	        },
	        // blipp will look for ms_instance and auth_uuid in node.info
	        "gemini_node_info":"/usr/local/etc/node.info",
	        "probes":{ // the keys under probes are the filenames of probes without the ".py"
		           // their values are dictionaries which contain default config for all instances
		           // of that probe. The different instances are in a list of dictionaries
		          // under "targets". The config in each dictionary in the list adds to and
		           // overrides the default config for the probe, as well as the default config
		           // for the whole blipp instance.
		    "ping1":{
		        "probe_module": "ping",
		        "collection_schedule":"builtins.random", // not implemented yet
		        "schedule_params":{"low": 10, "high": 60, "distribution": "poisson"},
		        // wait randomly between 10 and 60 seconds between collections, with a
                        // poisson distribution of wait values (not yet implemented)
		        "reporting_params":10,
		        "collection_size":3000000,
		        "collection_ttl":30000,
		        "address":"129.62.33.22",
		        "timeout":3,
		        "packet_size":56,
		        "byte_pattern":"0xAAAA"
		    },
		    "ping2":{
		        "probe_module": "ping",
		        "collection_schedule":"builtins.random", // not implemented yet
		        "schedule_params":{"low": 10, "high": 60, "distribution": "poisson"},
		        // wait randomly between 10 and 60 seconds between collections, with a
                        // poisson distribution of wait values (not yet implemented)
		        "reporting_params":10,
		        "collection_size":3000000,
		        "collection_ttl":1200000,
		        "address":"bing.com",
		        "timeout":2,
		        "packet_size":56,
		        "byte_pattern":"0xAAAA"
		    },
		    "cpu1":{
		        "probe_module": "cpu",
		        "collection_schedule":"simple",
		        "schedule_params": {"every": 1},
		    },
		    "net1":{
		        "probe_module": "net",
		        "status":"off", // not used yet
		    },
		    "ping3":{ // a more generic way to do ping... or anything else
		        "probe_module": "cmd_line_probe",
		        "command": "ping -c 1 $address", // some command to be executed
		        // a Python regex to extract data from the output of command
		        "regex": "ttl=(?P<ttl>\\d+).*time=(?P<rtt>\\d+\\.\\d+) ",
		        // map regex captures to event Types
		        "eventTypes": {"ttl": "ps:tools:blipp:linux:net:ping:ttl",
			        	   "rtt": "ps:tools:blipp:linux:net:ping:rtt"},
		        "address": "www.google.com"
		    },
		    "ping4": {
		        // another way to specify measurements - the
		        // schema at the url provided has default values
		        // including what probe_module to use, and other
		        // configuration options. Specifying any of them
		        // can override the default value
		        "$schema": "http://unis.incntre.iu.edu/schema/blippmeasurements/20130416/ping",
		        "address": "iu.edu"
		    }
	        }
	    }
        }
    }

**Defaults**
Blipp’s defaults are just a minimal set of configuration to get it up and running - it will continually check its configuration file and/or unis for updates (every 5 minutes by default). Sample defaults (2013-5-22) are below, but you can see the defaults of whatever version of BLiPP you are running in `settings.py` in BLiPP’s source::

    STANDALONE_DEFAULTS = {
        "$schema": SCHEMAS["services"],
        "status": "ON",
        "serviceType": "http://some_schema_domain/blipp",
        "properties": {
            "configurations": {
                "unis_poll_interval":300,
                "use_ssl": "",
	        "ssl_cafile": "",
                "probe_defaults": {
                    "collection_size": 10000000, # ~10 megabytes
                    "collection_ttl": 1500000, # ~17 days
                    "reporting_params": 1
                    }
                }
            }
        }

Scheduling
----------------

Scheduling the running of Probes in BLiPP is handled by python methods in the `schedules` directory of BLiPP’s source. Schedules can be specified in the configuration file on a per-probe basis under the `collection_schedule` key. An example value is `builtins.simple` which means the method `simple` in the file `builtins` in the schedules directory.

**writing your own scheduling method**
Scheduling methods are implemented using Python generators. The basic `simple` schedule method looks like this::

    def simple(every=None, start_time=None, end_time=sys.maxint):
        if not start_time:
            start_time = time.time()

        while start_time < end_time:
            start_time += every
            yield start_time

It simply returns times increasing by the amount `every` which is passed in as an argument.

The basic structure is a loop with a `yield` statement. The `yield` must return the next time (in seconds since the unix epoch), that the probe should be run. The loop could fetch this time from an external source, calculate it based on some parameters, etc... anything that you can do in Python. The arguments passed to the schedule method can also be specified in BLiPP’s configuration under the `schedule_params` key.

What are Probes?
--------------------

Probes are `.py` files which have a class called `Probe` which has a method called `get_data`.

`get_data` takes no arguments, and returns either a dictionary, or a list of dictionaries. The dictionaries can be in one of two formats:

1. No subjects::

    {
      "eventType": data,
      ...
    }

2. With subjects::

    {
      "subject": {
      "eventType": data,
      ...
    },
      ...
    }

“subject” is usually a link to the representation of the subject of the measurement in UNIS. The subject is the actual existing thing that the measurement is about. If subject is not given it defaults to a link to the current node’s UNIS representation. The “eventType” describes what type of thing data is about - usually it is a string like “ps:tools:blipp:linux:network:ip:utilization:packets:in”. The “data” field is just the value of the measurement described by the eventType string, and measured on the subject. Timestamp information will be added by the entity calling get_data (the probe runner), and all the metadata including the eventType will eventually be stored separately from the timestamp/value pairs.

Normally, BLiPP timestamps the data with the time that it made the call to `get_data`, if, however, any of the eventTypes are just the string “ts”, that will be interpreted as a date (if possible), and used as the timestamp.

Interesting Probes
-------------------
**The Command Line Probe (cmd_line_probe)**

The command line probe is a probe for getting data from arbitrary processes as though they were being run at the command line. It is quite flexible but requires some non trivial configuration. It requires 3 things in its “kwargs” dict:

1. A “command” to run - just as it would be run from a shell usually::

    ping -c 1 www.google.com

2. A python regular expression, “regex”, for extracting relevant output from the command. Notice that backslashes are escaped::

    ttl=(?P<ttl>\\\\d+).*time=(?P<rtt>\\\\d+\\\\.\\\\d+)

3. A dictionary “eventTypes” mapping the names of the captured values to event Types::

    {"eventTypes": {"ttl": "ps:tools:blipp:linux:net:ping:ttl",
        "rtt": "ps:tools:blipp:linux:net:ping:rtt"}

Putting it all together, we end up with a probe configuration that looks like::

    "probes":{
      "test_cmd_line_probe": {
          "probe_module": "cmd_line_probe",
          "command": "ping -c 1 www.iu.edu",
          "regex": "ttl=(?P<ttl>\\d+).*time=(?P<rtt>\\d+\\.\\d+) ",
          "eventTypes": {
              "ttl": "ps:tools:blipp:linux:net:ping:ttl",
              "rtt": "ps:tools:blipp:linux:net:ping:rtt"}
          }
      }

measurements, metrics, eventTypes, and metadata
------------------------------------------------
AKA: Lions and Tigers and Bears

**Measurements**
A measurement corresponds to a probe in BLiPP. It is stored in UNIS under `/measurements`, and contains that probe’s configuration. A single measurement might produce multiple metrics each of which has it’s own event type.

**Metrics**
A ‘metric’ is a term used to refer to one of the types of data that a measurement produces. One of the metrics that a ping probe might produce is round trip time. A CPU probe might produce 5 minute load average.

**Event Types**
The eventType is a string that is a more specific description of a metric, it tells more about what a metric means that just round trip time. I don’t think we’ve fully defined what event types need to say, or their structure, but they should at least include the metric, and what tool generated it. i.e. “ps:tools:linux:net:ping:rtt” It could maybe also tell the version of the tool, and what the units of the metric are.

**Metadata**
A peice of metadata corresponds to a metric generated by a particular measurement. Metadata is stored under `/metadata` in UNIS, and each metadata entry has an ID which corresponds to it’s data in the MS. Metadata has a link to the measurement which generated it, and lists the eventType which helps to describe the data it refers to. Ideally, one should be able to tell exactly what some data means, and where it comes from by looking at the metadata (and the measurement it links to). Metadata also has a “subject” which is usually the server or interface (node or port in UNIS terms) that the data is being collected on.

Blipp Command Line
---------------------
Nestled under the newblipp/scripts directory is a little file called `blippcmd.py`. This is BLiPP’s optional command line interface which is useful for making quick changes to BLiPP’s configuration, and then telling it to reload itself without having to wait for the poll interval.

You can navigate through BLiPP’s configuration as though it were a directory structure with familiar unix commands like `cd`, `ls`, `pwd` etc

Run it like so::

    # start it
    $ python blippcmd.py
    # load initial config
    blipp>>> show

**Several commands are possible through the BLiPP CLI.**

1. **show** - fully show the configuration at the current level
2. **pwd** - show what level of the configuration you are on
3. **ls** - show all the key/value pairs, but just keys if the values are dicts with directories shown in blue!
4. **lsd** - show a deep view of everything under the current “directory”
5. **cd <key>** - change config level to be the dict under key
6. **set <key> <val>**
7. **put** - PUT the current config to UNIS
8. **reload** - tell BLiPP to refresh itself based on new config
