import re
import numpy as np
from dataclasses import dataclass, field
from itertools import repeat
import geometry as g
from matplotlib.path import Path as mplpath
# import matplotlib.path
import simplify
from itertools import chain
from benchmark import timeit

# Regex helpers
FLAGS = re.IGNORECASE
NODES = re.compile(r'[mlvhcsqtaz]', flags=FLAGS)
COMMAND = re.compile(r'(?P<node>[mlvhcsqta])\s?(?P<coords>[+-]?[+\-\d,.\s[e\-\d]*]*)\s', flags=FLAGS)


@dataclass
class Path:
    path: str
    data: list = field(init=False)
    compound: bool = False
    holes: set[int] = ()

    def __post_init__(self):
        self.path_to_points(self.path)
        if self.compound:
            self.holes = self.check_holes()
        self.data = self.rearrange()
        #    path = lower_precision(path, 5)

    def check_holes(self):
        """ Check if compound path has holes, aka contours nested within contours that won't need to be filled in visualisation.
         We assume depth of nesting to be one (no dart board-like paths with contour-in-contour-in-contour), simple stuff
         like the holes in "B" or "Á" """
        cvhs = {}
        holes = []
        for i, d in enumerate(self.data):
            hull = g.convex_hull(d)
            cvhs[i] = hull
        # sort conv hulls by area - the largest contour may contain lesser ones
        # cvhs = [(k, v['hull']) for k, v in sorted(cvhs.items(), key=lambda x: -x[1]['area'])]
        cvhs = [(k, v) for k, v in sorted(cvhs.items(), key=lambda x: g.polygon_area(x[1]), reverse=True)]
        for i, (path_id, hl) in enumerate(cvhs[:-1]):
            if i < len(cvhs) - 1 and path_id not in self.holes:  # no double nesting
                curr_path = mplpath(hl)
                holes.append(*[p[0] for p in cvhs[i + 1:] if all(curr_path.contains_points(p[1]))])
        return set(holes)

    def rearrange(self):
        return [rearrange(p) for p in self.data]

    def rescale(self, method='distance'):
        # TODO add acceptable string values (distances, viewbox/height)
        scaling_factor = 1 / min([min(g.euclidean_all(dp[:-1])) for dp in self.data])
        # tmp = max([max(g.euclidean_all(dp[:-1])) for dp in data_points])
        # print("Scaling factor:", scaling_factor)  # , tmp)
        return [scaling_factor * dp for dp in self.data]

    def round(self, precision="5"):
        # TODO handling ints as well -> typing: union(str, int) or simply accept strings and check numeric value (0-int, everything else)
        return [np.around(dp, precision) for dp in self.data]

    def path_to_points(self, pth):
        # Get available nodes
        cmds = re.findall(NODES, pth)  # e.g. ['m', 'v', 'l', 'h', 'l', 'L', 'h', 'l', 'h', 'l', 'H', 'l', 'z', 'm', 'h', 'l', 'z']

        if set([e.lower() for e in cmds]).intersection('csqta'):
            raise NotImplementedError('Curve-based nodes are not supported')

        subpaths = [cm for cm in cmds if cm.lower() == 'm']
        data_points = []
        if len(subpaths) == 1:
            data_points = [extract_points(pth)]

        elif len(subpaths) > 1:  # cmds.count("m") + cmds.count("M") > 1:
            # data_points = []
            self.compound = True
            # print("Compound path detected. Processing {} subpaths separately".format(len(subpaths)))
            strt = 0
            sub_pth = []
            for s in subpaths:
                sub_pth.append(pth.index(s, strt))
                strt += sub_pth[-1] + 1
            sub_pth.append(len(pth))

            # Make ranges ([[0, 465], [465, 798],...]) from indices ([0,465, 798, ...]) and split path accordingly
            pth = [pth[i[0]:i[1]] for i in [[a, b] for a, b in zip(sub_pth[:-1], sub_pth[1:])]]

            while pth:  # for i, p in enumerate(pth):
                subpath = pth.pop(0)
                last_point = [0., 0.]
                if subpath[0].islower() and data_points:
                    last_point = data_points[-1][-1]  # if one of subsequent paths starts with a relative moveto, we need last coordinate from the previous path
                data_points.append(extract_points(subpath, last_point))

        self.data = data_points

    @timeit
    def simplify_rdp(self, alpha=1):
        return [simplify.rdp(p, alpha) for p in self.data]

    @timeit
    def simplify_vw(self, keep_amount=None):
        # subpaths = []
        return [simplify.visvalingam(p, keep_amount) for p in self.data]


class MorphedPath(Path):
    original_path = None

    def __init__(self, path: str, effect: dict, original_path: str):
        super().__init__(path)
        self.effect = effect
        self.original_path = Path(original_path)

    def get_path(self):
        return self.data

    def initial_path(self):
        return self.original_path.data


def parse_coords(c_lst):
    c_lst = c_lst.split(" ")
    if "," in c_lst[0]:
        c_lst = [c.split(",") for c in c_lst]
        c_lst = [list(map(float, c)) for c in c_lst]
    else:
        c_lst = list(map(float, c_lst))
    return c_lst if len(c_lst) > 1 else c_lst[0]


def extract_points(pth, curr_pos=[0., 0.]):
    coordinates = []

    for i in re.finditer(COMMAND, pth):
        node, coords = i.groups()
        coords = parse_coords(coords)
        # print(node,coords)
        relative, node = node.islower(), node.lower()

        if node in "m":  # only one coord so exit as you should
            if type(coords[0]) == float:
                coordinates.append([x + y for x, y in zip(curr_pos, coords)])
                continue
            else:  # there are multiple coords after m, minified input, interpret as every coord after as a line and keep going
                m = coords.pop(0)
                coordinates.append([x + y for x, y in zip(curr_pos, m)])
                node = "l"

        curr_pos = coordinates[-1]

        if node in 'hvl':  # linear segments only

            # prevent one single (x,y)-segment of "l" from being treated like a couple of "h"/"v"s and one value of "h"/"v"
            # from being treated as a list and throwing an error
            if node in 'l' and type(coords[0]) == float or node in 'hv' and type(coords) == float:
                coords = [coords]

            if node in 'hv':
                alignment = 1 if node == 'h' else 0  # h: ( 1, _ ); v: ( _ , 1)
                missing_axis = 0.0 if relative else curr_pos[alignment]

                second = repeat(missing_axis, len(coords))
                coords = map(list, zip(coords, second))  # "h" only lists x -> add other axis with previous value

                if not alignment:  # flip the axis for "v" - we already made sure the value is right in "missing_axis"
                    coords = [c[::-1] for c in coords]

            if relative:
                try:
                    [coordinates.append([x + y for x, y in zip(coordinates[-1], c)]) for c in coords]
                except TypeError:
                    pass
            else:
                [coordinates.append(c) for c in coords]

    coordinates.append(coordinates[0])  # Connect the last dots
    return np.asarray(coordinates)


def rearrange(path: np.ndarray, first=None):
    path = path[:-1]
    if not first:
        first = np.lexsort(path.T[::-1])[0]  # first = np.lexsort((path[:, 1], path[:, 0]))[0]
    rearranged = list(chain(range(first, len(path)), range(first)))
    new_path = path[rearranged]
    return np.append(new_path, [new_path[0]], axis=0)


def rescale(paths, method='distance'):
    # TODO add acceptable string values (distances, viewbox/height)
    scaling_factor = 1 / min([min(g.euclidean_all(dp[:-1])) for dp in paths])
    # tmp = max([max(g.euclidean_all(dp[:-1])) for dp in data_points])
    # print("Scaling factor:", scaling_factor)  # , tmp)
    return [scaling_factor * dp for dp in paths]


def lower_precision(paths, precision=5):
    return [np.round(p, precision) for p in paths]
