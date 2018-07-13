import pandas as pd

from fitness.gps import calculate_distance


def convert_units(settings, df, dataframe_units, desired_units, to_SI=False):
    # if to_SI = False: convert from SI_units to dataframe_units
    # if to_SI = True: convert from dataframe_units to SI_units
    if to_SI:
        factor = -1.
    else:
        factor = 1.

    # TODO: automate this more
    for column_name in df.columns:
        if 'elapsed_time' in column_name:
            dataframe_units[column_name] = desired_units['elapsed_time']
            df[column_name] = df[column_name] * (
                    settings.unit_factors['elapsed_time'][desired_units['elapsed_time']] ** factor)
        if 'position' in column_name:
            dataframe_units[column_name] = desired_units['position']
            df[column_name] = df[column_name] * (settings.unit_factors['position'][desired_units['position']] ** factor)
        if 'distance' in column_name:
            dataframe_units[column_name] = desired_units['distance']
            df[column_name] = df[column_name] * (settings.unit_factors['distance'][desired_units['distance']] ** factor)
        if 'speed' in column_name:
            dataframe_units[column_name] = desired_units['speed']
            if 'min/' in desired_units['speed']:
                if to_SI:
                    df[column_name] = 60 / df[column_name]
                    df[column_name] = df[column_name] * (
                            settings.unit_factors['speed'][desired_units['speed']] ** factor)
                else:
                    df[column_name] = df[column_name] * (
                            settings.unit_factors['speed'][desired_units['speed']] ** factor)
                    df[column_name] = 60 / df[column_name]
            else:
                df[column_name] = df[column_name] * (settings.unit_factors['speed'][desired_units['speed']] ** factor)
    return df, dataframe_units


def select_dates(StartDateEdit, EndDateEdit, column_date_local, df):
    start_date = StartDateEdit.date().toPyDate()
    end_date = EndDateEdit.date().toPyDate()
    df_copy = df.copy()
    df_copy.set_index(column_date_local, inplace=True)
    df_selected = df_copy.loc[str(start_date): str(end_date + pd.DateOffset(1))]
    df_selected.reset_index(inplace=True)
    return df_selected


def generate_mask(df, column, selected_options):
    mask = [False] * len(df)
    for option in selected_options:
        option_mask = df[column] == option
        mask = mask | option_mask
    return mask
    # TODO: what if some rows are empy in this column?
    # TODO: allow several gear for the same activity - maybe?


def location_mask(df_locations, current_units, settings, df, when, selected_options):
    # TODO: fix error with weird characters such as "ñ" in "Logroño"
    if 'any' in selected_options:
        mask = True
    else:
        mask = [False] * len(df)
        for option in selected_options:
            radius = df_locations.loc[df_locations['name'] == option, 'radius'].values[0]
            lon_deg = df_locations.loc[df_locations['name'] == option, 'position_long']
            lat_deg = df_locations.loc[df_locations['name'] == option, 'position_lat']
            distance = calculate_distance(df[when + '_position_long'], df[when + '_position_lat'],
                                          units_gps=current_units['position'], units_d='m', mode='fixed',
                                          fixed_lon=lon_deg * settings.unit_factors['position'][
                                              current_units['position']] / 0.00000008381903171539306640625,
                                          fixed_lat=lat_deg * settings.unit_factors['position'][
                                              current_units['position']] / 0.00000008381903171539306640625,
                                          )
            option_mask = distance.abs() <= radius
            mask = mask | option_mask
    return mask
