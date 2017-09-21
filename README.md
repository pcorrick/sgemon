# sgemon
Python script to scrape Sungrow inverter data from www.solarinfobank.com and write to InfluxDB.

Sungrow sell a WiFi dongle that plugs into the serial port of the inverter. This posts data to a www.solarinfobank.com account, in 15min increments.

# Find your UnitID
Login to your www.solarinfobank.com account. View the page sources of the Plant Overview page. Search for 'udevicechart' and find the UnitID of your system.
E.g. UnitID = xxxx in the example below:

    <a rel="unitmenu" onclick="loadContent('content_ajax','/devicechart/udevicechart/xxxx','ajax','GET')


# Find your DeviceID
Plug your UnitID in the following URL:
http://www.solarinfobank.com/aapp/UnitDevices?uid=xxxx&lan=en-us

The array returned contains deviceID details.
