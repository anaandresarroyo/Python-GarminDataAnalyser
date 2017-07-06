# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a records .csv file and plots stuff
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import pylab
import mplleaflet
import gmplot
#import gmaps

from matplotlib import rcParams
rcParams.update({'font.size': 30})

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

    folder_path_read = 'C:/Users/Ana Andres/Dropbox/Garmin/csv/'
    folder_path_save = 'C:/Users/Ana Andres/Dropbox/Garmin/figures/'
    sports = [
#             'walking',
             'cycling',
#             'running',
#             'training',
#             'test',
             ]
    colours = {'walking':'k',
               'cycling':'b',
               'running':'r',
               'training':'g',
               'test':'k'}
             
#    time_units = 'h'    
    time_units = 'min'
#    time_units = 'sec'
    
    # select files to read    
    # TODO: open a pop up window for the user to select the files

    
    file_paths = []    
    file_sports = []
    for sport in sports:
        folder_path_sport = folder_path_read + sport + '/'
        for file_name in os.listdir(folder_path_sport):
#        for file_name in reversed(os.listdir(folder_path_sport)):
            file_paths.append(folder_path_sport + file_name)
            file_sports.append(sport)
    
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(32,17), squeeze=False)
#    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(32,17), squeeze=False)
#    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(32,17), squeeze=True)
    colour_map = pylab.get_cmap('Set1')
    
    plot_map=True
    if plot_map:
#        gmap = gmplot.GoogleMapPlotter(52.22, 0.120, 12)
        gmap = gmplot.GoogleMapPlotter(46.36, 14.09, 11)
#    fig=gmaps.Map()
    
    time_offset=0
    number_of_files = 12
#    number_of_files = len(file_paths);
    for file_path, sport, ifn in zip(file_paths, file_sports, range(number_of_files)):
        verbose=True
        if verbose:
            print "%s / %s: %s" % (ifn+1, number_of_files, sport)
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
        print df['position_lat'].mean()
        print df['position_long'].mean()
        skewness = (stats.loc['mean']-stats.loc['50%'])/stats.loc['mean']*100 # skewness = (mean - median) / std
        skewness = pd.DataFrame(skewness)
        skewness = skewness.transpose()
        if ifn == 0:
            skewness_df = skewness
        else:
            skewness_df = skewness_df.append(skewness,ignore_index=True)
        
#        df.plot(ax=axes[0,0], x='speed', y='heart_rate', 
#                kind='scatter', color=colours[sport], edgecolors='none',
#                legend=False)        
#        axes[0,0].set_xlim([0,10])

#        df.plot(ax=axes[0,1], x='position_long', y='position_lat', 
#                kind='scatter', color=colours[sport], edgecolors='none',
#                legend=False)
#        axes[0,1].set_xlim([0.05e7,0.25e7])
#        axes[0,1].set_ylim([6.226e8,6.238e8])
#        garmin_layer = gmaps.symbol_layer(df['position_lat','position_long']*180/2**31,
#                                          fill_color=colours[sport], scale=12)
#        fig=gmaps.figure()
#        fig.add_layer(garmin_layer)
#        fig
#        mplleaflet.display(fig=ax.figure)
        
#        df.plot(ax=axes[1,0], y='speed', 
#                kind='hist', bins=100, normed=True, 
#                color=colours[sport], edgecolor='none', alpha=0.3, 
#                legend=False)
#        axes[1,0].set_xlabel('speed')
#        axes[1,0].set_xlim([0,10])

#        df.plot(ax=axes[1,1], x='distance', y='speed', 
#                kind='scatter', color=colours[sport], edgecolors='none', 
#                legend=False)
#        axes[1,1].set_ylim([0,10])

#        plt.plot(df['elapsed_time']+time_offset, 1/df['speed']*100/6,
#                label=df['timestamp'][0], linewidth=2)
#        plt.gca().invert_yaxis()
#        plt.ylim([15,3])
#        time_offset = df['elapsed_time'][-1] + time_offset
#        plt.ylabel('pace (min/km)')
#        plt.xlabel('time ('+time_units+')')
        
        plt.plot(df['elapsed_time'], df['distance'],
                label=df['timestamp'][0], linewidth=2)
#        plt.ylim([15,3])
        time_offset = df['elapsed_time'][-1] + time_offset
        plt.ylabel('speed (km/h)')
        plt.xlabel('time ('+time_units+')')
        
#        df.plot(ax=axes[0,0], x='distance', y='speed', 
#                kind='line', 
#                label=df['timestamp'][0], legend=True)

#        plt.plot(df['position_lat']*180/2**31, df['position_long']*180/2**31, color=colours[sport])
#        gmap.plot(df['position_long']*180/2**31, df['position_lat']*180/2**31, color=colours[sport])
        if plot_map:
#            plt.plot(df['position_long']*180/2**31, df['position_lat']*180/2**31, color=colours[sport])
            gmap.plot(df['position_lat'].dropna()*180/2**31, df['position_long'].dropna()*180/2**31, color=colours[sport])
        # TODO: it doesn't work with "walking" data :( FIX IT!!
#        gmap.scatter(df['position_lat']*180/2**31, df['position_long']*180/2**31, 'k', marker=True)
        
        
#    print df.columns
#    print(skewness_df.loc[:,['speed','heart_rate']])
#    print(skewness_df.loc[:,['position_lat','position_long']])
    
#    plt.subplot(311)
#    plt.title(sport)
#    if len(file_paths) <= 5:
##        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fontsize=34)
#    plt.legend(loc='upper right',fontsize=34)
    
#    plt.xlim(['11-may-2017','16-may-2017'])
#    axes[0].set_xlim([0,10])
#    axes[1].set_xlim([0,10])
#    plt.show()
#    mplleaflet.show(fig=ax.figure)
    if plot_map:
        gmap.draw("mymap.html")
    
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