import numpy as np


# symbolic monomial, aka [1 t t^2 t^3] with given t
def monomial(t, order=3):
    return np.matrix([t ** p for p in range(order + 1)])


def spline_matrix(order=3):
    if order == 2:
        return np.matrix([[1, 0, 0], [-2, 2, 0], [1, -2, 1]])
    if order == 3:
        return np.matrix([[1, 0, 0, 0], [-3, 3, 0, 0], [3, -6, 3, 0], [-1, 3, -3, 1]])
    return
