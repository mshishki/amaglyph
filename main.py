import svgparser as svgp
from matplotlib import pyplot as plt
import numpy as np

# TODO SEE https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d: also applicable to glyphs
if __name__ == '__main__':

    examples = ["test_assets/acute.svg", "test_assets/a500.svg", "test_assets/example3_lin_rough_ink2.svg", "test_assets/a_inkscape.svg"]
    pth, props = svgp.parse_svg(examples[0])
    data_points = svgp.path_to_points(pth[0])

"""NEXT STEPS
0. Prepping
0.1. SVG Parsing
0.2. Plotting
0.3. OOPification
1. Corner finding -> Segment splitting
2. Smoothing of segments from (1)
3. Fitting of smoothed segments
3.1 Line fitting
3.2 Curve fitting
4. Evaluation (Perimeter / Volume / ...) 
"""

vb = props["viewBox"]
vb = [vb[2]-vb[0], vb[3]-vb[1]]
ratio = vb[0] / vb[1]
#print(ratio)
n = 5
fSize = (n*ratio, n) if ratio < 1 else (n, n*ratio)
print(fSize)
#viewbox = [55.76775, 87.166107]
# ratio = (viewbox[0]/viewbox[1])

# FIG SIZE
# GRID SIZE BASED ON FIG SIZE / EQUAL
#fSize = (6, 8)
#plt.close('all')
fig = plt.figure(dpi=100, figsize=fSize)
ax = fig.add_subplot(1, 1, 1)
# TODO calc limits in OOP structure based on whether there is one path or multiple
bounds = [np.max([[np.max(d[:, i]) for d in data_points]]) for i in range(2)]

#https://matplotlib.org/2.1.1/gallery/api/font_file.html#sphx-glr-gallery-api-font-file-py
for i,d in enumerate(data_points):
    dx, dy = d[:, 0], d[:, 1]
    #plt.plot(d[:, 0], d[:, 1])
    plt.plot(dx, dy, linestyle='-', linewidth=1, marker="o", markersize=3, markerfacecolor='w', label='path {}'.format(i))#markersize = 99,
     #ax.grid(color='r', linestyle='-', linewidth=2)
    #plt.yscale('linear')
    #https://matplotlib.org/2.1.1/api/_as_gen/matplotlib.pyplot.plot.html
    #markeredgecolor='k',
    #plt.plot(range(10), linestyle='--', marker='o', color='b', label='line with marker')  # plt.plot(range(10), '--bo', label='line with marker')
#https://matplotlib.org/stable/gallery/lines_bars_and_markers/marker_reference.html#sphx-glr-gallery-lines-bars-and-markers-marker-reference-py
ax.axis('equal')

# Major ticks every 20, minor ticks every 5
#major_ticks = np.arange(0, 101, 20)

ax.tick_params(direction='out', length=0, width=0, colors='k', which="major",
               grid_color='k', top=True, labeltop=True, bottom=False, labelbottom=False, labelsize=7)
ax.tick_params(which="minor", grid_linestyle="", length=0, width=0)

major_ticks_steps = 10
ax.set_xticks(np.arange(0, round(bounds[0]/major_ticks_steps)*major_ticks_steps+1, major_ticks_steps))
ax.set_xticks(np.arange(0, bounds[0], 2), minor=True)
ax.set_yticks(np.arange(0, round(bounds[1]/major_ticks_steps)*major_ticks_steps+1, major_ticks_steps))
ax.set_yticks(np.arange(0, bounds[1], 2), minor=True)
#ax.margins(x=0.1, y=0.1, tight=True)
#plt.xlim(-10, round(bounds[0]/major_ticks_steps)*major_ticks_steps+9)
#plt.ylim(0, bounds[1])
ax.grid(visible=True)
ax.grid(which='both', alpha=0.2, linestyle='dotted') # "--"
#ax.grid(which='major', alpha=0.6, linestyle='dotted') # ":"
plt.box(False)
plt.gca().invert_yaxis()
plt.autoscale()

plt.legend()

plt.show()
# fig.savefig('test.png')
#https://stackoverflow.com/questions/50829104/how-to-find-corners-given-a-set-of-points
#https://www.researchgate.net/publication/226691035_On_numerical_optimization_theory_of_infinite_kernel_learning
#https://iopscience.iop.org/article/10.1088/2633-1357/abad0d