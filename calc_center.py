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
    """Converts radian coordinate to cartesian (x, y, z) coordinates."""
    CartesianPoint = namedtuple('CartesianPoint', 'x y z')

    # Calculate coordinates
    x = math.cos(lat) * math.cos(lon)
    y = math.cos(lat) * math.sin(lon)
    z = math.sin(lat)

    return CartesianPoint(x, y, z)


def geographic_midpoint(coords):
    """ Calculate the geographic midpoint
        for a list of radian coordinates.
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
    lon = math.atan2(center[1], center[0])
    lat = math.atan2(center[2], hypotenuse(center[0], center[1]))

    return lat, lon


def dist_spherical(coord1, coord2, R):
    """ Use spherical law of cosines to calculate distance between two coordinates.

        coord1  -- first coordinate in decimal degrees
        coord2  -- second coordinate in decimal degrees
        R       -- (Earth) radius, e.g., 6371000
    """

    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]

    c = math.acos(
        math.sin(lat1) * math.sin(lat2) +
        math.cos(lat1) * math.cos(lat2) *
        math.cos(lon2 - lon1))

    return c * R


def get_testpoints(lat, lon, radius=(math.pi/2), count=8):
    """Give test points around a circle from given point."""

    interval = 2 * math.pi / count
    angle = 0

    points = []
    for _ in range(8):
        points.append([
            lat + radius * math.cos(angle),
            lon + radius * math.sin(angle)
        ])
        angle += interval

    return points


def center_of_min_distance(coords, start, R):
    """Find the center with minimum max distance for a set of coordinates."""
    test_distance = math.pi / 2
    center = start
    testpoints = coords
    min_distance = max(
        [dist_spherical(start, coord, R) for coord in coords])

    while (test_distance > 0.00000002):
        curr_min = center

        for coord in testpoints:
            current = max([dist_spherical(coord, x, R) for x in coords])
            if current < min_distance:
                min_distance = current
                curr_min = coord

        if (curr_min[0] == center[0] and curr_min[1] == center[1]):
            test_distance /= 2
        else:
            center = curr_min

        testpoints = get_testpoints(start[0], start[1], test_distance)

    return center, min_distance


if __name__ == '__main__':
    # earth radius, kilometres
    R = 6371

    coords = []
    with open('coords.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        coords = [[degtorad(float(x)) for x in row] for row in csv_reader]

    midpoint = geographic_midpoint(coords)
    max_dist = max([dist_spherical(midpoint, coord, R) for coord in coords])
    center, max_c = center_of_min_distance(coords, midpoint, R)

    print('Geographic midpoint for coordinates is {}, {}'.format(
        radtodeg(midpoint[0]),
        radtodeg(midpoint[1])))
    print('Center with minimum distance to coordinates is {}, {}'.format(
        radtodeg(center[0]),
        radtodeg(center[1])))
    print('Furthest coordinate is {0:.2f} km from midpoint '.format(max_dist) +
          'and {0:.2f} km from center.'.format(max_c))
