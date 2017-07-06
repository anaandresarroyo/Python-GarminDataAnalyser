# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a Garmin .fit file and displays the messages and their type
"""
import os
from fitparse import FitFile
from collections import Counter

def FitPrinter(file_path, desired_messages=range(250), 
               verbose_message=True, verbose_summary=True):
    """TODO: Add doc string """
    
    # Open .fit file    
    fitfile = FitFile(file_path)
    
    # Initialise empty counter to count types of messages
    message_counter = Counter()
       
    # Get all data messages that are of type desired_messages
    for im, message in enumerate(fitfile.get_messages(desired_messages)):
        # Update the message_counter
        message_counter[message.name] += 1
        
        if verbose_message:
            # Print the message number and name
            print " - %s: %s: %s ----------" % (im, message.mesg_num, message.name)
            
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
            
    if verbose_summary:
        # print summary of file
        print "file name: " + os.path.basename(file_path)
        print "selected messages: %s\n" % (sum(message_counter.values()))
    
        # print the message_counter
        print "message.name: counts --------------------\n"
        for key, val in message_counter.items():
            print "%s: %s" % (key, val)
        print
    
    
if __name__ == '__main__':
    
    file_path = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/fit new/1837541844.fit'
    # TODO: ask for user input to select the file_path
    
    # Select which messages to read
    desired_messages = range(250) # all message with codes up to 300    
    FitPrinter(file_path, desired_messages, 
               verbose_message=False, verbose_summary=True)
    
    desired_messages = input('Type desired message info. Enclose in quotation marks and choose from the options listed above.\n\n')
    print

    FitPrinter(file_path, desired_messages, 
               verbose_message=True, verbose_summary=False)