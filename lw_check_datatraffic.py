#!/usr/bin/python3
# use api keys to iterate over servers in each location
# and display identifiable information and data traffic details
# https://blog.sleeplessbeastie.eu/2017/11/20/how-to-display-leaseweb-data-traffic-using-command-line/

# import http.client
import http.client

# import json
import json

# import datetime
import datetime


# current datetime
now = datetime.datetime.now()

# define api keys
api_keys={"NL":"8517f379-aa60-5c1e-53ef-55203cab8c81d", "DE":"c406d92f-3603-f477-6086-7e3a1953ba2dc", "US":"16986a34-4148-7141-142f-b9c998f8ca878", "SG": "a12da181-029e-7a5f-cf8e-c3c70ea717db1"}

for key in api_keys:
  try:
    # get servers in location
    https_connection = http.client.HTTPSConnection("api.leaseweb.com")
    https_headers = { 'x-lsw-auth': api_keys[key] }
    https_connection.request("GET", "/v1/bareMetals", headers=https_headers)
    https_response = https_connection.getresponse()
    https_response_data = https_response.read()
    json_servers = json.loads(https_response_data.decode("utf-8"))
    if not 'bareMetals' in json_servers:
      print('LeaseWeb', key, 'returned no data')
      continue
  except:
    # skip location if there is a problem
    continue

  print('LeaseWeb', key)
  for bareMetal in json_servers['bareMetals']:
    try:
      # get datatraffic for server
      # notice that you need to count datatraffic from the last day of previous month to the current day (to get the same results as found in customer portal)
      https_connection.request('GET', '/v1/bareMetals/' + bareMetal['bareMetal']['bareMetalId'] + '/networkUsage/datatraffic?dateFrom=00-' + str(now.month) + '-' + str(now.year) + '&dateTo=' + str(now.day) + '-' + str(now.month) + '-' + str(now.year), headers=https_headers)
      https_response = https_connection.getresponse()
      https_response_data = https_response.read()
      json_datatraffic = json.loads(https_response_data.decode("utf-8"))
    except:
      # skip server if there is a problem
      continue

    try:
      # get IP addresses for server
      https_connection.request('GET', '/v1/bareMetals/' + bareMetal['bareMetal']['bareMetalId'] + '/ips', headers=https_headers)
      https_response = https_connection.getresponse()
      https_response_data = https_response.read()
      json_ips= json.loads(https_response_data.decode("utf-8"))
      if not 'ips' in json_ips:
        # skip datapack
        continue
    except:
      continue

    # print results
    print(' *', bareMetal['bareMetal']['serverName'])
    print('   IP addresses: ', end='')
    for index, json_ip in enumerate(json_ips["ips"]):
      if index > 0: print(', ', end='')
      print(json_ip['ip']['ip'], end='')
    print()
    print('   Interval from', json_datatraffic['dataTraffic']['interval']['from'], 'to', json_datatraffic['dataTraffic']['interval']['to'], end='')
    if json_datatraffic['dataTraffic']['monthlyThreshold'] != "0 GB":
      print(' with monthly threshold ', json_datatraffic['dataTraffic']['monthlyThreshold'], end='')
    if json_datatraffic['dataTraffic']['overusage'] != "0 B":
      print(' [', json_datatraffic['dataTraffic']['overusage'], '] ', end='')
    print()
    print('   Used ', json_datatraffic['dataTraffic']['measurement']['total'])
    interface_index=1
    for json_interface_datatraffic in json_datatraffic['dataTraffic']['measurement']:
      try:
        print('    - Interface ', str(interface_index), ': total', json_datatraffic['dataTraffic']['measurement'][json_interface_datatraffic]['total'], end=' = ')
        print(json_datatraffic['dataTraffic']['measurement'][json_interface_datatraffic]['in'], 'in', end=' + ')
        print(json_datatraffic['dataTraffic']['measurement'][json_interface_datatraffic]['out'], 'out')
        if "node" in json_interface_datatraffic:
          interface_index=interface_index+1
      except:
        continue
  https_connection.close()

