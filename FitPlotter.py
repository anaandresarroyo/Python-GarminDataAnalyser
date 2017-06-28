# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a Garmin .fit file and plots the elapsed time, distance, and speed
"""
import os
from fitparse import FitFile
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

folder_name = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/tests/Cycling/'
#folder_name = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/tests/Running/'

#file_names = []
#for file_name in os.listdir(folder_name):
#    file_names.append(file_name)
##    print file_name

file_names = [
#              '1736326674.fit', # probike
#              '1738248352.fit',
#              '1740125308.fit',
#              '1748066969.fit',
#              '1750027812.fit',
#              '1755525793.fit',
#              '1759345190.fit',
#              '1767547532.fit',
#              '1769462985.fit',
#              '1771560728.fit',
#              '1773319990.fit',
#              '1779930535.fit',
#              '1783461306.fit',
#              '1784754409.fit',
#              '1786757983.fit',
#              '1793953245.fit',
#              '1796497051.fit',
#              '1800679832.fit',
#              '1806473488.fit',
#              '1810347567.fit',
#              '1819685424.fit',
              '1821550522.fit', # trek
              '1823366347.fit',
              ] # cycling
    
              
plt.figure(figsize=(32,17))
colour_map = pylab.get_cmap('Reds')

# select which messages to read
desired_messages = [
#                    'session',
#                    'activity',
                    'sport',
#                    'lap',
#                    'event',
#                    'file_id',
                    'record'
                    ]

for ifn, file_name in enumerate(file_names):
    fitfile = FitFile(folder_name + file_name)
    
    verbose = True;
    
    # initialise empty array to count types of messages
    message_count = {}
    
    # initialise empy lists to collect the data
    # TODO: use numpy arrays
    data_points = []
    heart_rate = []
    speed = []
    distance = []
    timestamp = []
    elapsed_time = []
       
    # Get all data messages that are of type desired_messages
    for im, message in enumerate(fitfile.get_messages(desired_messages)):            
        if message.name == 'record':
            data_points.append(im) # if there are only 'record' messages
            heart_rate.append(message.get_value('heart_rate'))
            try:
                speed.append(message.get_value('speed')*3.6) # m/s to km/h conversion
            except TypeError: 
                # when there is no recorded speed the value is 'None' and a TypeError is returned
                speed.append(0)
            distance.append(message.get_value('distance')/1000) # m to km conversion
            timestamp.append(message.get_value('timestamp'))
            # note that the timestamp is off by one hour, maybe due to daylights savings?
            timedelta = timestamp[-1]-timestamp[0]
            elapsed_time.append(timedelta.total_seconds()/60) # in minutes
            
        
    verbose = True
    if verbose == True:
        # print summary of file
        print "%s / %s\r" % (ifn+1, len(file_names))
        print file_name
        print
    
    
    plt.subplot(221)
    plt.plot(distance, elapsed_time, label=timestamp[0], color=colour_map(1.*ifn/len(file_names)))

    plt.subplot(223)
    plt.plot(distance, speed, label=timestamp[0], color=colour_map(1.*ifn/len(file_names)))
    

plt.subplot(221)
#plt.title('Cycling to work')
plt.title(folder_name)
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fontsize=34)
plt.ylabel('elapsed time (minutes)')
plt.xlabel('distance (km)')
#plt.ylim([0,25])
#plt.xlim([0,4.5])

plt.subplot(223)
plt.xlabel('distance (km)')
plt.ylabel('speed (km/h)')
#plt.xlim([0,4.5])

plt.show()
