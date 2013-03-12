SAMPLE_CONFIG = \
    {
    "status": "ON",
    "ttl": 300,
    "name": "blipp",
#   "id": "1234567890",
    "serviceType": "http://some_schema_domain/blipp",
    "runningOn": {
            "href": "http://dev.incntre.iu.edu/nodes/anode",
            "rel": "full"},
    "properties": {
            "configurations": {
                "unis_url":"http://dev.incntre.iu.edu",
                "use_ssl": "",
                "ssl_cert": "cert_file",
                "ssl_key": "key_file",
                "ssl_cafile": "ca_file",
                "domain":"testdomain.net",
                "probe_defaults": {
                    "collection_schedule":"simple",
                    "schedule_params": {"every": 10},
                    "reporting_schedule":"simple|num_measurements...etc",
                    "reporting_params":["arg1", 2],
                    "collection_size":10000000,
                    "collection_ttl":1500000,
                    "ms_url":"http://dev.incntre.iu.edu"},
                "probes": {
                    "ping": {
                        "collection_schedule": "simple",
                        "schedule_params": {"every": 10},
                        "reporting_schedule": "simple",
                        "reporting_params": [6],
                        "ms_url": "someurl",
                        "kwargs": {"remote_host": "google.com",
                                   "timeout": 2,
                                   "packet_size": 56,
                                   "byte_pattern": "0xAAAA"},
                        "targets": [{"kwargs": {"remote_host": "129.62.33.22",
                                                "timeout": 3},
                                     "collection_ttl": 30000,
                                     "schedule_params": {"every": 5}},
                                    {"kwargs": {"remote_host": "bing.com"}, "reporting_params": [7]}]
                        },
                    "cpu": {"collection_schedule": "simple",
                            "schedule_params": 1,
                            "kwargs": {"proc_dir": "/proc"}},
                    "net": {"status": "off",
                            "kwargs": {"proc_dir": "/proc",
                                 "unis_url": "http://www.dev.incntre.iu.edu",
                                 "subject":
                                     "http://www.dev.incntre.iu.edu/nodes/hikerbear"}
                            }
                    }
                }
            }
    }



PING_1 = {"name": "ping",
          "domain":"testdomain.net",
          "unis_url":"http://dev.incntre.iu.edu",
          "runningOn": {"href": "http://dev.incntre.iu.edu/nodes/anode",
                         "rel": "full"},
          "collection_schedule": "simple",
          "schedule_params": {"every": 5},
          "reporting_schedule": "simple",
          "reporting_params": [6],
          "collection_size": 10000000,
          "collection_ttl": 30000,
          "ms_url": "someurl",
          "use_ssl": "",
          "ssl_cert": "cert_file",
          "ssl_key": "key_file",
          "ssl_cafile": "ca_file",
          "properties": {},
          "kwargs": {"remote_host":  "129.62.33.22",
                     "timeout": 3,
                     "packet_size": 56,
                     "byte_pattern": "0xAAAA"}}

PING_2 = {"name": "ping",
          "domain":"testdomain.net",
          "unis_url":"http://dev.incntre.iu.edu",
          "runningOn": {"href": "http://dev.incntre.iu.edu/nodes/anode",
                        "rel": "full"},
          "collection_schedule": "simple",
          "schedule_params": {"every": 10},
          "reporting_schedule": "simple",
          "reporting_params": [7],
          "collection_size": 10000000,
          "collection_ttl": 1500000,
          "use_ssl": "",
          "ssl_cert": "cert_file",
          "ssl_key": "key_file",
          "ssl_cafile": "ca_file",
          "ms_url": "someurl",
          "properties":{},
          "kwargs": {"remote_host": "bing.com",
                     "timeout": 2,
                     "packet_size": 56,
                     "byte_pattern": "0xAAAA"}}

big_config_dict = {"not_in_unis": "file_val",
             "in_unis": "file_val",
             "name": "blipp",
             "id": 1234567890,
             "runningOn":
                 {"href": "http://dev.incntre.iu.edu/nodes/anode",
                  "rel": "full"},
             "probes":
                {"ping":
                      {"collection_schedule": "simple|other poss?",
                       "schedule_params": ["arg1", 2, "arg3"],
                       "reporting_schedule": "simple|num_measurements...etc",
                       "reporting_params": ["arg1", 2],
                       "collection_size": 10000000,
                       "collection_ttl": 1500000,
                       "ms_url": "someurl",
                       "kwargs": {"remote_host": "google.com",
                                  "timeout": 2,
                                  "packet_size": 56,
                                  "byte_pattern": "0xAAAA"},
                       "targets": [{"kwargs": {"remote_host": "129.62.33.22",
                                               "timeout": 3},
                                    "collection_ttl": 30000},
                                   {"kwargs": {"remote_host": "bing.com"}}]},
                  "cpu": {"collection_schedule": "simple",
                          "schedule_params": 1,
                          "kwargs": {"proc_dir": "/proc"}},
                  "net": {"status": "off",
                          "kwargs":
                              {"proc_dir": "/proc",
                               "unis_url": "http://www.dev.incntre.iu.edu",
                               "subject":
                               "http://www.dev.incntre.iu.edu/nodes/hikerbear"}
                          }}}

bootstrap_local_config = {
    "status": "ON",
    "$schema": 'http://unis.incntre.iu.edu/schema/20120709/service#',
    "serviceType": "http://some_schema_domain/blipp",
    "name": "blipp",
    "ttl": 100000,
    "location":{"institution": "blipp unit test inst"},
    "description": "blipp unit test",
    "properties": {
	"configurations": {
	    "unis_url":"http://dev.incntre.iu.edu",
	    "probe_defaults":
	    {"collection_schedule":"builtins.simple",
	     "schedule_params":{"every": 20},
	     "reporting_params":7,
	     "collection_size":10000000,
	     "collection_ttl":1500000,
	     "ms_url":"http://dev.incntre.iu.edu"},
	    "domain":"blippunittest",
	    "hostname":"unittest",
            "host_urn": "urn:ogf:network:domain=blippunittest:node=unittest",
	    "probes":{
		"ping":{
		    "collection_schedule":"simple",
		    "kwargs":{"remote_host":"google.com",
			      "timeout":2,
			      "packet_size":56,
			      "byte_pattern":"0xAAAA"},
		    "targets":[{"kwargs":{"remote_host":"127.0.0.1", "timeout":3}, "collection_ttl":30000},
			       {"kwargs":{"remote_host":"131.253.13.32"}}]
		},
		"cpu":{
		    "collection_schedule":"simple",
		    "schedule_params":{"every": 5},
		    "kwargs":{"proc_dir":"/proc"}
		},
		"net":{
		    "status": "OFF",
		    "kwargs": {"proc_dir":"/proc", "unis_url": "http://dev.incntre.iu.edu"}
		}
	    }
	},
	"summary": {
	    "metadata": []
	}
    }
}
