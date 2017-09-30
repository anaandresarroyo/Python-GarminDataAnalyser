# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Creates/updates Garmin database entries.
Inputs: .fit file, .csv file, or user input.
"""

import pandas as pd
from FitToCsv import FitToDataFrame
import os

current_gear = {'cycling':'Trek FX2 Hybrid Bike',
                'running':'Nike Black Sneakers',
                'training':'Nike Blue Sneakers',
                'walking':'Decathlon Hiking Shoes',
                }
activity_type = {'cycling':'Transportation',
                'running':'Fitness',
                'training':'Fitness',
                'walking':'Recreation',
                }

if __name__ == '__main__':
    
    # TODO: ask the user for the directories
    existing_database_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Ana-170930.csv'
    new_database_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Ana-170930.csv'
    directory_path = 'C:/Users/Ana Andres/Documents/Garmin/fit all/'
    
#    df_database = pd.read_csv(existing_database_path)
    
    for ifn, file_name in enumerate(os.listdir(directory_path)):   
        
        if 'df_database' in locals():
            # Check wether this file is already in the database
            mask = df_database['file_name'] == int(file_name[:-4])
            mask = mask.any()
        else:
            mask = False
            
        if mask:
            print "File %s / %s already in database. Skipped." % (ifn + 1, len(os.listdir(directory_path)))
            # If the file is in the database we will skip in because it is likely
            # that it's values have been modified to correct for errors such as
            # forgetting to turn the GPS off at the end of the activity
        else:
            file_path = directory_path + file_name            
            print "Reading file %s / %s\r" % (ifn + 1, len(os.listdir(directory_path)))
        
            # Read data from the Garmin 'session' message type
            df = FitToDataFrame(file_path, desired_message='session', verbose=False)           
            # Rename the running cadence to share a column with the walking cadence
            df = df.rename(columns = {'avg_running_cadence':'avg_cadence',
                                      'max_running_cadence':'max_cadence'})
            # Add the file name to the dataframe
            df['file_name'] = os.path.basename(file_path)[:-4]
            # Add the gear used, it will need to be edited later
            df['gear'] = current_gear[df.get_value(0,'sport')]
            # Add the type of activity, it will need to be edited later
            df['activity'] = activity_type[df.get_value(0,'sport')]
            # Add the timezone offset in hours
            # TODO: this needs checking
            df_activity = FitToDataFrame(file_path, desired_message='activity', verbose=False)           
            df['timezone'] = df_activity.loc[0,'local_timestamp']-df_activity.loc[0,'timestamp']            
    
            if 'df_database' in locals():
                # Add row to the database
                df_database = pd.concat([df_database,df])
            else:
                # Initialise the database
                df_database = df
    
    # Use the start time as the row index
    df_database = df_database.set_index(df_database['start_time'])
    # Save the database to a .csv file
    
    # TODO: sort dataframe by file name
    # TODO: ask the user wether to overwrite the file if it already exists
    
    df_database.to_csv(new_database_path, sep=',', header=True, index=True,
              columns=[
                       'file_name',
                       'sport',
                       'activity_type',
                       'avg_heart_rate',
                       'max_heart_rate',
                       'avg_cadence',
                       'max_cadence',
                       'start_position_lat',
                       'start_position_long',
                       'avg_speed',
                       'total_distance',
                       'total_elapsed_time',
                       'total_calories',
                       'timezone',
                       'gear',
                       ])
    print "Done!"