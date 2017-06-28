# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads many Garmin .fit file saves all the "record" message data into many CSV files
"""
import os
from fitparse import FitFile
import numpy as np
import pandas as pd

def TimestampToElapsed(timestamp,units='s'):
    """Convert a timestamp Pandas Series to a 
    Pandas Series of the elapsed time"""
    # the Garmin Forerunner 35 takes data every 1 second so in most cases the 
    # elapsed time will be the same as the row index
    timedelta = timestamp-timestamp[0]
    elapsed_time = timedelta.astype('timedelta64[s]') # in seconds
    # don't use 'timedelta64[m]' because it only returns the minute component of the 
    # timestamp and doesn't take into account the seconds as fractions of a minute
    if units == 'm':
        # convert from seconds to minutes
        elapsed_time = elapsed_time/60 
    return elapsed_time
    

folder_name = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/fit new/'

file_names = []
for file_name in os.listdir(folder_name):
    file_names.append(file_name)
    
# select which messages to read
desired_messages = [
#                    'session',
#                    'activity',
#                    'sport',
#                    'lap',
#                    'event',
#                    'file_id',
                    'record'
                    ]


for ifn, file_name in enumerate(file_names):
    fitfile = FitFile(folder_name + file_name)
    
    verbose = True;
    
    # Get all data messages that are of type desired_messages
    for im, message in enumerate(fitfile.get_messages(desired_messages)):
        if message.name == 'record':
            data_dict = {}
            units_dict = {}
            for message_data in message:                        
                data_dict[message_data.name] = message_data.value
                units_dict[message_data.name] = message_data.units                
                
            # Build pandas dataframe with all the recorded data
            if im == 0:
                data_pd = pd.DataFrame(data_dict, index=[im])                
            else:
                data_pd.loc[im] = data_dict
                           
                          
    elapsed_time = TimestampToElapsed(data_pd['timestamp'])
    verbose = True    
    if verbose == True:
        # print summary of file
        print "%s / %s\r" % (ifn + 1, len(file_names))
        print file_name
        print 'Done!'
        print

    
