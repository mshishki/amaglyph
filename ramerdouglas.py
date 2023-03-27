import geometry as g
import numpy as np


def ramer(data_points, alpha=1.0):
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
        results1 = ramer(data_points[:pt_index + 1], alpha)[:-1]
        results2 = ramer(data_points[pt_index:], alpha)
        results = np.concatenate((results1, results2))
    else:
        results = [start, end]

    return results


if __name__ == '__main__':
    from svg import SVGDocument
    from svgpath import lower_precision

    vector_image = SVGDocument("test_assets/a_rough_cp.svg")
    path_data = vector_image.get_path()
    path = path_data.rearrange()
    path = lower_precision(path, 5)
    optimized = []
    for p in path:
        optimized.append(ramer(p, 1))
        print("lengths:", len(p), len(optimized[-1]))

    from matplotlib import pyplot as plt
    vb = vector_image.dimensions
    magnify = 5
    vb = [vb[2] - vb[0], vb[3] - vb[1]]
    ratio = vb[0] / vb[1]  # print(ratio)
    fSize = (magnify * ratio, magnify) if ratio < 1 else (magnify, magnify * ratio)

    fig = plt.figure(dpi=100, figsize=fSize)
    ax = fig.add_subplot(1, 1, 1)
    plt.box(False)
    ax.axis('equal')
    ax.axis('off')
    plt.gca().invert_yaxis()
    plt.autoscale()
    plt.tight_layout(pad=0.0)
    ct = 0

    for i_, (p, o) in enumerate(zip(path, optimized)):
        plt.plot(p[:, 0], p[:, 1], linestyle='-', linewidth=2, color="orange")
        clr = "white" if i_ in path_data.holes else "beige"
        ax.fill(p[:, 0], p[:, 1], color=clr)

        plt.plot(o[:, 0], o[:, 1], linestyle='--', linewidth=1, marker=".", color="brown", markeredgecolor="brown", markerfacecolor="red", markersize=5)  # , marker="o", markersize=3, markerfacecolor='w')  # markersize = 99,

    fig.show()
