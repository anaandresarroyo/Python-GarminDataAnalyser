# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Creates/updates Garmin database entries.
"""

import pandas as pd
import os
from fitparse import FitFile

current_gear = {'cycling':'Trek FX2 Hybrid Bike',
                'running':'Nike Black Sneakers',
                'training':'Nike Blue Sneakers',
                'walking':'Decathlon Hiking',
                }
activity_type = {'cycling':'Transportation',
                'running':'Training',
                'training':'Fitness',
                'walking':'Recreation',
                }
                
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
        Contain the data of the desired_message type read from of the .fit file
        
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

if __name__ == '__main__':
    # TODO: ask the user for the directories
    existing_database_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Ana-171027.csv'
    new_database_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Ana-171029.csv'
    
    # Directory to read .fit files from
    fit_path_read = 'C:/Users/Ana Andres/Documents/Garmin/fit new/'        
    # Directory to save .csv files in
    fit_path_save = 'C:/Users/Ana Andres/Documents/Garmin/csv/'
        
    df_database = pd.read_csv(existing_database_path)
    
    for ifn, file_name in enumerate(os.listdir(fit_path_read)):   
        
        if 'df_database' in locals():
            # Check wether this file is already in the database
            mask = df_database['file_name'] == int(file_name[:-4])
            mask = mask.any()
        else:
            mask = False

        print "\r%s / %s: %s\r" % (ifn + 1, len(os.listdir(fit_path_read)), file_name)            
        if mask:
            print "Activity already in database!"
            # If the file is in the database we will skip in because it is likely
            # that it's values have been modified to correct for errors such as
            # forgetting to turn the GPS off at the end of the activity
        else:
            print "Adding activity to database..."
            file_path = fit_path_read + file_name                        
            
            # Read data from the Garmin 'record' message type
            df_record = FitToDataFrame(file_path, 'record', verbose=False)   
        
            # Save the Pandas DataFrame as a .csv file        
            file_path_save = fit_path_save + file_name[:-4] + '_record.csv'            
            overwrite = False
            save = True
            if os.path.exists(file_path_save):
                # TODO: ask for user input to overwrite or not
                if overwrite:
                    print "Overwriting file " + file_name
                else:
                    print 'Record .csv file already exists!'
                    save = False
            if save:
                df_record.to_csv(file_path_save, sep=',', header=True, index=False)
        
            # Read data from the Garmin 'session' message type
            df_session = FitToDataFrame(file_path, desired_message='session', verbose=False)           
            # Rename the running cadence to share a column with the walking cadence
            df_session = df_session.rename(columns = {'avg_running_cadence':'avg_cadence',
                                      'max_running_cadence':'max_cadence'})
            # Add the file name to the dataframe
            df_session['file_name'] = os.path.basename(file_path)[:-4]
            # Add the gear used, it will need to be edited later
            df_session['gear'] = current_gear[df_session.get_value(0,'sport')]
            # Add the type of activity, it will need to be edited later
            df_session['activity'] = activity_type[df_session.get_value(0,'sport')]
            # Add comments columns to be filled later
            df_session['comments'] = ''
            # Add end position information
            try:
                df_session['end_position_lat'] = df_record['position_lat'].dropna().iloc[-1]
                df_session['end_position_long'] = df_record['position_long'].dropna().iloc[-1]
            except:
                print "No GPS data."
            # Add the timezone offset in hours
            df_activity = FitToDataFrame(file_path, desired_message='activity', verbose=False)           
            df_session['timezone'] = df_activity.loc[0,'local_timestamp']-df_activity.loc[0,'timestamp']            
    
            if 'df_database' in locals():
                # Add row to the database
                df_database = pd.concat([df_database,df_session])
            else:
                # Initialise the database
                df_database = df_session
    
    
    
    # TODO: sort dataframe by file name
    # TODO: ask the user wether to overwrite the file if it already exists
    # TODO: add end location information
    # TODO: use global or local start_time?
    
    # Sort dataframe by file_name
#    print "\nSorting database by start time..."
#    df_database.sort_values(by='start_time', inplace=True)
    
    # Use the start time as the row index
    df_database = df_database.set_index(df_database['start_time'])   
    
    # Save the database to a .csv file
    print "\nSaving database..."
    df_database.to_csv(new_database_path, sep=',', header=True, index=True,
                      columns=[                               
                               'sport',
                               'activity',
                               'gear',
                               'comments',
                               'file_name',
                               'avg_speed',
                               'total_distance',
                               'total_elapsed_time',
                               'avg_heart_rate',
                               'max_heart_rate',
                               'avg_cadence',
                               'max_cadence',
                               'start_position_long',
                               'start_position_lat',                       
                               'end_position_long',
                               'end_position_lat',                       
                               'total_calories',
                               'timezone',                       
                               ])
    print "Done!"