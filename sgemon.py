#!/usr/bin/env python
from datetime import datetime
import time
import urllib2
import urllib
import httplib
import csv
import os
import json
import sys
from influxdb import InfluxDBClient

client = InfluxDBClient('localhost',8086,'','','solar')

sgDeviceId = "974894282"

def getSungrowData(start=time.strftime("%Y%m%d")):
    """
    Download Solar report for the day
    """
    response = urllib2.urlopen('http://www.solarinfobank.com/DataDownLoad/DownLoadRundata?deviceId='+sgDeviceId+'&yyyyMMDD='+start+'&type=csv')
    cr = csv.reader(response)
    return cr

now = datetime.now()
print now

influxDate = now.date().isoformat() + "T"
sOut = getSungrowData(now.strftime('%Y%m%d'))
print sOut
count = 0
for row in sOut:
    count += 1
    if count < 3:
        continue
    powerTime = datetime.strptime(row[0], '%H:%M:%S')
    powerTime = datetime.strftime(powerTime, '%H:%M')
    influxTime = datetime.strptime(row[0], '%H:%M:%S')
    influxDatetime = influxDate + influxTime.time().isoformat() + "Z-0800"
    powerGen = float(row[11])*1000
    energyGen = float(row[1])*1000
    invertTemp = row[3]
    voltage1 = float(row[4])
    voltage2 = float(row[6])
    vdc = (voltage1 + voltage2)/2
    print "InfluxTime: "+str(influxDatetime)+" Time: " + str(powerTime) + " W: " + str(powerGen) + " Wh: " + str(energyGen) + " temp: " + str(invertTemp) + " vdc: " + str(vdc)

    json_body = [
        {
            "measurement": "solar",
            "tags": {
                 "location": "rooftop solar"
            },
            "time": str(influxDatetime),
            "fields": {
                "powerTime": powerTime,
                "powerGen": powerGen,
                "energyGen": energyGen,
                "invertTemp": invertTemp,
                "voltage1": voltage1,
                "voltage2": voltage2,
                "vdc": vdc
            }
        }
    ]
    client.write_points(json_body)
