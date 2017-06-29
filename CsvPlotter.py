# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a records .csv file and plots stuff
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import pylab

from matplotlib import rcParams
rcParams.update({'font.size': 36})

rcParams.update({'lines.linewidth': 5})
rcParams.update({'axes.grid': True})
rcParams.update({'axes.linewidth': 2})
rcParams.update({'axes.axisbelow': True})
rcParams.update({'axes.labelpad': 3})
#rcParams.update({'axes.titlepad': 25})

rcParams.update({'xtick.major.size': 15})
rcParams.update({'ytick.major.size': 15})
rcParams.update({'xtick.major.pad': 10})
rcParams.update({'ytick.major.pad': 10})
rcParams.update({'xtick.major.width': 2})
rcParams.update({'ytick.major.width': 2})

rcParams.update({'grid.linewidth': 1.5})
#rcParams.update({'legend.frameon': False})

def TimestampToElapsed(timestamp,units='sec'):
    """Convert a timestamp Pandas Series to a 
    Pandas Series of the elapsed time"""
    # the Garmin Forerunner 35 takes data every 1 second so in most cases the 
    # elapsed time will be the same as the row index
    timedelta = timestamp-timestamp[0]
    elapsed_time = timedelta.astype('timedelta64[s]') # in seconds
    # don't use 'timedelta64[m]' because it only returns the minute component of the 
    # timestamp and doesn't take into account the seconds as fractions of a minute
    if units == 'min':
        # convert from seconds to minutes
        elapsed_time = elapsed_time/60 
    if units == 'h':
        # convert from seconds to hours
        elapsed_time = elapsed_time/60/60 
    return elapsed_time
    
    
if __name__ == '__main__':

    folder_name = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/csv/'
#    sport = 'cycling'
    sport = 'running'
#    sport = 'walking'
#    sport = 'training'
    time_units = 'h'    
#    time_units = 'min'
#    time_units = 'sec'
    
    # select files to read    
    file_names = []
    file_paths = []
    folder_path_read = folder_name + sport + '/'
    for file_name in os.listdir(folder_path_read):
        file_names.append(file_name)
        file_paths.append(folder_path_read + file_name)
    
#    plt.figure(figsize=(32,17))
    colour_map = pylab.get_cmap('Set1')
    
#    file_paths = file_paths[15:19]
    for ifn, file_path in enumerate(file_paths):
        # read data from csv file
        df = pd.read_csv(file_path)#, parse_dates=True, infer_datetime_format=True)
        
        #calculate elapsed time from the timestamp values
        df['elapsed_time'] = TimestampToElapsed(pd.to_datetime(df['timestamp']),units=time_units)
        
#        plt.subplot(311)
#        plt.plot(df['distance']/1000, df['elapsed_time'], label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
    
#        plt.subplot(312)
        plt.subplot(211)
        plt.plot(df['distance']/1000, df['speed']*3.6, label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
#        plt.plot(df['elapsed_time'], df['speed']*3.6, label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
        
#        plt.subplot(313)
        plt.subplot(212)
        plt.plot(df['distance']/1000, df['heart_rate'], label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
        
    
#    plt.subplot(311)
#    plt.title(sport)
#    if len(file_paths) <= 5:
##        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fontsize=34)
#        plt.legend(loc='upper left',fontsize=34)
#    plt.ylabel('elapsed time (' + time_units + ')')
#    plt.xlabel('distance (km)')
#    #plt.ylim([0,25])
#    #plt.xlim([0,4.5])
    
#    plt.subplot(312)
    plt.subplot(211)
    plt.xlabel('distance (km)')
#    plt.xlabel('elapsed time (' + time_units + ')')
    plt.ylabel('speed (km/h)')
    #plt.xlim([0,4.5])
#    plt.ylim([0,60])
    
#    plt.subplot(313)
    plt.subplot(212)
    plt.xlabel('distance (km)')
    plt.ylabel('heart rate (bpm)')
    
    plt.show()
