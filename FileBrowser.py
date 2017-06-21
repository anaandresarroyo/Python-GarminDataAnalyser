# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 18:18:21 2017

@author: Ana Andres

Reads a Garmin .fit file and displays the messages and their type
"""

from fitparse import FitFile
import matplotlib.pyplot as plt

from matplotlib import rcParams
rcParams.update({'font.size': 40})

rcParams.update({'lines.linewidth': 5})
rcParams.update({'axes.grid': True})
rcParams.update({'axes.linewidth': 2})
rcParams.update({'axes.axisbelow': True})
rcParams.update({'axes.labelpad': 10})
#rcParams.update({'axes.titlepad': 25})

rcParams.update({'xtick.major.size': 15})
rcParams.update({'ytick.major.size': 15})
rcParams.update({'xtick.major.pad': 25})
rcParams.update({'ytick.major.pad': 25})
rcParams.update({'xtick.major.width': 2})
rcParams.update({'ytick.major.width': 2})

rcParams.update({'grid.linewidth': 1.5})

#rcParams.update({'legend.frameon': False})



folder_name = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/Running/'
#file_name = '1799291774.fit' # squash
#file_name = '1804849333.fit' # running
#file_name = '1806473488.fit' # cycling
#file_name = '1807619481.fit' # walking
#file_name = '12378630852.fit' # exported from day view
#file_name = '12378631774.fit' # exported from day view

file_names = ['1741229575.fit',
              '1768541987.fit',
              '1776168778.fit',
              '1791583142.fit',
              '1795613506.fit',
              '1804849333.fit',
              ] # running
start_time = []

for file_name in file_names:
    fitfile = FitFile(folder_name + file_name)
    
    i = 0
    verbose = False;
    
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
    
    # select which messages to read
    desired_messages = range(300); # all messages
    desired_messages = 'record'
    #desired_messages = ['session','activity',
    #                    'sport','lap','event','file_id']
    
    # Get all data messages that are of type message
    for i, message in enumerate(fitfile.get_messages(desired_messages)):
           
        # if the message is in message_count dictionary, add 1
        if message.name in message_count.keys():
            message_count[message.name] = message_count[message.name] + 1
        # else add the message to message_count dictionary, set the value to 1
        else:
            message_count[message.name] = 1
            
        if message.name == 'record':
            data_points.append(i) # if there are only 'record' messages
            heart_rate.append(message.get_value('heart_rate'))
            speed.append(message.get_value('speed'))
            distance.append(message.get_value('distance')/1000) # in km
            timestamp.append(message.get_value('timestamp'))
            timedelta = timestamp[-1]-timestamp[0]
            elapsed_time.append(timedelta.total_seconds()/60) # in minutes
    
        if verbose == True:
            # Print the message number and name
            print " - %s: %s: %s -------------------------" % (i, message.mesg_num, message.name)
            
            # Go through all the data entries in this message
            for message_data in message:
        
                # Print the messages name and value (and units if it has any)
                if message_data.units:
                    print " * %s: %s %s" % (
                        message_data.name, message_data.value, message_data.units,
                    )
                else:
                    print " * %s: %s" % (message_data.name, message_data.value)
            print
        verbose = False;
        
    
    # print summary of file
    print "file name: " + file_name
    start_time.append(timestamp[0])
    print start_time[-1]
    print "selected messages: %s" % (sum(message_count.values()))
    print
    
    # print the message_count dictionary
    if verbose == True:
        print "message.name: counts"
        print
        for key, val in message_count.items():
            print "%s: %s" % (key, val)
        
    plt.plot(elapsed_time, distance)
    
plt.xlabel('elapsed time (minutes)')
plt.ylabel('distance (km)')
plt.title('Running')
plt.legend(start_time, loc='lower right')
plt.show()
