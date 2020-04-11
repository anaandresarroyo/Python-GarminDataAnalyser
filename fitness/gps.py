import numpy as np


def calculate_distance(longitude, latitude, units_gps='semicircles', units_d='m',
                       mode='start', fixed_lon=1601994.0, fixed_lat=622913929.0):
    """Calculate the great circle distance between two points
    on the earth using the Haversine formula.

    Arguments:
    longitude : float pandas Series
        Longitude values of GPS coordinates, in units of units_gps
    latitude : float pandas Series
        Latitude values of GPS coordinates, in units of units_gps
    units_gps : string
        Units of longitude or latitude, e.g. 'semicircles' (default) or 'deg'
    units_d: string
        Units of the calculated distance, e.g. 'm' (default) or 'km'
    mode : string
        If 'start' calculate the distance between all points of the array and the first point.
        If 'previous' calculate the distance between all points of the array the previous point.
        If 'fixed' calculate the distance between all points of the array and a fixed point.
    fixed_lon: float
        Longitude value in units of units_gps to be used with mode='fixed'
    fixed_lat: float
        Latitude value in units of units_gps to be used with mode='fixed'

    Output:
    distance: float pandas Series
        Contains the calculated distance in units of units_d
    """

    if units_gps == 'semicircles':
        # Convert semicircles to degrees
        longitude = longitude*180/2**31
        latitude = latitude*180/2**31
    elif units_gps == 'deg':
        pass
    else:
        raise ValueError('Unable to recognise the units for the longitude and latitude.')

    origin_lon = np.empty(longitude.shape)
    origin_lat = np.empty(latitude.shape)

    if mode == 'start':
        origin_lon[:] = longitude[0]
        origin_lat[:] = latitude[0]

    elif mode == 'previous':
        origin_lon[0] = longitude[0]
        origin_lat[0] = latitude[0]

        origin_lon[1:] = longitude[0:-1]
        origin_lat[1:] = latitude[0:-1]

    elif mode == 'fixed':
        if units_gps == 'semicircles':
            fixed_lon = fixed_lon*180/2**31
            fixed_lat = fixed_lat*180/2**31

        origin_lon[:] = fixed_lon
        origin_lat[:] = fixed_lat

    else:
        raise ValueError('Unable to recognise the mode.')

    # Radius of the Earth in units of units_d
    if units_d == 'm':
        radius = 6371000
    elif units_d == 'km':
        radius = 6371
    else:
        raise ValueError('Unable to recognise the units for the distance.')

    delta_lon = np.radians(longitude-origin_lon)
    delta_lat = np.radians(latitude-origin_lat)
    # Haversine formula
    a = np.sin(delta_lat/2) * np.sin(delta_lat/2) + np.cos(np.radians(origin_lat)) \
        * np.cos(np.radians(latitude)) * np.sin(delta_lon/2) * np.sin(delta_lon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = radius * c  # Same units as radius
    # TODO: check the validity of the Haversine formula
    # https://en.wikipedia.org/wiki/Geographical_distance

    return distance
