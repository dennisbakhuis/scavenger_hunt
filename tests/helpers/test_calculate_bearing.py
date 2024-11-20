"""Tests for the calculate_bearing function."""

import math

from helpers import calculate_bearing


def test_calculate_bearing_north():
    """Test bearing calculation for two points directly north."""
    location_1 = (0.0, 0.0)  # Equator and Prime Meridian
    location_2 = (1.0, 0.0)  # 1 degree north, same longitude
    assert math.isclose(calculate_bearing(location_1, location_2), 0.0, abs_tol=1e-1)


def test_calculate_bearing_east():
    """Test bearing calculation for two points directly east."""
    location_1 = (0.0, 0.0)  # Equator and Prime Meridian
    location_2 = (0.0, 1.0)  # 1 degree east, same latitude
    assert math.isclose(calculate_bearing(location_1, location_2), 90.0, abs_tol=1e-1)


def test_calculate_bearing_south():
    """Test bearing calculation for two points directly south."""
    location_1 = (1.0, 0.0)  # 1 degree north of the Equator
    location_2 = (0.0, 0.0)  # Equator and Prime Meridian
    assert math.isclose(calculate_bearing(location_1, location_2), 180.0, abs_tol=1e-1)


def test_calculate_bearing_west():
    """Test bearing calculation for two points directly west."""
    location_1 = (0.0, 1.0)  # Equator, 1 degree east
    location_2 = (0.0, 0.0)  # Equator and Prime Meridian
    assert math.isclose(calculate_bearing(location_1, location_2), 270.0, abs_tol=1e-1)


def test_calculate_bearing_northeast():
    """Test bearing calculation for two points northeast."""
    location_1 = (0.0, 0.0)  # Equator and Prime Meridian
    location_2 = (1.0, 1.0)  # 1 degree north, 1 degree east
    assert math.isclose(calculate_bearing(location_1, location_2), 45.0, abs_tol=1e-1)


def test_calculate_bearing_random():
    """Test bearing calculation between Enschede and Arnhem."""
    location_1 = (52.2215, 6.8937)  # Enschede, Netherlands
    location_2 = (51.9851, 5.8987)  # Arnhem, Netherlands
    expected_bearing = 249.2  # Approximate expected bearing from Enschede to Arnhem

    assert math.isclose(calculate_bearing(location_1, location_2), expected_bearing, abs_tol=1.0)
