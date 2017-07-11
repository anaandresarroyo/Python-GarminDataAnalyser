# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a records .csv file and plots stuff
"""

import matplotlib
# Force matplotlib to not use any Xwindows backend.
#matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import pylab
import gmplot
import datetime

matplotlib.rcParams.update({'font.size': 30})

matplotlib.rcParams.update({'lines.linewidth': 5})
matplotlib.rcParams.update({'axes.grid': True})
matplotlib.rcParams.update({'axes.linewidth': 2})
matplotlib.rcParams.update({'axes.axisbelow': True})
matplotlib.rcParams.update({'axes.labelpad': 3})
#matplotlib.rcParams.update({'axes.titlepad': 25})

matplotlib.rcParams.update({'xtick.major.size': 15})
matplotlib.rcParams.update({'ytick.major.size': 15})
matplotlib.rcParams.update({'xtick.major.pad': 10})
matplotlib.rcParams.update({'ytick.major.pad': 10})
matplotlib.rcParams.update({'xtick.major.width': 2})
matplotlib.rcParams.update({'ytick.major.width': 2})

matplotlib.rcParams.update({'grid.linewidth': 1.5})
#matplotlib.rcParams.update({'legend.frameon': False})



def ElapsedTime(timestamp, units_t='sec', mode='start'):    
    """Calculate the elapsed time from a timestamp pandas Series.
        
    Arguments:
    timestamp : timestamp pandas Series
        Timestamp values
    units_d: string
        Units of the calculated time, e.g. 'sec' (default), 'min', or 'h'
    mode : string
        If 'start' calculate the elapsed time between all points of the array and the first point.
        If 'previous' calculate the elapsed time between all points of the array the previous point.
    
    Output:
    elapsed_time: float pandas Series
        Contains the calculated elapsed time in units of units_t
    """
    
    # The Garmin Forerunner 35 takes data every 1 second

    origin_time =  np.empty(timestamp.shape, dtype=type(timestamp))
    if mode == 'start':
        origin_time[:] = timestamp[0]
    
    elif mode == 'previous':
        origin_time[0] = timestamp[0]
        for i, time in enumerate(timestamp[0:-1]):
            origin_time[i+1] = time
            
    else:
        raise ValueError('Unable to recognise the mode.')  
    
    timedelta = timestamp-origin_time
    elapsed_time = timedelta.astype('timedelta64[s]') # in seconds
    
    if units_t == 'sec':
        pass    
    elif units_t == 'min':
        # Convert seconds to minutes
        elapsed_time = elapsed_time/60 
    elif units_t == 'h':
        # Convert seconds to hours
        elapsed_time = elapsed_time/60/60 
    else:
        raise ValueError('Unable to recognise the units for the time.')    
    return elapsed_time
    
def Distance(longitude, latitude, units_gps='semicircles', units_d='m',
             mode='start', fixed_lon=1601994.0, fixed_lat=622913929.0):
    """Calculate the great circle distance between two points
    on the earth using the Haversine formula.
        
    Arguments:
    longitude : float pandas Series
        Longitude values of GPS coordinates, in units of units_gps
    latitude : float pandas Series
        Latitude values of GPS coordinates, in units of units_gps        
    units_gps : string
        Units of longitude or latitude, e.g. 'semicircles' (default) or 'degrees'
    units_d: string
        Units of the calculated distance, e.g. 'm' (default) or 'km'
    mode : string
        If 'start' calculate the distance between all points of the array and the first point.
        If 'previous' calculate the distance between all points of the array the previous point.
        If 'fixed' calculate the distance between all points of the array and a fixed point.
    fixed_lon: float
        Longitude value in units of units_gps to be used with mode='fixed'
    fixed_lat: float
        Latitude value in units of units_gps to be used with mode='fixed'        
    
    Output:
    distance: float pandas Series
        Contains the calculated distance in units of units_d
    """
    
    if units_gps == 'semicircles':
        # Convert semicircles to degrees
        longitude = longitude*180/2**31
        latitude = latitude*180/2**31
    elif units_gps == 'degrees':
        pass
    else:
        raise ValueError('Unable to recognise the units for the longitude and latitude.')
    
    origin_lon = np.empty(longitude.shape)
    origin_lat = np.empty(latitude.shape)
    
    if mode == 'start':
        origin_lon[:] = longitude[0]
        origin_lat[:] = latitude[0]
    
    elif mode == 'previous':
        origin_lon[0] = longitude[0]
        origin_lat[0] = latitude[0]
        
        origin_lon[1:] = longitude[0:-1]
        origin_lat[1:] = latitude[0:-1]
        
    elif mode == 'fixed':
        if units_gps == 'semicircles':
            fixed_lon = fixed_lon*180/2**31
            fixed_lat = fixed_lat*180/2**31
            
        origin_lon[:] = fixed_lon
        origin_lat[:] = fixed_lat

    else:
        raise ValueError('Unable to recognise the mode.')  
    
    # Radius of the Earth in units of units_d
    if units_d == 'm':
        radius = 6371000
    elif units_d == 'km':
        radius = 6371
    else:
        raise ValueError('Unable to recognise the units for the distance.')
    
    delta_lon = np.radians(longitude-origin_lon)
    delta_lat = np.radians(latitude-origin_lat)
    # Haversine formula
    a = np.sin(delta_lat/2) * np.sin(delta_lat/2) + np.cos(np.radians(origin_lat)) \
        * np.cos(np.radians(latitude)) * np.sin(delta_lon/2) * np.sin(delta_lon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))    
    distance = radius * c # Same units as radius
    # TODO: check the validity of the Haversine formula
    # https://en.wikipedia.org/wiki/Geographical_distance

    return distance
    
def AutoStop(df, mode='std', threshold=15, correction=False):
    """Crop the pandas DataFrame to eliminate the data points at the end in 
    which the user wasn't moving but the device was still recording data.
        
    Arguments:
    df : pandas DataFrame
        Garmin data. Required columns: 'position', 'speed'
    mode : string
        If 'std' (default) use the position's standard deviation to determine the end of the activity.
    threshold : double
        If mode='std' the threshold (in units of m) is used to determine the end of the activity
       
    Output:
    df: pandas DataFrame
        Contains the cropped data.
    """
    # Create new column in which to store the position's standard deviation
    df['position_std'] = np.nan
    for ip in df.index:
        # Calculate the standard deviation in the position from index ip until the end
        df.loc[ip,'position_std'] = np.std(df.loc[ip:,'position'])
#    df['position_std']=df['position_std']/ElapsedTime(df['timestamp'], units_t='sec', mode='previous')
    # Calculate the index at which the user stopped moving
    index_stop = df.index[df['position_std']<=threshold][0]
#    print df['timestamp'][0]
#    print df['timestamp'][-1]
#    print index_stop
    
    if correction:
        # Correct for the time it takes for the user to travel a distance equal
        # to the threshold at the average speed of the acitivity
        print 'threshold = ' + str(threshold) + ' m'
    #    print df.head()
    #    average_speed = np.mean(df.loc[:index_stop,'speed'])*0.2
#        average_speed = df.loc[index_stop,'speed']
    #    average_speed = np.mean(df['speed'])
#        print average_speed
#        seconds = threshold / average_speed
        seconds = 15
        print str(seconds) + ' seconds'
        timestamp_correction = datetime.timedelta(0, seconds) # (days, secons, ...)
#        print timestamp_correction
        # TODO: confirm that the df index is a timestamp
        index_stop = index_stop + timestamp_correction
#        print index_stop
        print
        
    # Discard the rows at the end in which the user wasn't moving
    df[:] = df.loc[:index_stop,:]
    return df
    
    
if __name__ == '__main__':

    directory_path_read = 'C:/Users/Ana Andres/Dropbox/Garmin/csv/'
    directory_path_save = 'C:/Users/Ana Andres/Dropbox/Garmin/figures/'
    sports = [
#             'walking',
#             'cycling',
             'running',
#             'training',
#             'test',
             ]
    colours = {'walking':'k',
               'cycling':'b',
               'running':'r',
               'training':'g',
               'test':'k'}
    
#    units_t = 'sec'
    units_t = 'min'
#    units_t = 'h'    
    
    units_d = 'm'
#    units_d = 'km'
    
    plot_map=True
    
    # ---------------------------------------
    
    # select files to read    
    # TODO: open a pop up window for the user to select the files    
    file_paths = []    
    file_sports = []
    for sport in sports:
        directory_path_sport = directory_path_read + sport + '/'
#        for file_name in os.listdir(directory_path_sport):
        for file_name in reversed(os.listdir(directory_path_sport)):
            file_paths.append(directory_path_sport + file_name)
            file_sports.append(sport)
    
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(32,17), squeeze=False)
#    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(32,17), squeeze=False)
#    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(32,17), squeeze=True)
    colour_map = pylab.get_cmap('Set1')
    
    
    if plot_map:
        gmap = gmplot.GoogleMapPlotter(52.22, 0.120, 12) # Cambridge 
#        gmap = gmplot.GoogleMapPlotter(46.36, 14.09, 11) # Lake Bled
    
    time_offset=0
#    number_of_files = 1
    number_of_files = len(file_paths);
    for file_path, sport, ifn in zip(file_paths, file_sports, range(number_of_files)):
        verbose=True
        if verbose:
            print "%s / %s: %s" % (ifn+1, number_of_files, sport)
        # Read data from .csv file
        df = pd.read_csv(file_path)
        # Convert timestamp column from string to datetime
        df['timestamp']=pd.to_datetime(df['timestamp'])
        # Set timestamp column as row indices
        df=df.set_index(pd.to_datetime(df['timestamp']))
       
        # Calculate elapsed time from the timestamp values
        df['elapsed_time'] = ElapsedTime(df['timestamp'], units_t=units_t)
        
        # Filter DataFrame
        # filter by quantile or by fixed speed?
        indices = df['speed'] < df['speed'].quantile(1)
#        indices = df['speed'] > df['speed'].quantile(0.5)
#        indices_1 = df['speed'] < 2 # m/s
#        indices_2 = df['speed'] > 2 # m/s
#        indices = list(set(indices_1) & set(indices_2))
#        df_filtered = df.loc[indices,:]
#        df[:] = df.loc[indices,:]
#        df_filtered['speed']*df_filtered['distance']
#        print df_filtered.shape
        
#        delta_time = []
#        calculated_distance = [0.0]
#        previous_elapsed_time = 0.0
#        previous_distance = 0.0
#        for ir, row in df.iterrows():
#            if ir > df.index[0]:
#                delta_time.append(row['elapsed_time'] - previous_elapsed_time)
#                calculated_distance.append(row['speed']*delta_time[-1] + previous_distance)
#                previous_distance = calculated_distance[-1]
#            previous_elapsed_time = row['elapsed_time']
#        # TODO: fix NaNs!!!
        
        # Investigate outliers with the difference between the mean and the median
#        stats = df.describe()
#        skewness = (stats.loc['mean']-stats.loc['50%'])/stats.loc['mean']*100 # skewness = (mean - median) / std
#        skewness = pd.DataFrame(skewness)
#        skewness = skewness.transpose()
#        if ifn == 0:
#            skewness_df = skewness
#        else:
#            skewness_df = skewness_df.append(skewness,ignore_index=True)
        
        df.plot(ax=axes[0,0], x='speed', y='cadence', s=30, 
                kind='scatter', color=colours[sport], edgecolors='none',
                legend=False)        
        axes[0,0].set_xlim([0,10])

#        df.plot(ax=axes[0,1], x='position_long', y='position_lat', 
#                kind='scatter', color=colours[sport], edgecolors='none',
#                legend=False)
#        axes[0,1].set_xlim([0.05e7,0.25e7])
#        axes[0,1].set_ylim([6.226e8,6.238e8])

        
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
#        plt.xlabel('time ('+units_t+')')
        
#        plt.subplot(221)
#        plt.plot(df['elapsed_time'], df['speed']*3.6,
#                label=os.path.basename(file_path), linewidth=2)
##        plt.plot(df['elapsed_time'][1:], np.diff(df['speed']*20),
##                label=os.path.basename(file_path), linewidth=2)
#        plt.ylabel('speed (km/h)')
#        plt.xlabel('time ('+units_t+')')
#        plt.legend(loc='upper right',fontsize=34)
        
#        plt.subplot(222)
#        plt.scatter(df['speed'][1:]*3.6, np.diff(df['speed']*3.6), 
#                    c=df['heart_rate'][1:], cmap='rainbow', edgecolors='none')
#        plt.xlabel('speed (km/h)')
#        plt.ylabel('acceleration (km/h/' + units_t + ')')
        
##        position = Distance(df['position_long'], df['position_lat'], mode='previous')
##        position = np.cumsum(position)
#        df['distance_new'] = np.cumsum(Distance(df['position_long'], df['position_lat'], mode='previous'))
#        df['position'] = Distance(df['position_long'], df['position_lat'], mode='start', units_d='m')
#        df['speed_new'] = Distance(df['position_long'], df['position_lat'], mode='previous', units_d='m') \
#                / ElapsedTime(df['timestamp'], units_t='sec', mode='previous')
#        
#        df = AutoStop(df, threshold=0)
##        
#        plt.subplot(411)
##        plt.plot(df['elapsed_time'], df['distance'], label='distance')
#        plt.plot(df['elapsed_time'], df['position'], label='position')        
##        plt.legend(loc='lower right',fontsize=34)
#        plt.ylabel('position ('+units_d+')')
#        plt.xlabel('time ('+units_t+')')
##        plt.xlim([15,20])
#        
#        plt.subplot(412)
#        plt.plot(df['elapsed_time'], df['position_std'], label='position std')
##        plt.legend(loc='upper right',fontsize=34)
#        plt.ylabel('position std ('+units_d+')')
#        plt.xlabel('time ('+units_t+')')
#        
#        plt.subplot(413)
#        plt.plot(df['elapsed_time'][1:], np.diff(df['position_std']))
#        plt.ylabel('d position std / d time (a.u.)')
#        plt.xlabel('time ('+units_t+')')
#        
#        plt.subplot(414)
#        plt.plot(df['elapsed_time'], df['speed'], label='speed')
##        plt.plot(df['elapsed_time'], df['speed_new'], label='speed new')
#        plt.plot(df['elapsed_time'][1:], np.diff(df['distance_new']))
#        
#        df = AutoStop(df, mode='diff', threshold=5, correction=False)
#        
##        plt.subplot(222)
#        plt.subplot(411)
#        plt.plot(df['elapsed_time'], df['position'], label='position filtered')
##        plt.plot(df['elapsed_time'], df['distance'], label='distance filtered')
##        plt.legend(loc='lower right',fontsize=34)
#        plt.ylabel('position ('+units_d+')')
#        plt.xlabel('time ('+units_t+')')
##        plt.ylim([1550,1650])
##        plt.xlim([16.5,17])
#        
##        plt.subplot(224)
#        plt.subplot(412)
#        plt.plot(df['elapsed_time'], df['position_std'], label='position std filtered')
##        plt.legend(loc='upper right',fontsize=34)
#        plt.ylabel('position std ('+units_d+')')
#        plt.xlabel('time ('+units_t+')')
##        plt.ylim([0,10])
##        plt.xlim([16.5,17])
#        
#        plt.subplot(413)
#        plt.plot(df['elapsed_time'][1:], np.diff(df['position_std']))
#        plt.ylabel('d position std / d time (a.u.)')
#        plt.xlabel('time ('+units_t+')')
##        plt.xlim([16.5,17])
#        
#        plt.subplot(414)
#        plt.plot(df['elapsed_time'], df['speed'], label='speed filtered')
#        plt.xlabel('time ('+units_t+')')
#        plt.ylabel('speed (m/s)')
#        plt.legend(loc='upper right',fontsize=34)
#        plt.ylim([0,6])
#        plt.xlim([16.5,17])
        
#        h = plt.hist(position, normed=True, alpha=0.5, bins=50,
#                     label=os.path.basename(file_path), linewidth=2)
#        plt.xlabel('position (a.u.)')
        
#        plt.subplot(223)
#        plt.scatter(df['speed']*3.6, df['heart_rate'])
#        plt.xlabel('speed (km/h)')
#        plt.ylabel('heart_rate (bpm)')
        

#        plt.plot(df['position_lat']*180/2**31, df['position_long']*180/2**31, color=colours[sport])
#        gmap.plot(df['position_long']*180/2**31, df['position_lat']*180/2**31, color=colours[sport])
        if plot_map:
            # Add a line plot to the gmap object which will be save to an .html file
            # Use line instead of scatter plot for faster speed and smaller file size
            # Make sure to remove NaNs or the plot won't work
            gmap.plot(df['position_lat'].dropna()*180/2**31, df['position_long'].dropna()*180/2**31, color=colours[sport])
        
        
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
    plt.show()

    if plot_map:
        gmap.draw(directory_path_save + 'mymap.html')
    
#    skewness_df.plot(y=['speed','heart_rate'])

# USEFUL STUFF    
 
#plt.yscale('log')
#df.plot(subplots=True,kind='line')
#plt.savefig(directory_path_save + 'test.png')
#df.plot(y='heart_rate',kind='hist',bins=100,normed=True,cumulative=True)
#df.plot(x='elapsed_time',y=['speed','heart_rate'])
#fig, axes = plt.subplots(nrows=2, ncols=1)
#df.plot(ax=axes[0]...)
#df.plot(x='elapsed_time',y=['speed','heart_rate','distance'],subplots=True)
#df.plot(x='distance',y=['speed','heart_rate','elapsed_time'],subplots=True)
#sorted(df['heart_rate'].unique())
#df['speed'].plot(kind='hist',bins=200,normed=True,alpha=0.3)