# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads many Garmin .fit file saves all the "record" message data into many CSV files
"""
import os
from fitparse import FitFile
import pandas as pd

def FitToDataFrame(file_paths,desired_messages=['record'],verbose=True):
    # TODO: make it for just one file so it outputs a single DataFrame and not dictionary
    # TODO: make it for just one desired_messages
    """Reads all the desired_messages from the .fit files and 
    generates a dictionary of Pandas DataFrame 
        
    Arguments:
    file_paths : list of strings
        The file paths to read. If single string converto to list.
    desired_messages : list of strings (optional)
        The types of messages to read. If single string converto to list.
        If the list list has more than 1 element choose only the first one.
    verbose : bool (optional)
        If True (default), print progress    
    
    Output:
    data_pd_dict: dictionary
        keys: strings
            File name without extension and including desired_message
        values: Pandas DataFrames 
            Contain the data read from the desired_messages of the file
    """

    if type(file_paths) is str:
        file_paths = [file_paths]
    if type(desired_messages) is str:
        desired_messages = [desired_messages]
    if len(desired_messages) > 1:
        desired_messages = desired_messages[0]
        print "WARNING!!! Only the first element of desired_messages was used"
        print

    if verbose:
        print "desired_messages = " + desired_messages[0]
        print 
    
    data_pd_dict = {}
    for ifn, file_path in enumerate(file_paths):
        (folder_path,file_name) = os.path.split(file_path)
        dict_key = file_name.replace('.fit','_' + desired_messages[0])   
        if verbose:
            # print summary of file
            print "Reading file %s / %s\r" % (ifn + 1, len(file_paths))
            print file_name
            print
            
        fitfile = FitFile(file_path)    
        # Get all data messages that are of type desired_messages
        for im, message in enumerate(fitfile.get_messages(desired_messages)):
#            if message.name == 'record':
                data_dict = {}
                units_dict = {}
                for message_data in message:                        
                    data_dict[message_data.name] = message_data.value
                    units_dict[message_data.name] = message_data.units    
                    #TODO: Figure out a way to incorporate the units into the DataFrame
                    
                # Build a Pandas DataFrame with all the recorded data
                if im == 0:
                    data_pd = pd.DataFrame(data_dict, index=[im])                
                else:
                    data_pd.loc[im] = data_dict                             
        
        data_pd_dict[dict_key] = data_pd
        #TODO: implement something to deal with duplicate file names
    
    if verbose:
        print 'Done!'
        print
    return data_pd_dict
    
if __name__ == '__main__':

    # select files to read    
    folder_path_read = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/fit new/'
    file_paths = []
    for file_name in os.listdir(folder_path_read):
        file_paths.append(folder_path_read + file_name)
        
    # select where to save the csv files
    # the files will be sorted into folders according to their sport
    folder_path_save = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Garmin/csv/'
    
    # initialise empty dictionary to count types of sports
    sport_count = {}
    
    for ifn, file_path in enumerate(file_paths):
        print "Reading file %s / %s\r" % (ifn + 1, len(file_paths))
        # read session data to obtain the type of sport        
        fitfile = FitFile(file_path)    
        for message in fitfile.get_messages('sport'):
            sport = message.get_value('sport')
            print 'sport = ' + sport
            
        if sport in sport_count.keys(): # TODO: sport_count (eliminate .keys())
            # TODO: check out python counter data type
            # if the sport is in sport_count dictionary, add 1
            sport_count[sport] = sport_count[sport] + 1        
        else:
            # else add the message to message_count dictionary, set the value to 1
            sport_count[sport] = 1
            
        # read record data into Pandas DataFrame
        data_pd_dict = FitToDataFrame(file_path,desired_messages='record',verbose=False)   
        
        for key, val in data_pd_dict.items():
            # save the Pandas DataFrame in the corresponding sport folder
            file_path = folder_path_save + sport + '/' + key + '.csv'
            # TODO: create the folder if it doesn't already exist
            val.to_csv(file_path, sep=',', header=True, index=False)
            # TODO: implement a safety check not to overwrite existing files
            
        print
        
    print 'Done!\n'
    
    # print the sport_count dictionary
    print "sport: counts ----------\n"
    for key, val in sport_count.items():
        print "%s: %s" % (key, val)

    
