#!/usr/bin/python3
# use api keys to iterate over servers in each location
# and display identifiable information and data traffic details
# https://blog.sleeplessbeastie.eu/2018/04/30/how-to-display-leaseweb-data-traffic-using-api-v2/

# import http.client
import http.client

# import json
import json

# import datetime
import datetime
import sys

# math
import math

def pretty_size(nbytes, base=1000, decimal_part=2):
  if base == 1000:
    metric = ("B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  elif base == 1024:
    metric = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
  else:
    return "%s %s" % (nbytes, "B")

  if nbytes == 0:
    return "%s %s" % ("0", "B")

  nunit = int(math.floor(math.log(nbytes, base)))
  nsize = round(nbytes/(math.pow(base, nunit)), decimal_part)
  return '%s %s' % (nsize, metric[nunit])

# current datetime
now = datetime.datetime.now()

# define api keys
api_keys={"NL":"8517f379-aa60-5c1e-53ef-55203cab8c81d", "DE":"c406d92f-3603-f477-6086-7e3a1953ba2dc", "US":"16986a34-4148-7141-142f-b9c998f8ca878", "SG": "a12da181-029e-7a5f-cf8e-c3c70ea717db1"}

for key in api_keys:
  try:
    # get servers in location
    https_connection = http.client.HTTPSConnection("api.leaseweb.com")
    https_headers = { 'x-lsw-auth': api_keys[key] }
    https_connection.request("GET", "/bareMetals/v2/servers", headers=https_headers)
    https_response = https_connection.getresponse()
    https_response_data = https_response.read()
    json_servers = json.loads(https_response_data.decode("utf-8"))
    if not 'servers' in json_servers:
      print('LeaseWeb', key, 'returned no data')
      continue
  except:
    # skip location if there is a problem
    continue

  print('LeaseWeb', key)
  for bareMetal in json_servers['servers']:
    try:
      # get server info
      https_connection.request('GET', '/bareMetals/v2/servers/' + bareMetal['id'], headers=https_headers)
      https_response = https_connection.getresponse()
      https_response_data = https_response.read()
      json_server = json.loads(https_response_data.decode("utf-8"))

      # get datatraffic for server
      https_connection.request('GET', '/bareMetals/v2/servers/' + bareMetal['id'] + '/metrics/datatraffic?from=' + str(now.year) + '-' + str(now.month).rjust(2,'0') + '-01T00:00:00Z' + '&to=' + str(now.year) + '-' + str(now.month).rjust(2,'0') + '-' + str(now.day) + 'T00:00:00Z&aggregation=SUM', headers=https_headers)
      https_response = https_connection.getresponse()
      https_response_data = https_response.read()
      json_datatraffic = json.loads(https_response_data.decode("utf-8"))
    except:
      # skip server if there is a problem
      continue

    try:
      # get IP addresses for server
      https_connection.request('GET', '/bareMetals/v2/servers/' + bareMetal['id'] + '/ips?networkType=public', headers=https_headers)
      https_response = https_connection.getresponse()
      https_response_data = https_response.read()
      json_ips= json.loads(https_response_data.decode("utf-8"))
      if not 'ips' in json_ips:
        # skip datapack
        continue
    except:
      continue

    # print results
    try:
      print(' *', bareMetal['contract']['internalReference'])
      print('   IP addresses: ', end='')
      for index, json_ip in enumerate(json_ips["ips"]):
        if index > 0: print(', ', end='')
        print(json_ip['ip'], end='')
      print()
      if (str(json_server['contract']['networkTraffic']['datatrafficUnit']) != 'None'):
        print('   Using network type', json_server['contract']['networkTraffic']['type'], 'traffic type', json_server['contract']['networkTraffic']['trafficType'], 'datatraffic limit', json_server['contract']['networkTraffic']['datatrafficLimit'], json_server['contract']['networkTraffic']['datatrafficUnit'], end='')
        print()
      print('   Interval from', json_datatraffic['_metadata']['from'], 'to', json_datatraffic['_metadata']['to'], end='\n')
      print('   Data traffic on public interface: ', end='\n')
      print('    ', pretty_size(json_datatraffic['metrics']['DOWN_PUBLIC']['values'][0]['value']), 'in', end=' ')
      print(pretty_size(json_datatraffic['metrics']['UP_PUBLIC']['values'][0]['value']), 'out', end=' ')
      print(pretty_size(int(json_datatraffic['metrics']['DOWN_PUBLIC']['values'][0]['value']) + int(json_datatraffic['metrics']['UP_PUBLIC']['values'][0]['value'])), 'total', end='')
      print()
    except:
      continue
  https_connection.close()

