import time
import datetime
import urllib2
import urllib
import json
from StringIO import StringIO    
import sys
import httplib
import math
from influxdb import InfluxDBClient

client = InfluxDBClient('10.10.10.50',8086,'root','root','solar')

interval = 300

# Sungrow IDs
# Fiddle with the sungrow solarinfo web interface till you get them
sgUnitId = "8603"
sgDeviceId = "974894282"
sgUserId = "7544"
sgPlantId = "7811"
sgDelay = 300 # delay between calls to Sungrow website

# Sungrow Monitor Codes
# 103 Daily energy (kWh)
# 104 Total Energy (kWh)
# 106 Ambient temperature inside equipment (deg C)
# 107 Transformer temperature inside equipment (deg C) seems to be always -0.1
# 108 Heatsink temperature inside equipment (deg C) seems to be always -0.1
# 109 VDC1
# 110 IDC1
# 111 VDC2
# 112 IDC2
# 115 Total DC Power
# 116 Voltage A Phase (Grid Voltage)
# 119 Current A Phase
# 125 Total Active Power
# 128 AC frequency

def round_minutes(dt, direction, resolution):
	new_minute = (dt.minute // resolution + (1 if direction == 'up' else 0)) * resolution
	newDatetime = dt + datetime.timedelta(minutes=new_minute - dt.minute)
	return newDatetime

#newDatetime = round_minutes(datetime.datetime.now(), "down", 15)
#print "Hour:Minutes = "+str(newDatetime.hour)+":"+str(newDatetime.minute)

def getCurrentPower():
	url = 'http://www.solarinfobank.com/aapp/UnitDevices?uid='+sgUnitId+'&lan=en-us'
	response = urllib2.urlopen(url)
	urldata = response.read()
	dataset  = json.loads(urldata)

	s = dataset['units'][0]['devices'][0]['displayField']

	power = int(s.split(':')[1].strip()[:-1])
	return power

def getInverterTemps():
	start = time.strftime("%Y%m%d") + "00"
	end = time.strftime("%Y%m%d") + "23"
	url = 'http://www.solarinfobank.com//aapp/MonitorDayChart?dId='+sgDeviceId+'&startYYYYMMDDHH='+start+'&endYYYYMMDDHH='+end+'&chartType=line&monitorCode=106&lan=en-us'
	response = urllib2.urlopen(url)
	urldata = response.read()
	dataset  = json.loads(urldata)

	if(dataset['isHasData']):
		return dataset
	else:
		return False

def getGridVoltage():
	start = time.strftime("%Y%m%d") + "00"
	end = time.strftime("%Y%m%d") + "23"
	url = 'http://www.solarinfobank.com//aapp/MonitorDayChart?dId='+sgDeviceId+'&startYYYYMMDDHH='+start+'&endYYYYMMDDHH='+end+'&chartType=line&monitorCode=116&lan=en-us'
	response = urllib2.urlopen(url)
	urldata = response.read()
	dataset  = json.loads(urldata)

	if(dataset['isHasData']):
		return dataset
	else:
		return False

def getData(dataset):
	roundedDatetime = round_minutes(datetime.datetime.now(), "down", 15)
	t = str(roundedDatetime.hour).zfill(2)+":"+str(roundedDatetime.minute).zfill(2)
	print t

	categories, data = dataset['categories'], dataset['series'][0]['data']
	index = categories.index(t)
	datapoint = data[index - 1]
	return datapoint

try:
	power = getCurrentPower()
	#print "Current Power: "+str(power)+" W"
	#temp = getData(getInverterTemps())

	gridVoltage = getData(getGridVoltage())
	#print gridVoltage

	json_body = [
		{
			"measurement": "solar",
			"tags": {
				"location": "rooftop solar"
			},
			"fields": {
				"power": power,
				"grid voltage": gridVoltage
			}
		}
	]
	client.write_points(json_body)

except urllib2.URLError as e:
	print "One of the web servers is dead, sleeping for a bit"
	print e.args

except StandardError as e:
	print "something went bad... lets take a nap"
	print e.args


