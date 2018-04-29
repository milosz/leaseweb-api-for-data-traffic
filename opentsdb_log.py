#!/usr/bin/python3
# Log LeaseWeb data traffic to OpenTSDB
# https://blog.sleeplessebastie.eu/2018/05/18/how-to-store-leaseweb-data-traffic-in-opentsdb-time-series-database/

# http
import http.client

# json
import json

# opentsdb
import potsdb

# date
import datetime

# define api keys
api_keys={"NL":"8517f379-aa60-5c1e-53ef-55203cab8c81d", "DE":"c406d92f-3603-f477-6086-7e3a1953ba2dc", "US":"16986a34-4148-7141-142f-b9c998f8ca878", "SG": "a12da181-029e-7a5f-cf8e-c3c70ea717db1"}

# opentsdb server/port
opentsdb_server="192.0.2.100"
opentsdb_port=4242
opentsdb_metric_name="leaseweb.datatraffic"
opentsdb_metric_tag="hostname"

# current datetime
current_datetime = datetime.datetime.utcnow()

for key in api_keys:
  try:
    # get server list
    https_connection = http.client.HTTPSConnection("api.leaseweb.com")
    https_headers = { 'x-lsw-auth': api_keys[key]}
    https_connection.request("GET", "/bareMetals/v2/servers", headers=https_headers)
    https_response = https_connection.getresponse()

    https_data = https_response.read()
    json_servers = json.loads(https_data.decode("utf-8"))

    # connect to opentsdb
    metrics = potsdb.Client(opentsdb_server, port=opentsdb_port,check_host=False)
  except:
    continue

  if not 'servers' in json_servers:
    print('LeaseWeb', key, 'returned no data')
    continue

  # for each server
  for bareMetal in json_servers['servers']:
    try:
      # get id and name
      bareMetalId = bareMetal['id']
      serverName  = bareMetal['contract']['internalReference']

      # get datatraffic
      https_connection.request('GET', '/bareMetals/v2/servers/' + bareMetalId + '/metrics/datatraffic?from=' + str(current_datetime.year) + '-' + str(current_datetime.month).rjust(2,'0') + '-' + '01' + 'T00:00:00Z' + '&to=' + str(current_datetime.year) + '-' + str(current_datetime.month).rjust(2,'0') + '-' + str(current_datetime.day) + 'T' + str(current_datetime.hour).rjust(2,'0')+':00:00Z&aggregation=SUM', headers=https_headers)
      https_response = https_connection.getresponse()
      https_data = https_response.read()

      # load json
      json_datatraffic = json.loads(https_data.decode("utf-8"))

      # calculate total datatrraffic
      datatraffic=int(json_datatraffic['metrics']['DOWN_PUBLIC']['values'][0]['value']) + int(json_datatraffic['metrics']['UP_PUBLIC']['values'][0]['value'])

      # push to opentsdb
      metrics.log(opentsdb_metric_name,datatraffic, **{opentsdb_metric_tag: serverName})
    except:
      continue

  # on exit
  metrics.wait()
  https_connection.close()

