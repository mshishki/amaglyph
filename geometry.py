import numpy as np
from itertools import combinations


def slope(p1, p2):
    slope_x, slope_y = p1 - p2
    if slope_x == 0.:
        return float('inf')
    else:
        return slope_y / slope_x


def convex_hull(pts):
    """Graham scan"""
    points = pts.copy()
    h = []

    # Sort points by smallest value of x
    points = points[np.lexsort(points.T[::-1])]  # curve_points[np.lexsort((curve_points[:,1], curve_points[:,0]))]

    # The first point definitely belongs to the convex hull - take it out
    h.append(points[0])
    points = np.delete(points, 0, axis=0)

    # Sort remaining points in counterclockwise order by their slope (note: will be shown as clockwise in matplotlib bc we flipped the y axis)
    points = np.array(sorted(points, key=lambda pt: (slope(pt, h[0]), -pt[1], pt[0])))

    for p in points:
        h.append(p)
        # cross product of three points = direction of rotation
        # cross > 0: rotating left = the corner (2nd pt) in polygon formed by last three points is convex and lies on the outside
        # cross < 0: rotating right => middle point lies within the hull
        # cross == 0: three points are collinear
        while len(h) > 2 and np.cross(h[-2] - h[-3], h[-1] - h[-3]) <= 0:
            h.pop(-2)

    h.append(h[0])  # add first point to close the polygon
    return np.array(h)


def polygon_area(contour):
    """ Area of the polygon formed by given vertices (shoelace formula) """
    n = len(contour)  # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += contour[i][0] * contour[j][1]
        area -= contour[j][0] * contour[i][1]
    area = abs(area) / 2.0
    return area


def euclidean(p1, p2):
    # Euclidean distance is the L2 norm
    return np.linalg.norm(p2 - p1)


def euclidean_all(data_points):
    # compute the deltas from vectorized points
    d = np.diff(data_points, axis=0)
    # np.hypot to compute the lengths
    return np.hypot(d[:, 0], d[:, 1])


def get_perimeter(data_points):
    # contour perimeter, or arc length
    return np.sum(euclidean_all(data_points))


def get_curvature(points):  # p1,p2,p3):
    # Calculating length of all three sides
    sides = [euclidean(*p_) for p_ in combinations(points, 2)]
    area = polygon_area(points)

    curvature = (4 * area) / np.prod(sides)

    return curvature, area


def perpendicular_distance(pt, start, end):
    """ Calculate perpendicular distance between vectors -> vector rejection of a on b """
    b = end - start  # vector AB = b - a
    a = end - pt  # vector AC = c - a # a = end - pt

    # distance can be expressed via cross-product ||a x b|| = ||a|| ||b|| ||sin(theta)||
    # easier than first calculating delta y or delta x since we don't need to make theta-based distinction of axes etc etc
    num = np.linalg.norm(np.cross(b, a))  # cross-product of vectors = magnitude
    den = np.linalg.norm(b)
    return num / den
