import numpy as np
from matrix import *


def de_casteljau(control_points, t, branches=None):
    """ A somewhat "creative" (derogative) implementation of De Casteljau,
    used for both splitting Bezier curve in two and calculating its points with specified speed """
    if t == 0.0:  # first control point
        return control_points[0]
    elif t == 1.0:  # last control point
        return control_points[-1]

    # create lines between consecutive control points
    segments = zip(control_points[:-1], control_points[1:])
    # extract point on the line at given t
    points = np.asarray([s[0] + t * (s[1] - s[0]) for s in segments])

    if branches:
        left, right = branches
        left.append(control_points[0])
        right.insert(0, control_points[-1])
        branches = [left, right]

    if len(control_points) == 1:
        # return (control_points[0], *branches) if branches else control_points[0]
        return (control_points[0], *branches) if branches else control_points[0]

    return de_casteljau(points, t, branches)


def point_on_curve(control_points, t):
    """Wrapper for evaluating a point in the curve via `de_casteljau`"""
    segments = control_points

    if t == 0.0:  # first control point
        return segments[0]
    elif t == 1.0:  # last control point
        return segments[-1]
    return de_casteljau(control_points, t)


def split_curve(control_points, t):
    """Wrapper for splitting curve via `de_casteljau`"""
    _, left, right = de_casteljau(control_points, t, [[], []])
    return left, right


def flatten_curve(control_points, steps: int = 25):
    """ Reconstruct Bezier curve from control points for a specified number of segments """
    t_vals = [i * (1 / steps) for i in range(steps + 1)]
    pts = [point_on_curve(control_points, t) for t in t_vals]
    return np.asarray(pts)  # TODO add points based on flatness


def from_polynomials(control_points, t):
    """ Evaluation of a curve point at t, this time using polynomial representation.
     Less numerically stable than Casteljau. """
    order = len(control_points)
    # create monomial basis
    P = monomial(t, order)

    # create spline matrix
    S = spline_matrix(order)

    # create geometry basis
    G = np.matrix(control_points)

    return (P * S * G).A1


if __name__ == "__main__":
    # pth, props = svgp.parse_svg("test_assets/TEST_CURVE2.svg") # 'M 0.08430203,20.022515 C 13.326388,-9.2997562 28.319917,1.5821534 30.961649,4.4126518'

    cp = np.asarray([[0.08166278, 20.258437], [13.326388, -9.2997562], [28.319917, 1.5821534], [30.961649, 4.4126518]])

    single_point = de_casteljau(cp, 0.5)
    curve_points = flatten_curve(cp, 95)
    left, right = split_curve(cp, 0.5)

    single_point_ = from_polynomials(cp, 0.5)
