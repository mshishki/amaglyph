import geometry as g
import numpy as np


def rdp(data_points, alpha=1.0):
    # d_points = data_points
    # np.array_equal(data_points[0], data_points[-1])
    start = data_points[0]
    end = data_points[-1]

    if np.array_equal(start, end):
        # closed polygon = change the end
        end = data_points[-2]

    d_max = 0.
    pt_index = 0

    for i in range(1, len(data_points) - 1):
        # Traverse through points of S_k and determine parameters for straight line segment between last vertices
        #  for each possible curve segment
        curr_point = data_points[i]
        perp = g.perpendicular_distance(curr_point, start, end)
        if perp > d_max:
            d_max = perp
            pt_index = i

    if d_max > alpha:
        results1 = rdp(data_points[:pt_index + 1], alpha)[:-1]
        results2 = rdp(data_points[pt_index:], alpha)
        results = np.concatenate((results1, results2))
    else:
        results = [start, end]

    return results


def visvalingam(data_points, keep_amount=None):
    areas = []
    for i in range(1, len(data_points) - 1):
        curr_points = data_points[i - 1:i + 2]
        area = g.polygon_area(curr_points)
        areas.append(area)
        # print(i, area, curr_points[1])

    if not keep_amount:
        # determine amount of critical points from their distribution (the 5% largest areas must belong to corners)
        keep_amount = len([a for a in areas if np.greater(a, np.percentile(areas, 95))]) + 1  # or 99.5, even

    while len(data_points) > keep_amount:
        ind = np.concatenate(np.where(areas == min(areas)))[0]

        # delete the area and the middle point at corresponding indices
        old_area = areas.pop(ind)
        data_points = np.delete(data_points, ind + 1, axis=0)

        # Compute areas with new neighbourhood
        if ind < len(areas) - 1:
            areas[ind] = g.polygon_area(data_points[np.arange(ind, ind + 3, dtype=int)])
        if ind > 0:
            areas[ind - 1] = g.polygon_area(data_points[np.arange(ind - 1, ind + 2, dtype=int)])

    return data_points


if __name__ == '__main__':
    from svg import SVGDocument
    from svgpath import lower_precision

    vector_image = SVGDocument("test_assets/a_rough_cp.svg")
    path_data = vector_image.get_path()
    path = path_data.rearrange()
    path = lower_precision(path, 5)
    optimized = []
    optimized2 = []

    for p in path:
        optimized.append(rdp(p, 1))
        optimized2.append(visvalingam(p))
        #print("lengths:", len(p), len(optimized[-1]), len(optimized2[-1]))

    from matplotlib import pyplot as plt

    fig, ax = plt.subplots(1, 2, constrained_layout=True, sharey='col')

    plt.box(False)
    for a in ax:
        a.set_aspect('equal', 'box')
        a.axis('off')
        a.invert_yaxis()  # axis('off')

    for i_, (p, r, v) in enumerate(zip(path, optimized, optimized2)):
        ax[0].plot(p[:, 0], p[:, 1], linestyle='-', linewidth=2, color="orange")
        clr = "white" if i_ in path_data.holes else "beige"
        ax[0].fill(p[:, 0], p[:, 1], color=clr)
        ax[0].plot(r[:, 0], r[:, 1], linestyle='--', linewidth=1, marker="x", color="brown", \
                   markeredgecolor="brown", markerfacecolor="brown", markersize=5)

        ax[1].plot(p[:, 0], p[:, 1], linestyle='-', linewidth=2, color="cornflowerblue")  # steelblue")
        clr = "white" if i_ in path_data.holes else "skyblue"
        ax[1].fill(p[:, 0], p[:, 1], color=clr)
        ax[1].plot(v[:, 0], v[:, 1], linestyle='-.', linewidth=1, marker="x", color="blue", \
                   markeredgecolor="midnightblue", markerfacecolor="blue", markersize=5)

    fig.suptitle('Line simplification: Results', fontsize=30)
    ax[0].set_title(f'{sum([len(o) for o in optimized])} pts')
    ax[0].text(0.5, -0.1, 'Ramer-Douglas-Peucker', size=15, ha="center", transform=ax[0].transAxes)
    ax[1].set_title(f'{sum([len(o) for o in optimized2])} pts')
    ax[1].text(0.5, -0.1, 'Visvalingam-Whyatt', size=15, ha="center", transform=ax[1].transAxes)

    plt.tight_layout(pad=0.0)

    fig.show()
