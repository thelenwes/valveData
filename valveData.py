# -*- coding: utf-8 -*-
"""
valveData.py
Library to extract data from valve using a REST interface.  Optionally, data
can be detected for gaps, resampled and put into a obspy Stream structure.  REquires
a parameter file called 'config.json' in the same directory as script.  Contents
should look something like this:
{
  "host": "hvo-rest.wr.usgs.gov"
}
See requests documentation for more details.
--------------------------------------------------------------------
RSAM DATA Example:
import valveData
# Gets last 12 hours of RSAM data
date, datenum, data = valveData.getRsamLast('NPT$HWZ$HV, '-12h') 
# Detects gaps greater than 120 seconds
gapIndex = valveData.detectGap(date, 120)  
# Splits data based on gaps and resamples
slicedDates, slicedData = valveData.splitData(date, data, gapIndex, delta=60, resample=True)  
# Converts to obspy object
streamDataRSAM = valveData.data2obspy(slicedDates, slicedData, channel)  

Created on Mon Feb 16 07:50:24 2015

@author: wthelen
"""

import json
import requests

config = {}
try:
    with open('config.json') as cfg:
        config = json.load(cfg)
except:
    with open('/Users/westonthelen/python/config.json') as cfg:
        config = json.load(cfg)
            
    
def dump(response):
    '''
    Testing function for seeing what is coming back in response.
    '''
    print json.dumps(json.loads(response.text), indent=2)

def rsaminfo():
    '''
    Prints to the screen information about the rsam dataset in the REST interface
    '''
    resp = requests.get('http://%s/api/rsam' % (config['host']))
    print resp.text
    
def triggersinfo():
    '''
    Prints to the screen information about the triggers dataset in the REST interface
    '''
    resp = requests.get('http://%s/api/triggers' % (config['host']))
    print resp.text
    
def tiltinfo():
    '''
    Prints to the screen information about the tilt dataset in the REST interface
    '''
    resp = requests.get('http://%s/api/tilt' % (config['host']))
    print resp.text
    
def flyspecinfo():
    '''
    Prints to the screen information about the flyspec dataset in the REST interface
    '''
    resp = requests.get('http://%s/api/flyspec' % (config['host']))
    print resp.text
    
def straininfo():
    '''
    Prints to the screen information about the strain dataset in the REST interface
    '''
    resp = requests.get('http://%s/api/strain' % (config['host']))
    print resp.text
    
def gpsinfo():
    '''
    Prints to the screen information about the gps dataset in the REST interface
    '''
    resp = requests.get('http://%s/api/gps' % (config['host']))
    print resp.text
    
gmt_j2koffset = 946764000
hst_j2koffset = 946728000

def j2k_to_date(j2k, hst=False):
    """
    Return the date for the passed in j2k value.
    j2k -- J2K value to parse
    hst -- Is the data requested in HST? If not, return GMT
    """
    if hst:
        return datetime.fromtimestamp(j2k + hst_j2koffset)
    else:
        return datetime.fromtimestamp(j2k + gmt_j2koffset)
        
def getRsamLast(channel, starttime, timezone='utc', downsample='none', dsint=10):
    '''
    Gets RSAM data from REST interface for the last X time increment.
    
    Parameters
    ----------
    channel: string
        channel name, separated by $, cause valve is crazy like that.  see rsaminfo() for full listing
    starttime: string
        starttime for plot relative to current time.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    downsample: string
        method for downsampling.  Can be 'none', 'mean' or 'decimate'.  
    dsint: integer
        factor to downsample by.  for example, as dsint of 10 on a 60 sec/sample
        data will result in 600 sec/sample data (1 min to 10 min)
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''
    payload = {'channel': channel, 'starttime': starttime, 'timezone': timezone, 'downsample': downsample, 'dsint': 10}
    req = requests.get('http://%s/api/rsam' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, 'rsam')
    return date, datenum, data
    
def getTriggersLast(channel, starttime, timezone='utc'):
    '''
    Gets Trigger data from REST interface for the last X time increment.
    
    Parameters
    ----------
    channel: string
        channel name, separated by $, cause valve is crazy like that.  see rsaminfo() for full listing
    starttime: string
        starttime for plot relative to current time.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''
    payload = {'channel': channel, 'starttime': starttime, 'timezone': timezone}
    req = requests.get('http://%s/api/triggers' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, 'triggers')
    return date, datenum, data
    
def getTiltLast(channel, starttime, timezone='utc', downsample='none', dsint=10, series='radial', rank=1):
    '''
    Gets Tilt data from REST interface for the last X time increment.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see tiltinfo() for full listing
    series: string 
        Can be one of the following:
            'radial'
            'tangential'
            'east'
            'north'
            'rainfall'
    starttime: string
        starttime for plot relative to current time.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    downsample: string
        method for downsampling.  Can be 'none', 'mean' or 'decimate'.  
    dsint: integer
        factor to downsample by.  for example, as dsint of 10 on a 60 sec/sample
        data will result in 600 sec/sample data (1 min to 10 min)
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''
    payload = {'channel': channel, 'starttime': starttime, 'timezone': timezone, 'downsample': downsample, 'dsint': 10, 'series': series, 'rank': rank}
    req = requests.get('http://%s/api/tilt' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getFlySpecLast(channel, starttime, timezone='utc', downsample='none', dsint=10, series='bstflux', rank=2):
    '''
    Gets Flypec data from REST interface for the last X time increment.
    
    Parameters
    ----------
    channel: string
        channel name, for example, FLYA.  see tiltinfo() for full listing
    series: string 
        Can be one of the following:
            'bstflux'
            'bstfluxmean'
            'bstfluxmeanstdec'
            'ps': plume speed
            'pd': plume direction
    starttime: string
        starttime for plot relative to current time.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    downsample: string
        method for downsampling.  Can be 'none', 'mean' or 'decimate'.  
    dsint: integer
        factor to downsample by.  for example, as dsint of 10 on a 60 sec/sample
        data will result in 600 sec/sample data (1 min to 10 min)
    rank: int
        Rank of data
          0: Best Possible
          1: Raw Data
          2: Processed
          3: Filtered
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''
    payload = {'channel': channel, 'starttime': starttime, 'timezone': timezone, 'downsample': downsample, 'dsint': 10, 'series': series, 'rank': rank}
    req = requests.get('http://%s/api/flyspec' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getStrainLast(channel, starttime, timezone='utc', debias='none', series='dt01'):
    '''
    Gets Strain data from REST interface for the last X time increment.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see tiltinfo() for full listing
    series: string 
        Can be one of the following:
            'dt01'
            'dt02'
            'barometer'
    starttime: string
        starttime for plot relative to current time.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    debias: string
        Remove mean?  Can be 'none' or 'mean'.  Defaults to 'none'.  
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''    
    payload = {'channel': channel, 'starttime': starttime, 'timezone': timezone, 'debias': debias, 'series': series}
    req = requests.get('http://%s/api/strain' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getGPSLengthLast(channel, baseline, starttime, timezone='utc', dsint=10):
    '''
    Gets GPS length data from REST interface for the last X time increment.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see gpsinfo() for full listing
    baseline: string
    	channel name, for example, MLSP to calculate the length from.
    starttime: string
        starttime for plot relative to current time.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure  
    dsint: integer
        factor to downsample by.  for example, as dsint of 10 on a 60 sec/sample
        data will result in 600 sec/sample data (1 min to 10 min)
     
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''    
    
    series = 'length'
    payload = {'channel': channel, 'baseline': baseline, 'starttime': starttime, 'timezone': timezone, 'dsint': 10, 'series': series}
    req = requests.get('http://%s/api/gps' % (config['host']), params=payload)    
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getRTNetLast(channel, starttime, timezone='utc', series='up', rank=4):
    '''
    Gets GPS RTNet data from REST interface for the last X time interval.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see gpsinfo() for full listing
    starttime: string
        typically in the form of: yyyy[MMdd[hhmm]] 
        Can also be relative to endtime.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure  
    series: string
        data that is to be requested.  one series at a time (ex. "north" or "up", not "east,up")
    rank: int
    	the rank of data to grab (see valve, default is 4)
     
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''    
    
    payload = {'channel': channel, 'starttime': starttime, 'timezone': timezone, 'rank': rank, 'series': series}
    req = requests.get('http://%s/api/rtnet' % (config['host']), params=payload)    
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getTremorSpan(channel, starttime, endtime, timezone='utc'):
    '''
    Gets Trigger data from REST interface from starttime to endtime.
    
    Parameters
    ----------
    channel: string
        channel name, separated by $, cause valve is crazy like that.  see rsaminfo() for full listing
    starttime: string
        typically in the form of: yyyy[MMdd[hhmm]] 
        Can also be relative to endtime.  Options are:
            #i for minutes (30i would be last 30 minutes)
            #h for hours (1h frould be last 1 hour)
            #d for days
            #w for weeks
            #m for months
            #y for years
            BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
            YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''
    payload = {'channel': channel, 'starttime': starttime, 'endtime': endtime, 'timezone': timezone}
    req = requests.get('http://%s/api/triggers' % (config['host']), params=payload)    
    date, datenum, data = parseJson(req, channel, 'triggers')
    return date, datenum, data
    
def getTiltSpan(channel, starttime, endtime, timezone='utc', downsample='none', dsint=10, series='radial', rank=1):
    '''
    Gets Tilt data from REST interface for the given time interval.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see tiltinfo() for full listing
    series: string 
        Can be one of the following:
            'radial'
            'tangential'
            'east'
            'north'
            'rainfall'
    starttime: string
    	typically in the form of: yyyy[MMdd[hhmm]] 
        Can also be relative to endtime.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    downsample: string
        method for downsampling.  Can be 'none', 'mean' or 'decimate'.  
    dsint: integer
        factor to downsample by.  for example, as dsint of 10 on a 60 sec/sample
        data will result in 600 sec/sample data (1 min to 10 min)
    rank: integer
    	which rank is used (1 is decimated data, 2 is raw data).  defaults to 2.
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''    
    
    payload = {'channel': channel, 'starttime': starttime, 'endtime': endtime, 'timezone': timezone, 'downsample': downsample, 'dsint': dsint, 'series': series, 'rank': rank}
    req = requests.get('http://%s/api/tilt' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getStrainSpan(channel, starttime, endtime, timezone='utc', debias='none', series='dt01'):
    '''
    Gets Strain data from REST interface for given time interval.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see tiltinfo() for full listing
    series: string 
        Can be one of the following:
            'dt01'
            'dt02'
            'barometer'
    starttime: string
    	typically in the form of: yyyy[MMdd[hhmm]] 
        Can also be relative to endtime.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    debias: string
        Remove mean?  Can be 'none' or 'mean'.  Defaults to 'none'.  
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''    
    
    payload = {'channel': channel, 'starttime': starttime, 'endtime': endtime, 'timezone': timezone, 'debias': debias, 'series': series}
    req = requests.get('http://%s/api/strain' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getFlySpecSpan(channel, starttime, endtime, timezone='utc', downsample='none', dsint=10, series='bstflux', rank=2):
    '''
    Gets FlySpec data from REST interface for the given time interval.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see tiltinfo() for full listing
    series: string 
        Can be one of the following:
            'bstflux'
            'bstfluxmean'
            'bstfluxmeanstdec'
            'ps': plume speed
            'pd': plume direction
    starttime: string
        typically in the form of: yyyy[MMdd[hhmm]] 
        Can also be relative to endtime.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    downsample: string
        method for downsampling.  Can be 'none', 'mean' or 'decimate'.  
    dsint: integer
        factor to downsample by.  for example, as dsint of 10 on a 60 sec/sample
        data will result in 600 sec/sample data (1 min to 10 min)
    rank: int
        Rank of data
          0: Best Possible
          1: Raw Data
          2: Processed
          3: Filtered     
     
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''    
    
    payload = {'channel': channel, 'starttime': starttime, 'endtime': endtime, 'timezone': timezone, 'downsample': downsample, 'dsint': 10, 'series': series, 'rank': rank}
    req = requests.get('http://%s/api/flyspec' % (config['host']), params=payload)    
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getGPSLengthSpan(channel, baseline, starttime, endtime, timezone='utc', dsint=10):
    '''
    Gets GPS length data from REST interface for the given start time and stop time.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see gpsinfo() for full listing
    baseline: string
    	channel name, for example, MLSP to calculate the length from.
    starttime: string
        typically in the form of: yyyy[MMdd[hhmm]] 
        Can also be relative to endtime.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure  
    dsint: integer
        factor to downsample by.  for example, as dsint of 10 on a 60 sec/sample
        data will result in 600 sec/sample data (1 min to 10 min)
     
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''    
    
    series = 'length'
    payload = {'channel': channel, 'baseline': baseline, 'starttime': starttime, 'endtime': endtime, 'timezone': timezone, 'dsint': 10, 'series': series}
    req = requests.get('http://%s/api/gps' % (config['host']), params=payload)    
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data
    
def getRTNetSpan(channel, starttime, endtime, timezone='utc', series='up', rank=4):
    '''
    Gets GPS RTNet data from REST interface for the given start time and stop time.
    
    Parameters
    ----------
    channel: string
        channel name, for example, UWE.  see gpsinfo() for full listing
    starttime: string
        typically in the form of: yyyy[MMdd[hhmm]] 
        Can also be relative to endtime.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure  
    series: string
        data that is to be requested.  one series at a time (ex. "north" or "up", not "east,up")
    rank: int
    	the rank of data to grab (see valve, default is 4)
     
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''    
    
    payload = {'channel': channel, 'starttime': starttime, 'endtime': endtime, 'timezone': timezone, 'rank': rank, 'series': series}
    req = requests.get('http://%s/api/rtnet' % (config['host']), params=payload)    
    date, datenum, data = parseJson(req, channel, series)
    return date, datenum, data

def getRsamSpan(channel, starttime, endtime, timezone='utc', downsample='none', dsint=10):
    '''
    Gets RSAM data from REST interface for a given start and stop time.
    
    Parameters
    ----------
    channel: string
        channel name, separated by $, cause valve is crazy like that.  see rsaminfo() for full listing
    starttime: string
        starttime for plot relative to current time.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    downsample: string
        method for downsampling.  Can be 'none', 'mean' or 'decimate'.  
    dsint: integer
        factor to downsample by.  for example, as dsint of 10 on a 60 sec/sample
        data will result in 600 sec/sample data (1 min to 10 min)
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''
    payload = {'channel': channel, 'starttime': starttime, 'endtime': endtime, 'timezone': timezone, 'downsample': downsample, 'dsint': 10}
    req = requests.get('http://%s/api/rsam' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, 'rsam')
    return date, datenum, data

def getTriggersSpan(channel, starttime, endtime, timezone='utc'):
    '''
    Gets trigger data from REST interface for a given start and stop time.
    
    Parameters
    ----------
    channel: string
        channel name, separated by $, cause valve is crazy like that.  see rsaminfo() for full listing
    starttime: string
        starttime for plot relative to current time.  Options are:
        #i for minutes (30i would be last 30 minutes)
        #h for hours (1h frould be last 1 hour)
        #d for days
        #w for weeks
        #m for months
        #y for years
        BE CAREFUL, REQUESTING TOO MUCH DATA WITHOUT DOWNSAMPLING MAY BE BAD FOR
        YOUR HEALTH.
    endtime: string
        typically in the form of: yyyy[MMdd[hhmm]]
    timezone: string
        timezone for the data.  default is 'utc'. 'hst' is also accepted, as
        should other timezones, but I don't know for sure
    
        
    Outputs
    ---------
    date: list
        List of UTCDateTime objects corresponding to data list
    datenum: list
        List of matplotlib datenums
    data: list
        List of data
        
    '''
    payload = {'channel': channel, 'starttime': starttime, 'endtime': endtime, 'timezone': timezone}
    req = requests.get('http://%s/api/triggers' % (config['host']), params=payload)
    date, datenum, data = parseJson(req, channel, 'triggers')
    return date, datenum, data


def parseJson(toParse, channel, series):
    '''
    Parses JSON embedded within requests structure.
    
    Parameters
    ----------
    toParse: requests object
        
    channel: string
        string of SCNL or something similar to identify the object
    series: string
        label of the data in the json object
        'rsam' for rsam data
        'radial', 'tangential', 'east', 'north', 'rainfall' for tilt data
        'bstflux', 'bstfluxmean', 'bstfluxmeanstdev', 'ps' or 'pd' for flyspec data
        
    Outputs
    ---------
    date: list
        Times of individual samples in UTCDateTime
    datenum: list
        Times of individual samples in matplotlib datenum format
    data: list
        Data
        
    '''
    from obspy import UTCDateTime
    import matplotlib.dates as dates
    date = []
    datenum = []
    data = []
    jj = toParse.json()
    for samp in jj['records'][channel]:
        d = samp['date']
        dd = UTCDateTime(d)
        date.append(dd)
#        j2k_to_date(date, timezone).strftime('%Y-%m-%d %H:%M:%S.%f')
        datenum.append(dates.date2num(dd.datetime))
        data.append(samp[series])
    return date, datenum, data

def detectGap(date, gapThres):
    """
    Detects gap in a date vector based on the user defined threshold.
    
    Parameters
    ----------
    date: list
        Dates in UTCDateTime format to detect gaps within.
    gapThres: float
        Threshold in seconds over which to detect a gap.
    
    Outputs
    ---------
    gapIndex: list
        Indicies of gaps
    """
    from numpy import diff, where, array
    datediff = array(diff(date))
    gapIndex = where(datediff>gapThres)
    # Print gap information to screen (or somewhere)
    print '%d gaps found of greater than %s seconds' % (len(gapIndex[0]),gapThres)
    for i in gapIndex[0]:
        gapLength = date[i+1]-date[i]
        print 'Gap: %0.4f seconds at %s' % (gapLength, date[i].strftime('%Y-%m-%d_%H:%M:%S'))
    return gapIndex[0]
    
def splitData(date,data,gapIndex,delta=60,resample=True):
    """
    Splits date and data based on gapIndex.  After data is split, it is
    resampled to create an even time series.
    
    Parameters
    ----------
    date: list
        Dates in UTCDateTime format to detect gaps within.
    data: list
        Floats of data corresponding to the date.
    gapIndex: float
        Threshold in seconds over which to detect a gap.
    delta: float
        Number of seconds per sample
    resample: boolean
        If true, resample data to delta seconds per sample
    
    Outputs
    ---------
    slicedDates: list
        list of lists of continuous dates correcponding to data (no gaps)
    slicedData: list
        list of lists of continuous data correcponding to dates (no gaps)
    """
    slicedData = []   # Stores a list of data without gaps
    slicedDates = []  # Stores a list of dates without gaps
    import matplotlib.dates as md
    from obspy import UTCDateTime
    from datetime import timedelta
    from numpy import interp

    if len(data) == 0:
        return slicedDates, slicedData
    
    # Step through indices, assigning beginning and ending indexes, 
    # and converting to time series
    if resample == True:
        numdelta = timedelta(seconds=delta)
        print 'Resampling data to even spacing of %d seconds' % delta
    for ind in range(len(gapIndex)):
        if ind == 0:
            startSamp = 0
            endSamp = gapIndex[ind]+1
        else:
            startSamp = gapIndex[ind-1]+1
            endSamp = gapIndex[ind]+1
        if endSamp-startSamp <= 1:   # If only consists of one datapoint, don't save it
            continue
        # Now resample (if necessary)
        if resample == True:
            dnum = md.date2num(date[startSamp:endSamp])
            dnumnew = md.drange(date[startSamp],date[endSamp-1], numdelta)
            newdata = interp(dnumnew, dnum, data[startSamp:endSamp])
            dvec = []
            for d in dnumnew:
                dvec.append(UTCDateTime(md.num2date(d)))
            slicedData.append(newdata)
            slicedDates.append(dvec)
        else:
            #print 'Start Samp: %d' % startSamp
            #print 'Start Date: %s' % date[startSamp]
            #print 'End Samp: %d' % endSamp
            #print 'End Date: %s' % date[endSamp]
            #print 'nSamples: %d' % endSamp-startSamp
            slicedData.append(data[startSamp:endSamp])
            slicedDates.append(date[startSamp:endSamp])
    if len(gapIndex) > 0:   # This loop gets entered if there is a gap
        # Add last window of data
        startSamp = gapIndex[-1]+1
        datalen = len(data)-gapIndex[-1]
        if datalen > 1:     # Check to make sure that last data segment is more than one sample
            # Resample last window (if necessary)
            if resample == True:
                dnum = md.date2num(date[startSamp:-1])
                dnumnew = md.drange(date[startSamp],date[-1], numdelta)
                newdata = interp(dnumnew, dnum, data[startSamp:-1])
                dvec = []
                for d in dnumnew:
                    dvec.append(UTCDateTime(md.num2date(d)))
                slicedData.append(newdata)
                slicedDates.append(dvec)
            else:
                slicedData.append(data[startSamp:-1])
                slicedDates.append(date[startSamp:-1])
    else:   # This is the loop for data with no gaps that needs to be resampled
        if resample == True:
            dnum = md.date2num(date)
            dnumnew = md.drange(date[0],date[-1], numdelta)
            newdata = interp(dnumnew, dnum, data)
            dvec = []
            for d in dnumnew:
                dvec.append(UTCDateTime(md.num2date(d)))
            slicedData.append(newdata)
            slicedDates.append(dvec)
        else:
            slicedData.append(data)
            slicedDates.append(date)
        
    
    return slicedDates, slicedData
    
def data2obspy(dates, data, name):
    """
    Converts data to an obspy stream object.
    
    Parameters
    ----------
    dates: list
        List of list of Dates in UTCDateTime format.  Each list is assumed
        to be continuous and evenly sampled.
    data: list
        List of list of floats of data corresponding to the dates above.  Each
        list is assumed to be continuous and evenly sampled.
    name: string
        Channel name separated by $ in station$channel$network order
        
    Outputs
    ---------
    streamData: Stream
        Obspy stream, with each list converted to a trace with the appropriate
        metadata.
    """
    from numpy import round,array
    from obspy import Trace,Stream
    streamData = Stream()
    # Get ID
    try:
        sta,chan,net,loc = name.split('$',4)
    except:
        try:
            sta, chan, net = name.split('$',3)
            loc = ''
        except:
            try:
                sta, chan = name.split('$',2)
                net = ''
                loc = ''
            except:
                sta = name
                chan = ''
                net = ''
                loc = ''
        
        
    # Loop over lists to get metadata and convert to obspy
    for nowdates, nowdata in zip(dates, data):
        # Build metadata string, then punch the data into a Trace and save in the stream
        starttime = nowdates[0]
        npts = len(nowdata)
        delta = round(nowdates[1]-nowdates[0])
        meta = {'station': sta, 'network': net, 'channel': chan, 'location': loc, 'delta': delta, 'starttime': starttime, 'npts': npts}
        npdata = array(nowdata, dtype='float64')
        T = Trace(data=npdata, header=meta)
        T.verify()
        streamData.append(T)
    
    return streamData
    
def vtime2obspytime( vtime ):
    """
    Converts valve time string to UTCdatetime (an obspy object).
    
    Parameters
    ----------
    vtime: list
        List of strings of valve times (yyyymmddHHMMSS).
        
    Outputs
    ---------
    obspytime: list
        List of UTCdatetime objects.
    """
    from obspy import UTCDateTime
    obspytime = [nowtime.strptime(nowtime, '%Y%m%d%H%M%S') for nowtime in vtime] 
    return obspytime
    
def obspytime2vtime( obspytime ):
    """
    Converts UTCdatetime (an obspy object) to a valve time.
    
    Parameters
    ----------
    obspytime: list
        List of UTCdatetime objects.
        
    Outputs
    ---------
    vtime: list
        List of strings of valve times (yyyymmddHHMMSS).
        
    """
    vtime = [nowtime.strftime('%Y%m%d%H%M%S') for nowtime in obspytime]   
    return vtime
        
def main():
    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    # RSAM Test-------------------------------------------------------------------
    
    channel = 'NPT$HWZ$HV'
    starttime = '201504150000'
    endtime = '201504152030'
    date, datenum, data = getRsamSpan(channel, starttime, endtime)
    #date, datenum, data = getRsamLast(channel, '-12h')
    
    gapIndex = detectGap(date, 120)
    slicedDates, slicedData = splitData(date, data, gapIndex, delta=60, resample=True)
    streamDataRSAM = data2obspy(slicedDates, slicedData, channel)
    
    plt.figure()
    plt.plot_date(datenum, data, 'og')
    plt.hold()
    for x,y in zip(slicedDates, slicedData):
        plt.plot_date(md.date2num(x), y, '-')
    
    #%%    
    # Tilt Test-------------------------------------------------------------------
#    channel = 'UWE'
#    starttime = '201504150000'
#    endtime = '201504152030'
#    series = 'radial'
#    [date, datenum, data] = getTiltSpan(channel, starttime, endtime, series=series)
#    #[date, datenum, data] = getTiltLast(channel,'-12h', series=series)
#    gapIndex = detectGap(date, 120)
#    slicedDates, slicedData = splitData(date, data, gapIndex, resample=False)
#    name = '%s$%s' % (channel,series)
#    streamDataTilt = data2obspy(slicedDates, slicedData, name)
#    
#    plt.figure()
#    plt.plot_date(datenum, data, 'og')
#    plt.hold()
#    for x,y in zip(slicedDates, slicedData):
#        plt.plot_date(md.date2num(x), y, '-')
    channel = 'UWE'
    starttime = '201404230000'
    endtime = '201406110000'
    series = 'radial'
    [date, datenum, data] = getTiltSpan(channel, starttime, endtime, series=series)
    gapIndex = detectGap(date, 120)
    slicedDates, slicedData = splitData(date, data, gapIndex, resample=False)
    name = '%s$%s' % (channel,series)
    streamDataTilt = data2obspy(slicedDates, slicedData, name)
    streamDataTilt.merge(fill_value='interpolate')
    fname = '%s_%s_%s.mseed' % (channel, series, streamDataTilt[0].stats.starttime.strftime('%Y%m%d_%H%M%S'))
    streamDataTilt.write(fname, format='MSEED')
    #%%
    
    # Flyspec Test----------------------------------------------------------------
    channel = 'FLYA'
    starttime = '201504150000'
    endtime = '201504152030'
    series = 'bstflux'
    [date, datenum, data] = getFlySpecSpan(channel, starttime, endtime, series=series)
    #[date, datenum, data] = getFlySpecLast(channel, '-12h', series=series)
    gapIndex = detectGap(date, 30)
    slicedDates, slicedData = splitData(date, data, gapIndex, delta=10, resample=True)
    name = '%s$%s' % (channel,series)
    streamDataFS = data2obspy(slicedDates, slicedData, name)
    
    plt.figure()
    plt.plot_date(datenum, data, 'og')
    plt.hold()
    for x,y in zip(slicedDates, slicedData):
        plt.plot_date(md.date2num(x), y, '-')
        
if __name__ == "__main__":
    main()
