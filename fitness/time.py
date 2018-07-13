import numpy as np
import pandas as pd


def calculate_elapsed_time(timestamp, units_t='sec', mode='start', fixed_timestamp=None):
    """Calculate the elapsed time from a timestamp pandas Series.

    Arguments:
    timestamp : timestamp pandas Series
        Timestamp values
    units_d: string
        Units of the calculated time, e.g. 'sec' (default), 'min', or 'h'
    mode : string
        If 'start' calculate the elapsed time between all points of the array and the first point.
        If 'previous' calculate the elapsed time between all points of the array the previous point.
        If 'fixed' calculate the elapsed time between all points of the array the fixed_timestamp.
    fixed_timestamp : one timestamp value
        Fixed timestamp value to be used as a reference to calculate the elapsed time.
    Output:
    elapsed_time: float pandas Series
        Contains the calculated elapsed time in units of units_t
    """

    # The Garmin Forerunner 35 takes data every 1 second

    origin_time = np.empty(timestamp.shape, dtype=type(timestamp))
    if mode == 'start':
        origin_time[:] = timestamp[0]

    elif mode == 'previous':
        origin_time[0] = timestamp[0]
        for i, time in enumerate(timestamp[0:-1]):
            origin_time[i + 1] = time
            # TODO: change to origin_time.append(time)
    elif mode == 'fixed':
        origin_time[:] = fixed_timestamp

    else:
        raise ValueError('Unable to recognise the mode.')

    # TODO: whey does origin_time have to be converted to datetime?
    timedelta = timestamp - pd.to_datetime(origin_time)
    elapsed_time = timedelta.astype('timedelta64[s]')  # in seconds

    if units_t == 's':
        pass
    elif units_t == 'sec':
        pass
    elif units_t == 'min':
        # Convert seconds to minutes
        elapsed_time = elapsed_time / 60
    elif units_t == 'h':
        # Convert seconds to hours
        elapsed_time = elapsed_time / 60 / 60
    else:
        raise ValueError('Unable to recognise the units for the time.')
    return elapsed_time


def select_times(StartTimeDoubleSpinBox, EndTimeDoubleSpinBox, df):
    # TODO: use pandas time indexing
    start_time = StartTimeDoubleSpinBox.value()
    end_time = EndTimeDoubleSpinBox.value()
    mask_start = df['elapsed_time'] >= start_time
    mask_end = df['elapsed_time'] <= end_time
    return df.loc[mask_start & mask_end]
