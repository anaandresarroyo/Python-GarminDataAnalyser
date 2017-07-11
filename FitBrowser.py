# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a Garmin .fit file and prints its information
"""
import os
from fitparse import FitFile
from collections import Counter
import tkFileDialog
import Tkinter as tk

def FitPrinter(file_path, desired_messages=range(250), 
               verbose_message=False, verbose_summary=True):
    """Reads all the data of the desired_messages types
    from the .fit file and prints it on the console
        
    Arguments:
    file_paths : string
        The file path to read.
    desired_messages : string / list of strings / list of numbers (optional)
        The type of messages to read.
    verbose_message : bool (optional)
        If True (default), print data contained within each message
    verbose_summary : bool (optional)
        If True (default), print summary of message types
    
    Output:
    none
        
    """
    
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
                    print " * %s: %s %s" % (message_data.name, message_data.value, message_data.units)
                else:
                    print " * %s: %s" % (message_data.name, message_data.value)
            print
            
    if verbose_summary:
        # Print summary of file
        print "file name: " + os.path.basename(file_path)
        print "selected messages: %s\n" % (sum(message_counter.values()))
    
        # Print the message_counter values
        print "message.name: counts --------------------\n"
        for key, val in message_counter.items():
            print "%s: %s" % (key, val)
        print
    
    
    
if __name__ == '__main__':
    
    # Hide background Tkinter window
    root = tk.Tk()
    root.withdraw()
    
    # Choose file
    file_path = tkFileDialog.askopenfilename(title='Choose .fit file.', 
                                             filetypes=[('FIT','*.fit'), ('all','*.*')])
    
    # Print file summary
    FitPrinter(file_path)
               
    desired_messages = ''
    while desired_messages!='exit':
        print "Write the type of message you would like to see more info from. " \
              "(Choose from the options listed in the message counter.) " \
              "(Type 'exit' to exit the while loop.)\n"
        desired_messages = raw_input()
        print
        
        # Print message data from desired_messages types
        FitPrinter(file_path, desired_messages, 
                   verbose_message=True, verbose_summary=False)
    
    print 'THE END!'