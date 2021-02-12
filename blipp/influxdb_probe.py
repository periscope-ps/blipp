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
from requests.exceptions import ConnectionError
import subprocess
import json
import shlex
from . import settings
import datetime
import calendar
from .unis_client import UNISInstance

logger = settings.get_logger('influxdb_probe')

EVENT_MAPS={
    "disk_read.disk_octets": "ps:tools:blipp:influxdb:ceph:diskread:disk_octets",
    "disk_write.disk_octets": "ps:tools:blipp:influxdb:ceph:diskwrite:disk_octets",
    "disk_io_time.disk_io_time": "ps:tools:blipp:influxdb:ceph:diskio:disk_io_time",
    "ethstat_value.rx_bytes": "ps:tools:blipp:influxdb:ceph:ethstat:rx_bytes",
    "ethstat_value.tx_bytes": "ps:tools:blipp:influxdb:ceph:ethstat:tx_bytes"
}

EVENT_COLUMNS={
    "disk_read": "type",
    "disk_write": "type",
    "disk_io_time": "type",
    "ethstat_value": "type_instance"
}

ETHTABLE = 'ethstat_value'

class Probe:

    def __init__(self, service, measurement):
        self.service = service
        self.measurement = measurement
        self.config = measurement["configuration"]
        self.unis = UNISInstance(service)
        
        self.command = self._substitute_command(str(self.config.get("command")), self.config)
        
        # TODO: get the latest ts and store it and use it as query bound next run.
        query_url = 'http://localhost:8086/query?pretty=true&u=reader&p=Qul@r*Buve5'
        query_db = "db=collectd"
        query_table = self.config.get("table")
        query_every = self.config.get("schedule_params").get("every")
        query = "q=select * from {0} where time > now() - {1}s;".format(query_table, query_every)
        self.command = ['curl', '-GET', query_url,
                        '--data-urlencode', query_db,
                        '--data-urlencode', query]

    def get_data(self):
        proc = subprocess.Popen(self.command,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        output = proc.communicate()

        if not output[0]:
            raise CmdError(output[1])
        try:
            data = self._extract_data(output[0])
        except ValueError as e:
            #logger.exc("get_data", e)
            return {}
        # sample data [{'wsu.stor1-href': {ts: <ts>, et: [instance, type, type_instance, value]}},
        #              {'um.stor2-href': {ts: <ts>, et: [instance, type, type_instance, value]}}]
        return data

    def _extract_data(self, stdout):
        def normalize(values, time_index, host_index, subject_index, event_index, table_name):
            '''
            carve the host and turn it into the subject of the data        
            change name 'time' to 'ts' and remove it from the data
            '''
            if '.'.join([table_name, values[event_index]]) not in EVENT_MAPS:
                # not event type that we are interested
                return {}
            
            host_name = values[host_index]
            try:
                host_obj = self.unis.get("/nodes?name=" + host_name)
            except ConnectionError:
                host_obj = None
            
            if not host_obj:
                # host not registered in this domain OR ConnectionError
                return {}
            
            if table_name == ETHTABLE:
                if 'ports' in host_obj[0]:
                    ports = host_obj[0]['ports']
                    subject = None
                    
                    for port in ports:
                        port_id = port['href'].split('/')[-1]
                        try:
                            port_obj = self.unis.get("/ports/" + port_id)
                        except ConnectionError:
                            port_obj = None
                        
                        if port_obj and port_obj['name'] == values[subject_index]:
                            subject = port_obj['selfRef']
                            break
                    
                    if not subject:
                        # none of the eth matches
                        return {}
                    
                else:
                    # this host has no eth uploaded
                    return {}
            else :
                # other tables (disk stat) will aggregate all instances
                subject = host_obj[0]['selfRef']
            
            event_type = EVENT_MAPS['.'.join([table_name, values[event_index]])]
            dt = datetime.datetime.strptime(values[time_index], "%Y-%m-%dT%H:%M:%S.%fZ")
            time = calendar.timegm(dt.timetuple()) + (dt.microsecond / 1000000.0)
            
            values = values[-1]
            
            return {subject: {'ts': time, event_type: values}}
        
        
        json_output = json.loads(stdout)
        if not json_output['results'][0]:
            return []
        
        table_name = json_output['results'][0]['series'][0]['name']
        event_column = EVENT_COLUMNS[table_name]
        
        i = json_output['results'][0]['series'][0]['columns'].index('time')
        j = json_output['results'][0]['series'][0]['columns'].index('host')
        k = json_output['results'][0]['series'][0]['columns'].index('instance')
        e = json_output['results'][0]['series'][0]['columns'].index(event_column)
        ret = [normalize(x, i, j, k, e, table_name) for x in json_output['results'][0]['series'][0]['values']]
        ret = [x for x in ret if x]
        
        if table_name == ETHTABLE:
            pass
        else:
            # aggregate all drive on one host
            # ts is chosen randomly from the same subject-et items
            tmp = dict()
            for data in ret:
                et = [x for x in iter(data.values()).next().keys() if x != 'ts'][0]
                if (next(iter(data.keys())), et) in tmp:
                    tmp[(next(iter(data.keys())), et)][et] += iter(data.values()).next()[et]
                else:
                    tmp[(next(iter(data.keys())), et)] = next(iter(data.values()))
            ret = []
            for k, v in tmp.items():
                ret.append({k[0]: v})
        
        return ret

    def _substitute_command(self, command, config):
        ''' command in form "ping $ADDRESS"
        config should have substitutions like "address": "example.com"
        Note; now more complex
        '''
        command = shlex.split(command)
        ret = []
        for item in command:
            if item[0] == '$':
                if item[1:] in config:
                    val = config[item[1:]]
                    if isinstance(val, bool):
                        if val:
                            ret.append(item[1:])
                    elif item[1]=="-":
                        ret.append(item[1:])
                        ret.append(str(val))
                    else:
                        ret.append(str(val))
            elif item:
                ret.append(item)
        logger.info('substitute_command', cmd=ret, name=self.config['name'])
        return ret

class CmdError(Exception):
    def __init__(self, stderr):
        self.stderr = stderr

    def __str__(self):
        return "Exception in command line probe: " + self.stderr
