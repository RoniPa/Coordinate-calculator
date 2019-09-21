import math
import csv
from collections import namedtuple


def hypotenuse(x, y):
    """Calculate hypotenuse for coordinates."""
    return math.sqrt(x*x + y*y)


def degtorad(deg):
    """Convert given decimal degree to radians."""
    return deg * math.pi / 180


def radtodeg(rad):
    """Convert given radian to decimal degrees."""
    return rad * 180 / math.pi


def to_cartesian(lat, lon):
    """Converts degree coordinate to cartesian (x, y, z) coordinates."""
    CartesianPoint = namedtuple('CartesianPoint', 'x y z')

    # Degrees to radians
    lat = degtorad(lat)
    lon = degtorad(lon)

    # Calculate coordinates
    x = math.cos(lat) * math.cos(lon)
    y = math.cos(lat) * math.sin(lon)
    z = math.sin(lat)

    return CartesianPoint(x, y, z)


def geographic_midpoint(coords):
    """ Calculate the geographic midpoint
        for a list of decimal degree coordinates.
    """
    # deg to cartesian coords
    coords = [to_cartesian(*coord) for coord in coords]

    # Not weighted, use 1 for all
    weight = 1
    weight_sum = len(coords) * weight

    center = [0, 0, 0]
    for c in coords:
        center[0] += c.x * weight
        center[1] += c.y * weight
        center[2] += c.z * weight

    center = [val / weight_sum for val in center]
    lon_radians = math.atan2(center[1], center[0])
    lat_radians = math.atan2(center[2], hypotenuse(center[0], center[1]))
    lon = radtodeg(lon_radians)
    lat = radtodeg(lat_radians)

    return lat, lon


def haversine(coord1, coord2, R):
    """ Use haversine formula to calculate distance between two coordinates.

        coord1  -- first coordinate in decimal degrees
        coord2  -- second coordinate in decimal degrees
        R       -- (Earth) radius, e.g., 6371000
    """

    lat1 = degtorad(coord1[0])
    lon1 = degtorad(coord1[1])

    lat2 = degtorad(coord2[0])
    lon2 = degtorad(coord2[1])

    a = math.pow(math.sin((lat1-lat2) / 2), 2) + \
        math.cos(lat1) * math.cos(lat2) * \
        math.pow(math.sin((lon1-lon2) / 2), 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


if __name__ == '__main__':
    # earth radius, kilometres
    R = 6371

    coords = []
    with open('coords.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        coords = [[float(x) for x in row] for row in csv_reader]

    midpoint = geographic_midpoint(coords)
    max_dist = max([haversine(midpoint, coord, R) for coord in coords])

    print('Center of coordinates is {}, {}'.format(midpoint[0], midpoint[1]))
    print('Furthest coordinate is {0:.2f} km from midpoint.'.format(max_dist))
