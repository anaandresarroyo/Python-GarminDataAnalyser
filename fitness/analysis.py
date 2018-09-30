import pandas as pd

from fitness.gps import calculate_distance


def convert_units(config, df, dataframe_units, desired_units, to_SI=False):
    # if to_SI = False: convert from SI_units to dataframe_units
    # if to_SI = True: convert from dataframe_units to SI_units

    if to_SI:
        factor = -1.
    else:
        factor = 1.

    # TODO: automate this more
    for column_name in df.columns:
        for quantity in ['elapsed time', 'position', 'distance', 'speed']:
            if quantity in column_name:
                dataframe_units[column_name] = desired_units[quantity]
                df[column_name] = df[column_name] * (
                        eval(config['%s UNIT FACTORS' % quantity.upper()][desired_units[quantity]]) ** factor)
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


def location_mask(df_locations, current_units, config, df, when, selected_options):
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
                                          fixed_lon=lon_deg * config['POSITION UNIT FACTORS'][
                                              current_units['position']] / 0.00000008381903171539306640625,
                                          fixed_lat=lat_deg * config['POSITION UNIT FACTORS'][
                                              current_units['position']] / 0.00000008381903171539306640625,
                                          # fixed_lon=lon_deg * settings.unit_factors['position'][
                                          #     current_units['position']] / 0.00000008381903171539306640625,
                                          # fixed_lat=lat_deg * settings.unit_factors['position'][
                                          #     current_units['position']] / 0.00000008381903171539306640625,
                                          )
            option_mask = distance.abs() <= radius
            mask = mask | option_mask
    return mask
