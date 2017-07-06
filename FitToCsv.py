# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads many Garmin .fit file saves the desired data into many .csv files
"""
import os
from collections import Counter
from fitparse import FitFile
import pandas as pd

def FitToDataFrame(file_path, desired_message='record', verbose=True):
    """Reads all the data of the desired_message type
    from the .fit file and returns a pandas DataFrame 
        
    Arguments:
    file_paths : string
        The file path to read.
    desired_message : string (optional)
        The type of messages to read.
    verbose : bool (optional)
        If True (default), print progress    
    
    Output:
    df: pandas DataFrame
        Contain the data of the desired_message type read from of the fit file
        
    """
    
    if verbose:
        (directory_path,file_name) = os.path.split(file_path)
        print "Reading file: " + file_name
        print "Message type: " + desired_message + '\n'        
        
    fitfile = FitFile(file_path)    
    # Get all data messages that are of type desired_message
    for im, message in enumerate(fitfile.get_messages(desired_message)):
            data_dict = {}
            units_dict = {}
            for message_data in message:                        
                data_dict[message_data.name] = message_data.value
                units_dict[message_data.name] = message_data.units    
                # TODO: Figure out a way to incorporate the units into the DataFrame
                # TODO: Calculate the timezone/local time from the "activity" data
                
            # Build a pandas DataFrame with all the recorded data
            if im == 0:
                df = pd.DataFrame(data_dict, index=[im])       
            else:
                df.loc[im] = data_dict  
                               
    if verbose:
        print 'Done!\n'
    
    try:        
        return df
    except: 
        print "Could not return DataFrame."
        print "Check that the specified desired_message type exists."
        raise

def FitToCsv(path_read, path_save=False, desired_message='record', 
             subdirectories = True, verbose=True):
    """Reads all the data of the desired_message type
    from the .fit files and saves it to .csv files
        
    Arguments:
    path_read : string
        The directory/file path to read.
    path_save : string
        The directory path to save the data in.
        If path_save=True it will save the .csv file in the .fit file directory
    desired_message : list of string (optional)
        The type of messages to read.
    subdirectories : bool (optional)
        If True (default), place csv files in subdirectories according to their sport
    verbose : bool (optional)
        If True (default), print progress    
    
    Output:
    nothing
        
    """
    
    if os.path.isdir(path_read):
    # If path_read is a directory, find all files within it
        file_paths = []
        for file_name in os.listdir(path_read):
            if file_name.endswith('.fit'):
                file_paths.append(path_read + file_name)
    elif os.path.isfile(path_read):
    # If path_read is a single file
        file_paths = [path_read]
        
    if not path_save:
        path_save = os.path.dirname(path_read) + '/'
        
    # Initialise empty dictionary to count types of sports
    sport_counter = Counter()
    
    for ifn, file_path in enumerate(file_paths):
        if verbose:
            print "Reading file %s / %s\r" % (ifn + 1, len(file_paths))
        # Read session data to obtain the type of sport   
        fitfile = FitFile(file_path)    
        for message in fitfile.get_messages('sport'):
            sport = message.get_value('sport')
            
        # Update the sport_counter
        sport_counter[sport] += 1
            
        # Read data into pandas DataFrame
        df = FitToDataFrame(file_path, desired_message, verbose=False)   
        
        # Get the file_name of the current file_path
        file_name = os.path.basename(file_path)
        # Generate the file_name for the csv file
        file_name = file_name[:-4] + '_' + desired_message + '.csv'
        if subdirectories: # Place files in subdirectories according to their sport
            # Create the directory for the corresponding sport if it doesn't already exist
            if not os.path.exists(path_save + sport + '/'):
                os.makedirs(path_save + sport + '/')
            # Generate the file_path_save in the corresponding sport directory
            file_path_save = path_save + sport + '/' + file_name
        else: # Do not place files in subdirectories
            # Generate the file_path_save in the path_save directory
            if not os.path.exists(path_save):
                os.makedirs(path_save)            
            file_path_save = path_save + file_name
        if os.path.exists(file_path_save):
            # TODO: ask for user input to overwrite or not
            print "Overwriting file " + file_name
        # Save the Pandas DataFrame as a csv
        df.to_csv(file_path_save, sep=',', header=True, index=False)
        if verbose:
            print
        
    if verbose:
        # Print the sport_counter
        print "sport: counts ----------\n"
        for key, val in sport_counter.items():
            print "%s: %s" % (key, val)
        print '\nDone!\n'
    
if __name__ == '__main__':

    # Directory to read fit files from
    path_read = 'C:/Users/Ana Andres/Dropbox/Garmin/fit new/'
        
    # Directory to save csv files in
    path_save = 'C:/Users/Ana Andres/Dropbox/Garmin/csv/'
    
    # Convert .fit files to .csv files
    FitToCsv(path_read, path_save, desired_message='record', 
                 subdirectories = True, verbose=True)
