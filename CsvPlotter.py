# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a records .csv file and plots stuff
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import pylab
#import numpy as np
#from mpl_toolkits.basemap import Basemap

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
    """Convert a timestamp pandas Series to a 
    float64 pandas Series of the elapsed time"""
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

    folder_path_read = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/csv/'
    folder_path_save = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/figures/'
    sports = [
             'walking',
             'cycling',
             'running',
#             'training',
             ]
    sports_colours = [
                     'g',                    
                     'b',
                     'r',
#                     'k'
                     ]
             
#    time_units = 'h'    
#    time_units = 'min'
    time_units = 'sec'
    
    # select files to read    
    # TODO: open a pop up window for the user to select the files

#    file_names = ['1729258358_record.csv']
#    file_paths = []    
#    folder_path_read = folder_path_read + sports[2] + '/'
#    for file_name in file_names:
#        file_paths.append(folder_path_read + file_name)

    file_names = []
    file_paths = []    
    file_colours = []
    for isp, sport in enumerate(sports):
        folder_path_sport = folder_path_read + sport + '/'
        for file_name in os.listdir(folder_path_sport):
            file_names.append(file_name)
            file_paths.append(folder_path_sport + file_name)
            file_colours.append(sports_colours[isp])
    
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(32,17), squeeze=False)
    colour_map = pylab.get_cmap('Set1')
    
#    file_paths = file_paths[15:19]
    for ifn, file_path in enumerate(file_paths):
        verbose=True
        if verbose:
            print "%s / %s\r" % (ifn+1, len(file_paths))
        # read data from csv file
        df = pd.read_csv(file_path)
        df['timestamp']=pd.to_datetime(df['timestamp'])
        df=df.set_index(pd.to_datetime(df['timestamp']))
       
        # Calculate elapsed time from the timestamp values
#        df['elapsed_time'] = TimestampToElapsed(pd.to_datetime(df['timestamp']),units=time_units)
        df['elapsed_time'] = TimestampToElapsed(df['timestamp'],units=time_units)
#        print df.shape
#        print df.info()
        
        # Filter DataFrame
        # filter by quantile or by fixed speed?
        indices = df['speed'] < df['speed'].quantile(1)
#        indices = df['speed'] > df['speed'].quantile(0.5)
#        indices_1 = df['speed'] < 2 # m/s
#        indices_2 = df['speed'] > 2 # m/s
#        indices = list(set(indices_1) & set(indices_2))
#        df_filtered = df.loc[indices,:]
        df = df.loc[indices,:]
#        df_filtered['speed']*df_filtered['distance']
#        print df_filtered.shape
        
        delta_time = []
        calculated_distance = []
        previous_elapsed_time = 0.0
        previous_distance = 0.0
        for ir, row in df.iterrows():
            if ir > df.index[0]:
                delta_time.append(row['elapsed_time'] - previous_elapsed_time)
                calculated_distance.append(row['speed']*delta_time[-1] + previous_distance)
                previous_distance = calculated_distance[-1]
            previous_elapsed_time = row['elapsed_time']
#            calculated_distance = df['speed']*df['elapsed_time']
        
        # Investigate outliers with the difference between the mean and the median
        stats = df.describe()
        skewness = (stats.loc['mean']-stats.loc['50%'])/stats.loc['mean']*100 # skewness = (mean - median) / std
        skewness = pd.DataFrame(skewness)
        skewness = skewness.transpose()
        if ifn == 0:
            skewness_df = skewness
        else:
            skewness_df = skewness_df.append(skewness,ignore_index=True)
            # TODO: sort out the row indices, they are all 0 now
        
#        df
#        plt.subplot(311)
#        plt.plot(df['distance']/1000, df['elapsed_time'], label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
    
#        plt.subplot(312)
#        plt.subplot(211)
#        plt.plot(df['distance']/1000, df['speed']*3.6, label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
#        plt.plot(df['elapsed_time'], df['speed']*3.6, label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
#        plt.plot(df['elapsed_time'], df['speed']*3.6, label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
#        plt.plot(df['elapsed_time'], df['distance'], label='raw distance')
#        plt.plot(df['elapsed_time'][1:], calculated_distance, label='new distance',)
#        plt.plot(df['timestamp'], df['speed']*3.6, label=df['timestamp'][0], color=colour_map(1.*ifn/len(file_paths)))
        df.plot(ax=axes[0,0], x='speed', y='heart_rate', 
                kind='scatter', color=file_colours[ifn], edgecolors='none',
                legend=False)        
        axes[0,0].set_xlim([0,10])

        df.plot(ax=axes[0,1], x='position_long', y='position_lat', 
                kind='scatter', color=file_colours[ifn], edgecolors='none',
                legend=False)
        axes[0,1].set_xlim([0.05e7,0.25e7])
        axes[0,1].set_ylim([6.226e8,6.238e8])
        
        plt.subplot(axes[1,0])
        plt.hist(df['speed'], color=file_colours[ifn], alpha=0.3, normed=True, bins=100)
        axes[1,0].set_xlabel('speed')
        axes[1,0].set_xlim([0,10])

        df.plot(ax=axes[1,1], x='distance', y='speed', 
                kind='scatter', color=file_colours[ifn], edgecolors='none', 
                legend=False)
        axes[1,1].set_ylim([0,10])
        
        
#    print df.columns
#    print(skewness_df.loc[:,['speed','heart_rate']])
    
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
#    plt.subplot(211)
#    plt.legend(loc='upper left',fontsize=34)
#    plt.title(sport)
#    plt.xlabel('distance (km)')
#    plt.xlabel('elapsed time (' + time_units + ')')
#    plt.ylabel('speed (km/h)')
#    plt.xlim([0,4.5])
#    plt.ylim([0,60])
    
#    plt.subplot(313)
#    plt.subplot(212)
#    plt.xlabel('distance (km)')
#    plt.xlabel('elapsed time (' + time_units + ')')
#    plt.ylabel('heart rate (bpm)')
    
#    plt.xlim(['11-may-2017','16-may-2017'])
#    axes[0].set_xlim([0,10])
#    axes[1].set_xlim([0,10])
    plt.show()
    
#    skewness_df.plot(y=['speed','heart_rate'])

# USEFUL STUFF    
 
#plt.yscale('log')
#df.plot(subplots=True,kind='line')
#plt.savefig(folder_path_save + 'test.png')
#df.plot(y='heart_rate',kind='hist',bins=100,normed=True,cumulative=True)
#df.plot(x='elapsed_time',y=['speed','heart_rate'])
#fig, axes = plt.subplots(nrows=2, ncols=1)
#df.plot(ax=axes[0]...)
#df.plot(x='elapsed_time',y=['speed','heart_rate','distance'],subplots=True)
#df.plot(x='distance',y=['speed','heart_rate','elapsed_time'],subplots=True)
#sorted(df['heart_rate'].unique())
#df['speed'].plot(kind='hist',bins=200,normed=True,alpha=0.3)