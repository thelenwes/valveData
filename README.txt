Readme for valveData.py

Library to extract data from valve using a REST interface.  Optionally, data
can be detected for gaps, resampled and put into a obspy Stream structure.  Requires
a parameter file called 'config.json' in the same directory as script.  Contents
should look something like this:
{
  "host": "hvo-rest.wr.usgs.gov"
}
See requests documentation for more details.
--------------------------------------------------------------------

Requirements:
json
requests
obspy (for splitData, data2obspy, vtime2obspytime, obspytime2vtime)


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

