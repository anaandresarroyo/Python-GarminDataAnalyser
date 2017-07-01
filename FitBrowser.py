# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a Garmin .fit file and displays the messages and their type
"""

from fitparse import FitFile

folder_name = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/fit all/'

#file_name = '1799291774.fit' # squash
#file_name = '1804849333.fit' # running
#file_name = '1806473488.fit' # cycling
#file_name = '1807619481.fit' # walking
#file_name = '12378630852.fit' # exported from day view
#file_name = '12378631774.fit' # exported from day view

#file_names = ['1741229575.fit',
#              '1768541987.fit',
#              '1776168778.fit',
#              '1791583142.fit',
#              '1795613506.fit',
#              '1804849333.fit',
#              ] # running

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
#              '1821550522.fit', # trek
              '1823366347.fit',
              ] # cycling
           

# select which messages to read
#desired_messages = range(300) # all message with codes up to 300
desired_messages = [
                    'session',
#                    'activity',
#                    'sport',
#                    'lap',
#                    'event',
#                    'file_id',
                    'record',
                    ]


for ifn, file_name in enumerate(file_names):
    fitfile = FitFile(folder_name + file_name)
    
    verbose = True;
    
    # initialise empty dictionary to count types of messages
    message_count = {}
       
    # Get all data messages that are of type desired_messages
    for im, message in enumerate(fitfile.get_messages(desired_messages)):
           
        if message.name in message_count.keys():
            # if the message is in message_count dictionary, add 1
            message_count[message.name] = message_count[message.name] + 1        
        else:
            # else add the message to message_count dictionary, set the value to 1
            message_count[message.name] = 1
            
        if message.name == 'record':
            if message_count[message.name] == 1:
                # only print data of one 'record' message because there tend to be too many
                verbose = True
            else:
                verbose = False
        else:
            verbose = True
        
        if verbose == True:
            # Print the message number and name
            print " - %s: %s: %s ------------------------------" % (im, message.mesg_num, message.name)
            
            # Go through all the data entries in this message
            for message_data in message:        
                # Print the messages name and value (and units if it has any)
                if message_data.units:
                    print " * %s: %s %s" % (
                                            message_data.name, 
                                            message_data.value, 
                                            message_data.units,
                                            )
                else:
                    print " * %s: %s" % (message_data.name, message_data.value)
            print
            

    verbose = True
    if verbose == True:
        # print summary of file
        print "%s / %s\r" % (ifn+1, len(file_names))
        print "file name: " + file_name
        print "selected messages: %s" % (sum(message_count.values()))
        print
    
    verbose = True
    if verbose == True:
        # print the message_count dictionary
        print "message.name: counts ------------------------------"
        print
        for key, val in message_count.items():
            print "%s: %s" % (key, val)
    
