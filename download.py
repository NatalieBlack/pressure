#!/usr/bin/env python

import os
import requests
import json
import arrow, datetime, time
from tzlocal import get_localzone
from config import apikey, startsecond, startminute, starthour, startday, startmonth, startyear, endsecond, endminute, endhour, endday, endmonth, endyear, minlat, maxlat, minlon, maxlon

def make_call(s, f, data):
    params = {'api_key': apikey, 'start_time': s, 'end_time': f,
               'min_lat': minlat, 'max_lat': maxlat,
               'min_lon': minlon, 'max_lon': maxlon 
              }
    
    r = requests.get('https://pressurenet.io/live', params=params)

    print "Request made to " + r.url
    print arrow.get(str(s/1000)).format('MMMM-DD-YYYY:HH:mm:ss') + " to " + arrow.get(str(f/1000)).format('MMMM-DD-YYYY:HH:mm:ss')
    print "Status: {}".format(r.status_code)
    if r.status_code == 200:
        print "{} items downloaded".format(len(r.json()))

        if len(r.json()) > 0:
            data += r.json()

stime = arrow.get(datetime.datetime(startyear, startmonth, startday, starthour, startminute, startsecond, tzinfo=get_localzone()))
origstart = stime

ftime = arrow.get(datetime.datetime(endyear, endmonth, endday, endhour, endminute, endsecond, tzinfo=get_localzone()))

data = []

ftimestamp = ftime.timestamp * 1000

#don't ask for more than 1 day's data at a time
while (ftime - stime).days > 1:
    stimestamp = stime.timestamp * 1000
    ftimestamp = stime.replace(days=+1).timestamp * 1000

    make_call(stimestamp, ftimestamp, data)

    stime = arrow.get(ftimestamp / 1000).replace(seconds=+1)
    time.sleep(10)

stimestamp = stime.timestamp * 1000
ftimestamp = ftime.timestamp * 1000

make_call(stimestamp, ftimestamp, data)

fn = os.path.join('data', '{startdate}_{enddate}_{minlat}-{maxlat}_{minlon}-{maxlon}.json'.format(
        startdate = origstart.format('MMMM-DD-YYYY:HH:mm:ss'),
         enddate = ftime.format('MMMM-DD-YYYY:HH:mm:ss'),
         minlat = minlat, maxlat = maxlat, 
         minlon = minlon, maxlon = maxlon
        ))

print "Data saved to " + fn

with open(fn, 'w+') as outfile:
      json.dump(data, outfile)
      outfile.close()
