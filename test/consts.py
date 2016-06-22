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
                    "ping1": {
                        "probe_module": "ping",
                        "collection_schedule": "simple",
                        "schedule_params": {"every": 5},
                        "reporting_schedule": "simple",
                        "reporting_params": [6],
                        "ms_url": "someurl",
                        "collection_ttl": 30000,
                        "kwargs": {"remote_host": "129.62.33.22",
                                   "timeout": 3,
                                   "packet_size": 56,
                                   "byte_pattern": "0xAAAA"}
                    },
                    "ping2": {
                        "probe_module": "ping",
                        "collection_schedule": "simple",
                        "schedule_params": {"every": 10},
                        "reporting_schedule": "simple",
                        "reporting_params": [7],
                        "ms_url": "someurl",
                        "kwargs": {"remote_host": "bing.com",
                                   "timeout": 2,
                                   "packet_size": 56,
                                   "byte_pattern": "0xAAAA"}
                    },
                    "cpu": {
                        "probe_module": "cpu",
                        "collection_schedule": "simple",
                        "schedule_params": 1,
                        "kwargs": {"proc_dir": "/proc"}
                    },
                    "net": {
                        "probe_module": "net",
                        "status": "off",
                        "kwargs": {"proc_dir": "/proc",
                                   "unis_url": "http://www.dev.incntre.iu.edu",
                                   "subject":
                                   "http://www.dev.incntre.iu.edu/nodes/hikerbear"}
                    }
                }
            }
            }
    }

SAMPLE_STRIPPED =     {
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
                "domain":"testdomain.net"
            }
    }
}

STRIPPED_PROBES = {
    "ping1": {
        "collection_size":10000000,
        "probe_module": "ping",
        "collection_schedule": "simple",
        "schedule_params": {"every": 5},
        "reporting_schedule": "simple",
        "reporting_params": [6],
        "ms_url": "someurl",
        "collection_ttl": 30000,
        "kwargs": {"remote_host": "129.62.33.22",
                   "timeout": 3,
                   "packet_size": 56,
                   "byte_pattern": "0xAAAA"}
    },
    "ping2": {
        "collection_size":10000000,
        "collection_ttl":1500000,
        "probe_module": "ping",
        "collection_schedule": "simple",
        "schedule_params": {"every": 10},
        "reporting_schedule": "simple",
        "reporting_params": [7],
        "ms_url": "someurl",
        "kwargs": {"remote_host": "bing.com",
                   "timeout": 2,
                   "packet_size": 56,
                   "byte_pattern": "0xAAAA"}
    },
    "cpu": {
        "reporting_schedule":"simple|num_measurements...etc",
        "reporting_params":["arg1", 2],
        "collection_size":10000000,
        "collection_ttl":1500000,
        "ms_url":"http://dev.incntre.iu.edu",
        "probe_module": "cpu",
        "collection_schedule": "simple",
        "schedule_params": 1,
        "kwargs": {"proc_dir": "/proc"}
    },
    "net": {
        "collection_schedule":"simple",
        "schedule_params": {"every": 10},
        "reporting_schedule":"simple|num_measurements...etc",
        "reporting_params":["arg1", 2],
        "collection_size":10000000,
        "collection_ttl":1500000,
        "ms_url":"http://dev.incntre.iu.edu",
        "probe_module": "net",
        "status": "off",
        "kwargs": {"proc_dir": "/proc",
                   "unis_url": "http://www.dev.incntre.iu.edu",
                   "subject":
                   "http://www.dev.incntre.iu.edu/nodes/hikerbear"}
    }
}




PING_SCHEMA = {
    "name": "pingschema",
    "address": "iu.edu",
    u"probe_module": u"cmd_line_probe",
    "domain":"testdomain.net",
    "unis_url":"http://dev.incntre.iu.edu",
    "runningOn": {"href": "http://dev.incntre.iu.edu/nodes/anode",
                  "rel": "full"},
    "collection_schedule": "simple",
    "schedule_params": {"every": 10},
    "reporting_schedule": "simple|num_measurements...etc",
    "reporting_params": ['arg1', 2],
    "collection_size": 10000000,
    "collection_ttl": 1500000,
    "ms_url": "http://dev.incntre.iu.edu",
    "use_ssl": "",
    "ssl_cert": "cert_file",
    "ssl_key": "key_file",
    "ssl_cafile": "ca_file",
    "properties": {},
    '$schema': 'file://ping-schema.json',
    u'command': u'ping -W $TIMEOUT -s $PACKET_SIZE -t $TTL -p $PATTERN -M $HINT -Q $TOS $EXTRAARGS $ADDRESS',
    u'regex': u'ttl=(?P<ttl>\\d+).*time=(?P<rtt>\\d+\\.\\d+) ',
    u'eventTypes': {
        u'ttl': u'ps:tools:blipp:linux:net:ping:ttl',
        u'rtt': u'ps:tools:blipp:linux:net:ping:rtt'
    },
    u'timeout': 2,
    u'packet_size': 56,
    u'ttl': 60,
    u'pattern': u'00',
    u'hint': u'dont',
    u'tos': u'0',
    u'extraargs': u'',
}

PING_1 = {"name": "ping1",
          "probe_module": "ping",
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

PING_2= {"name": "ping2",
              "probe_module": "ping",
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
    "$schema": 'http://unis.incntre.iu.edu/schema/20140214/service#',
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
meminfo = """
MemTotal:        8127964 kB
MemFree:          525460 kB
Buffers:          358700 kB
Cached:          4390548 kB
SwapCached:          768 kB
Active:          4015276 kB
Inactive:        3044436 kB
Active(anon):    1950768 kB
Inactive(anon):   367044 kB
Active(file):    2064508 kB
Inactive(file):  2677392 kB
Unevictable:           0 kB
Mlocked:               0 kB
SwapTotal:       5105656 kB
SwapFree:        5104120 kB
Dirty:                96 kB
Writeback:             0 kB
AnonPages:       2309808 kB
Mapped:           173400 kB
Shmem:              7360 kB
Slab:             401292 kB
SReclaimable:     371660 kB
SUnreclaim:        29632 kB
KernelStack:        4672 kB
PageTables:        42628 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:     9169636 kB
Committed_AS:    5341024 kB
VmallocTotal:   34359738367 kB
VmallocUsed:      330620 kB
VmallocChunk:   34359380988 kB
HardwareCorrupted:     0 kB
HugePages_Total:       0
HugePages_Free:        0
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
DirectMap4k:     2021376 kB
DirectMap2M:     6301696 kB"""

user_beancounters = """Version: 2.5
       uid  resource                     held              maxheld              barrier                limit              failcnt
        7:  kmemsize                 61925780             64507904  9223372036854775807  9223372036854775807                    0
            lockedpages                     0                    0  9223372036854775807  9223372036854775807                    0
            privvmpages                312066               321621  9223372036854775807  9223372036854775807                    0
            shmpages                      640                 1296  9223372036854775807  9223372036854775807                    0
            dummy                           0                    0                    0                    0                    0
            numproc                        34                   84  9223372036854775807  9223372036854775807                    0
            physpages                 1173286              1180545  9223372036854775807  9223372036854775807                    0
            vmguarpages                     0                    0  9223372036854775807  9223372036854775807                    0
            oomguarpages                12375                17889  9223372036854775807  9223372036854775807                    0
            numtcpsock                     10                   74  9223372036854775807  9223372036854775807                    0
            numflock                        2                   10  9223372036854775807  9223372036854775807                    0
            numpty                          1                    2  9223372036854775807  9223372036854775807                    0
            numsiginfo                      0                   27  9223372036854775807  9223372036854775807                    0
            tcpsndbuf                  182080              1398784  9223372036854775807  9223372036854775807                    0
            tcprcvbuf                  163840              7966208  9223372036854775807  9223372036854775807                    0
            othersockbuf                14016                41184  9223372036854775807  9223372036854775807                    0
            dgramrcvbuf                     0                 8768  9223372036854775807  9223372036854775807                    0
            numothersock                   94                   99  9223372036854775807  9223372036854775807                    0
            dcachesize               57694551             57798312             60817408             67108864                    0
            numfile                       360                  600  9223372036854775807  9223372036854775807                    0
            dummy                           0                    0                    0                    0                    0
            dummy                           0                    0                    0                    0                    0
            dummy                           0                    0                    0                    0                    0
            numiptent                      20                   20  9223372036854775807  9223372036854775807                    0"""
