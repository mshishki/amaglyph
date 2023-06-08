from simplify import rdp, visvalingam
from matplotlib import pyplot as plt

from svg import SVGDocument
from svgpath import lower_precision

vector_image = SVGDocument("examples/o.svg")
path_data = vector_image.get_path()
path = path_data.rearrange()
path = lower_precision(path, 5)

rdps = []
vws = []
epsilons = [0.25, 0.5, 0.75, 1.0, 2.0, 4.0, 8.0]

for e in epsilons:
    optimized_path = []
    optimized_path_vw = []

    for p in path:
        rdp_result = rdp(p, e)
        optimized_path.append(rdp_result)
        optimized_path_vw.append(visvalingam(p, len(rdp_result)))
    rdps.append(optimized_path)
    vws.append(optimized_path_vw)

for i in range(len(epsilons)):
    fig, ax = plt.subplots(1, 2, constrained_layout=True, sharey='col')
    plt.box(False)
    for a in ax:
        a.set_aspect('equal', 'box')
        a.axis('off')
        a.invert_yaxis()  # axis('off')
    colors = [("orange", "beige"), ("cornflowerblue", "skyblue")]

    for i_, (p, r, v) in enumerate(zip(path, rdps[i], vws[i])):
        clr = "white" if i_ in path_data.holes else "beige"
        ax[0].fill(p[:, 0], p[:, 1], color=clr)
        ax[0].plot(r[:, 0], r[:, 1], linestyle='--', linewidth=2, marker=".", color="brown", \
                   markeredgecolor="brown", markerfacecolor="white", markersize=10)

        clr = "white" if i_ in path_data.holes else "skyblue"
        ax[1].fill(p[:, 0], p[:, 1], color=clr)
        ax[1].plot(v[:, 0], v[:, 1], linestyle='-.', linewidth=2, marker=".", color="midnightblue", \
                   markeredgecolor="midnightblue", markerfacecolor="white", markersize=10)
    fig.suptitle(f'epsilon = {epsilons[i]}: {"+".join([str(len(o)) for o in rdps[i]])} pts', fontsize=30)
    ax[0].text(0.5, -0.1, 'Ramer-Douglas-Peucker', size=15, ha="center", transform=ax[0].transAxes)
    ax[1].text(0.5, -0.1, 'Visvalingam-Whyatt', size=15, ha="center", transform=ax[1].transAxes)
    fig.show()
    #plt.savefig(f"plots/lnsimp{str(epsilons[i]).replace('.', '-')}.png", dpi=300)
