import pandas as pd
from fitparse import FitFile


def create_dataframe_from_fit_file(file_path, desired_message='record'):
    """
    Reads all the data of the desired_message type from the .fit file and returns a pandas DataFrame

    :param file_path : string
        The file path to read.
    :param desired_message : string
        The type of messages to read.

    :return df: pandas DataFrame
        Contain the data of the desired_message type read from of the .fit file.
    """

    df = pd.DataFrame()
    fit_file = FitFile(file_path)
    for im, message in enumerate(fit_file.get_messages(desired_message)):
            for message_data in message:
                df.loc[im, message_data.name.replace('_', ' ')] = message_data.value

    return df


def edit_database_from_records(index, database, records):
    """
    Modifies the variable database based on the information in records.

    :param index: pandas index
    :param database: pandas dataframe
    :param records: pandas dataframe
    :return:
    """

    database.loc[index, 'start time'] = records['timestamp'].dropna().iloc[0]
    database.loc[index, 'end time'] = records['timestamp'].dropna().iloc[-1]

    database.loc[index, 'max speed'] = records['speed'].max()
    # TODO: calculate other statistics like avg speed, avg heart rate, max heart rate, ...

    if len(records['position lat'].dropna()):
        database.loc[index, 'end position lat'] = records['position lat'].dropna().iloc[-1]
    if len(records['position long'].dropna()):
        database.loc[index, 'end position long'] = records['position long'].dropna().iloc[-1]
