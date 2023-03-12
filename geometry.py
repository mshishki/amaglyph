import numpy as np
from casteljau import flatten_curve
from matplotlib import pyplot as plt
import svgparser as svgp


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

    # Sort remaining points in counterclockwise order by their slope
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


if __name__ == "__main__":
    # TODO: Jarvis march? Could be useful depending on the hull https://en.wikipedia.org/wiki/Gift_wrapping_algorithm
    pth, props = svgp.parse_svg("test_assets/a_rough.svg")
    curve_points = svgp.path_to_points(pth[0])[0]

    hull = convex_hull(curve_points)

    a = polygon_area(curve_points)
    a_hull = polygon_area(hull)

    vb = props["viewBox"]
    magnify = 3
    vb = [vb[2] - vb[0], vb[3] - vb[1]]
    ratio = vb[0] / vb[1]  # print(ratio)
    fSize = (magnify * ratio, magnify) if ratio < 1 else (magnify, magnify * ratio)
    
    fig = plt.figure(dpi=100, figsize=fSize)
    ax = fig.add_subplot(1, 1, 1)

    plt.plot(curve_points[:, 0], curve_points[:, 1], linestyle='-', linewidth=1, color="orange")  # , marker="o", markersize=3, markerfacecolor='w')  # markersize = 99,
    ax.fill(curve_points[:, 0], curve_points[:, 1], color="orange")
    plt.plot(hull[:, 0], hull[:, 1], linestyle='-', linewidth=2, marker="x", color="b", markeredgecolor="k")  # , marker="o", markersize=3, markerfacecolor='w')  # markersize = 99,

    plt.box(False)
    ax.axis('equal')
    ax.axis('off')
    plt.gca().invert_yaxis()
    plt.autoscale()
    plt.tight_layout(pad=0.0)
    fig.show()
