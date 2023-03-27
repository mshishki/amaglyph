import numpy as np
from casteljau import flatten_curve
from matplotlib import pyplot as plt
import svgparser as svgp
from itertools import combinations
from typing import overload, Union


def slope(p1, p2):
    slope_x, slope_y = p1 - p2
    if slope_x == 0.:
        return float('inf')
    else:
        return slope_y / slope_x


def convex_hull(pts):
    """Graham scan"""  # https://lvngd.com/blog/convex-hull-graham-scan-algorithm-python/ https://medium.com/@pascal.sommer.ch/a-gentle-introduction-to-the-convex-hull-problem-62dfcabee90c
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
            # https://stackoverflow.com/questions/22156646/homework-cross-product-of-3-points-in-2d-space
            # p1, p2, p3 = hull[-3:] #  cross_product = np.cross(p2 - p1, p3 - p1)

    h.append(h[0])  # add first point to close the polygon
    return np.array(h)


def polygon_area(contour):
    """ Area of the polygon formed by given vertices (shoelace formula) """
    # https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
    n = len(contour)  # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += contour[i][0] * contour[j][1]
        area -= contour[j][0] * contour[i][1]
    area = abs(area) / 2.0
    return area


def euclidean(p1, p2):
    # Euclidean distance is the L2 norm: numpy.linalg.norm(a-b)
    # https://stackoverflow.com/questions/1401712/how-can-the-euclidean-distance-be-calculated-with-numpy
    return np.linalg.norm(p2 - p1)


def euclidean_all(data_points):
    # https://stackoverflow.com/questions/13590484/calculating-euclidean-distance-between-consecutive-points-of-an-array-with-numpy
    # compute the deltas from vectorized points
    d = np.diff(data_points, axis=0)
    # np.hypot to compute the lengths:
    return np.hypot(d[:, 0], d[:, 1])


def get_perimeter(data_points):
    # contour perimeter, or arc length
    return np.sum(euclidean_all(data_points))  # (a, b) for a, b in zip(data_points[:-1], data_points[1:])])


def get_curvature(points):  # p1,p2,p3):
    # #https://stackoverflow.com/questions/41144224/calculate-curvature-for-3-points-x-y

    # Calculating length of all three sides
    sides = [euclidean(*p_) for p_ in combinations(points, 2)]
    # len_side_1 = np.linalg.norm(p2 - p1)
    # len_side_2 = np.linalg.norm(p3 - p2)
    # len_side_3 = np.linalg.norm(p3 - p1)

    # Calculating area using Herons formula
    #     sp = (len_side_1 + len_side_2 + len_side_3) / 2  # semiperimeter
    #    area = math.sqrt(sp * (sp - len_side_1) * (sp - len_side_2) * (sp - len_side_3))

    area = polygon_area(points)

    # Calculating curvature using Menger curvature formula
    curvature = (4 * area) / np.prod(sides)  # (len_side_1 * len_side_2 * len_side_3)

    return curvature, area


def perpendicular_distance(pt, start, end):
    """ Calculate perpendicular distance between vectors -> vector rejection of a on b """
    b = end - start  # vector AB = b - a
    a = end - pt  # vector AC = c - a # a = end - pt

    # distance can be expressed via cross-product ||a x b|| = ||a|| ||b|| ||sin(theta)||
    # easier than first calculating delta y or delta x since we don't need to make theta-based distinction of axes etc etc
    num = np.linalg.norm(np.cross(b, a))  # cross-product of vectors = magnitude
    den = np.linalg.norm(b)
    # if pos > 140:
    #    print(f"{pos}: {num}/{den}, {num/den}")
    return num / den

