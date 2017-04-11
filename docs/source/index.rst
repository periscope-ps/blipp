.. BLiPP documentation

.. image:: _static/CREST.png
     :align: center


BLiPP - Basic Lightweight Periscope Probes
===========================================
BLiPP is a tool that runs on hosts that collects various host and network data and stores in the Measurement Store (MS). It includes provisions for automated, remote configuration via the directory service infrastructure. It is a tool for scheduling and running Probes.

**What’s a Probe?**  
---------------------
A Probe is just a small tool that runs a single measurement. This measurement might report several metrics - for example, the `mem` Probe reports both free memory, and used memory (among other things). A `ping` probe might report the round trip time to it’s destination as well as the time-to-live value on the returned packet. BLiPP works in conjunction with two other services, UNIS, and the Measurement Store (MS).

BLiPP takes all the metrics returned from the *Probe*, adds timestamp information, and send the data to the Measurement Store (MS). BLiPP sends metadata about what sort of information each metric represents to UNIS (a topology and information service). Therefore, one must look in UNIS to see what types of data are being collected, and then into the MS to find the actual data.

Basically UNIS contains information about what’s going on in your network, what nodes and links it has, what services (such as BLiPP) are running, and how they are configured. The MS just contains collections of timestamp value pairs which represent data collected by BLiPP or other tools. Each collection has an associated metadata id which one can use to access information about that particular measurement in the MS.

**What can BLiPP do?**
-------------------------
At a high level, BLiPP is a general framework for running things (*probes*) at scheduled times and gathering information from their output. BLiPP’s design should make it easy to run new things with arbitrary schedules.

BLiPP has built in probes to capture statistics about the usage of network interfaces, memory, and cpu, as well as a generic probe that allows an arbitrary command to be run, and data to be collected from it’s output.

The net, mem and cpu probes all read from the proc filesystem, and therefore will only work on operating systems that support this.

**How is it Configured?**
----------------------------
The basics

When BLiPP starts up, it needs to know 4 things.

1. Where is UNIS?
2. Where is the MS?
3. What Probes should it run?
4. When should those probes be run?

Here’s a minimal configuration file that shows this ::

    {
        "properties": {
	    "configurations": {
	        "unis_url": "http://localhost:8888",
	        "probe_defaults": {
		    "ms_url": "http://localhost:8888",
		    "collection_schedule": "builtins.simple",
		    "schedule_params": {"every": 10}
	        },
	        "probes": {
	        }
	    }
        }
    }

This tells blipp that UNIS and the MS are both running at http://localhost:8888, that it should run no `Probes`, and that they should be run every 10 seconds.
If you change the configuration above under probes to look like this::

    "probes": {
      "minimal_cpu_probe": {
        "probe_module": "cpu"
      }
    }

BLiPP will run the `cpu` probe every 10 seconds.
There are many more possible options, in fact, most aspects of BLiPP’s operation are configurable. After you start BLiPP with this minimal configuration file, it merges in the defaults and pushes it to UNIS - here is what it looks like afterwards::

   {
      "status": "ON",
      "$schema": "http://unis.incntre.iu.edu/schema/20120709/service#",
      "serviceType": "http://some_schema_domain/blipp",
      "name": "blipp",
      "selfRef": "http://localhost:8888/services/519cdd28164ed87d43c55d44",
      "ts": 1369234728270946,
      "id": "519cdd28164ed87d43c55d44",
      "runningOn": {
          "href": "http://localhost:8888/nodes/519cdd27164ed87d43c55d42",
          "rel": "full"
      },
      "properties": {
          "configurations": {
          "unis_poll_interval": 300,
          "config_file": "sample_config/minimalconfig.json",
          "ssl_cafile": "",
          "probe_defaults": {
              "reporting_params": 1,
              "schedule_params": {
                  "every": 10
              },
             "collection_schedule": "builtins.simple",
             "collection_size": 10000000,
             "ms_url": "http://localhost:8888",
             "collection_ttl": 1500000
          },
          "use_ssl": "",
          "unis_url": "http://localhost:8888",
          "probes": {
              "minimal_cpu_probe": {
                  "probe_module": "cpu"
              }
          }
        }
      }
    }

Whoa! Lots more stuff! A lot of this (anything under properties.configurations particularly) BLiPP adds automatically from its defaults and through some of its interactions with UNIS.

Other things, namely `ts`, `id`, and `selfRef` are added by UNIS itself when the configuration is POSTed to UNIS as a UNIS `service` element.

.. toctree::
   :maxdepth: 2

   blipp_in_depth.rst
   development_notes.rst
   getting_started.rst

