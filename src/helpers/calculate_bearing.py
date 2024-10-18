"""Method to calculate the bearing between two geographic coordinates."""
import math


def calculate_bearing(location_1, location_2):
    """
    Calculate the bearing between two geographic coordinates.

    Parameters
    ----------
    location_1 : tuple of float
        The latitude and longitude of the first location in decimal degrees (lat1, lon1).
    location_2 : tuple of float
        The latitude and longitude of the second location in decimal degrees (lat2, lon2).

    Returns
    -------
    float
        The bearing from the first location to the second location in degrees, measured clockwise from north.
    """
    latitude_1, longitude_1 = location_1
    latitude_2, longitude_2 = location_2

    latitude_1 = math.radians(latitude_1)
    longitude_1 = math.radians(longitude_1)
    latitude_2 = math.radians(latitude_2)
    longitude_2 = math.radians(longitude_2)

    delta_longitude = longitude_2 - longitude_1

    x_component = math.sin(delta_longitude) * math.cos(latitude_2)
    y_component = math.cos(latitude_1) * math.sin(latitude_2) - math.sin(latitude_1) * math.cos(latitude_2) * math.cos(delta_longitude)

    initial_bearing_radians = math.atan2(x_component, y_component)

    initial_bearing_degrees = math.degrees(initial_bearing_radians)
    bearing = (initial_bearing_degrees + 360) % 360

    return bearing
