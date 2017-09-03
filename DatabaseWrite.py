# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Creates/updates Garmin database entries.
Inputs: .fit file, .csv file, or user input.
"""

import pandas as pd
from FitToCsv import FitToDataFrame
import os

if __name__ == '__main__':
    
    database_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Ana-test.csv'
    directory_path = 'C:/Users/Ana Andres/Documents/Garmin/fit test/'
    
    for ifn, file_name in enumerate(os.listdir(directory_path)):
        file_path = directory_path + file_name            
        print "Reading file %s / %s\r" % (ifn + 1, len(os.listdir(directory_path)))
    
        # Read data from the Garmin 'session' message type
        df = FitToDataFrame(file_path, desired_message='session', verbose=False)           
        # Add the file name to the dataframe
        df['file_name'] = os.path.basename(file_path)[:-4]
        # Rename the running cadence to share a column with the walking cadence
        df = df.rename(columns = {'avg_running_cadence':'avg_cadence',
                                  'max_running_cadence':'max_cadence'})

        if ifn == 0:
            # Initialise the database
            df_database = df
        else:
            # Add row to the database
            df_database = pd.concat([df_database,df])

    # TODO: use timestamp and local_timestamp from the activity data to save the time zone    
    
    # Use the start time as the row index
    df_database = df_database.set_index(df_database['start_time'])
    # Save the database to a .csv file
    df_database.to_csv(database_path, sep=',', header=True, index=True,
              columns=[
                       'file_name',
                       'sport',
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
                       ])
    print "Done!"