import pandas as pd
import os
import configparser

from fitness.time import auto_crop_records
from fitparser import tools as fit_tools

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('user_config.ini')

    # TODO: ask the user for the directories
    database_path = os.path.join(config['DIRECTORIES']['database'],
                                 config['FILE NAMES']['database'])
    fit_path_read = os.path.join(config['DIRECTORIES']['fit files'])
    csv_path_save = os.path.join(config['DIRECTORIES']['csv files'])
    overwrite_csv = os.path.join(config['CSV OPTIONS']['overwrite existing files'])
    overwrite_values = os.path.join(config['DATABASE OPTIONS']['overwrite existing values'])
        
    if os.path.exists(database_path):
        print('The database already exists.')
        print('Reading the database.')
        df_database = pd.read_csv(database_path)
        df_database['file name'] = df_database['file name'].astype(str)
        df_database.set_index('file name', inplace=True)
    else:
        print('The database does not exist yet.')
        print('Creating and empty database...')
        df_database = pd.DataFrame()
        df_database.index.name = 'file name'

    fit_file_names = [f for f in os.listdir(fit_path_read) if '.fit' in f]
    
    for ifn, fit_file_name in enumerate(fit_file_names):
        print("\nFile %s / %s: %s" % (ifn + 1, len(fit_file_names), fit_file_name))

        df_records = pd.DataFrame()

        fit_file_path = fit_path_read + fit_file_name
        index = fit_file_name.replace('.fit', '')
        csv_file_name = fit_file_name.replace('.fit', '_record.csv')
        csv_file_path = os.path.join(csv_path_save, csv_file_name)

        if index in df_database.index.astype(str):
            print('This file is already in the database.')
            if overwrite_values.lower() == 'no':
                print('The database will not be updated.')
                edit_database = False
            else:
                print('The values in the database will be updated.')
                edit_database = True
        else:
            print('This file is not in the database yet.')
            edit_database = True


        if os.path.exists(csv_file_path):
            print('The csv records file already exists.')
            if overwrite_csv.lower() == 'yes':
                print("The csv records file will be overwritten.")
                save_csv = True
            else:
                print('The csv records file will not be overwritten.')
                save_csv = False
        else:
            print('The csv records file does not exist yet.')
            save_csv = True

        if save_csv:
            if df_records.empty:
                print('Reading the records from the fit file...')
                df_records = fit_tools.create_dataframe_from_fit_file(fit_file_path, 'record')
                df_records = auto_crop_records(df_records)
            print('Saving the csv records file...')
            df_records.to_csv(csv_file_path, sep=',', header=True, index=False)

        if edit_database:
            if df_records.empty:
                print('Reading the records from the fit file...')
                df_records = fit_tools.create_dataframe_from_fit_file(fit_file_path, 'record')
                df_records = auto_crop_records(df_records)

            print("Editing the database...")
            # Read data from the Garmin 'session' message type
            df_session = fit_tools.create_dataframe_from_fit_file(fit_file_path, 'session')
            # Rename the running cadence to share a column with the walking cadence
            df_session = df_session.rename(columns={'avg running cadence': 'avg cadence',
                                                    'max running cadence': 'max cadence'})
            for column in df_session.columns:
                df_database.loc[index, column] = df_session[column][0]

            sport = df_database.loc[index, 'sport']
            # TODO: automatically determine the sport based on avg speed, cadence, heart rate...

            gear = None
            if sport in config.options('DEFAULT GEAR'):
                gear = config['DEFAULT GEAR'][sport]
            df_database.loc[index, 'gear'] = gear

            activity = None
            if sport in config.options('DEFAULT ACTIVITY TYPE'):
                activity = config['DEFAULT ACTIVITY TYPE'][sport]
            df_database.loc[index, 'activity'] = activity

            df_database.loc[index, 'comments'] = ''

            fit_tools.edit_database_from_records(index, df_database, df_records)

            df_activity = fit_tools.create_dataframe_from_fit_file(fit_file_path, 'activity')
            if 'local timestamp' in df_activity.columns:
                df_database.loc[index, 'timezone'] = df_activity['local timestamp'][0] - df_activity['timestamp'][0]
            else:
                df_database.loc[index, 'timezone'] = None
                           
        # Do not save "unknown" columns
        known_columns = []
        for column in df_database.columns:
            if "unknown" not in column:
                known_columns.append(column)

        # Get the list of desired columns from the configuration file
        desired_columns = list(filter(None, [x.strip() for x in
                                             config['DATABASE OPTIONS']['desired columns'].splitlines()]))

        # Find intersection between desired_columns and known columns in the database
        # Order intersection based on the order of desired_columns
        saving_columns = sorted(set(desired_columns) & set(known_columns), key=desired_columns.index)

        df_database.sort_index(inplace=True)

        print('Saving the database...')
        df_database.to_csv(database_path, sep=',', header=True, index=True, columns=saving_columns)
    
    print("\nThe end!")

    # TODO: use logging instead of printing
