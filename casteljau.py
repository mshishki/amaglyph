import svgparser as svgp
import numpy as np

pth, props = svgp.parse_svg("test_assets/TEST_CURVE2.svg")
# 'M 0.08430203,20.022515 C 13.326388,-9.2997562 28.319917,1.5821534 30.961649,4.4126518'

cp = np.asarray([[0.08166278, 20.258437], [13.326388, -9.2997562], [28.319917, 1.5821534], [30.961649, 4.4126518]])

order = 3


def point_on_curve(control_points, t):
    segments = control_points

    if t == 0.0:  # first control point
        return segments[0]
    elif t == 1.0:  # last control point
        return segments[-1]
    while len(segments) != 1:
        # create lines between consecutive control points
        segments = zip(segments[:-1], segments[1:])
        # extract point on the line at given t
        segments = np.asarray([s[0] + t * (s[1] - s[0]) for s in segments])
    return segments[0]


def flattened_curve(control_points, steps: int = 25):
    # Generate values at which we sample our B(t)
    t_vals = [i * (1 / steps) for i in range(steps + 1)]

    pts = [point_on_curve(control_points, t) for t in t_vals]

    return np.asarray(pts)


def midpoints(control_points, t, split=True):
    if t == 0.0:  # first control point
        return control_points[0]
    elif t == 1.0:  # last control point
        return control_points[-1]

    # Create pairs between lines
    segments = zip(control_points[:-1], control_points[1:])
    # extract point on the line at given t
    segments = np.asarray([s[0] + t * (s[1] - s[0]) for s in segments])
    if split:
        return segments, control_points
    return segments


def split_curve(control_points, t):
    segments = control_points

    left, right = [], []

    while len(segments) > 0:
        segments, control_points_ = midpoints(segments, t, True)

        left.append(control_points_[0])
        right.append(control_points_[-1])

    right.reverse()
    return np.asarray(left), np.asarray(right)


l, r = split_curve(cp, 0.5)
pt = point_on_curve(cp, 0.5)
crv = flattened_curve(cp, 25)
