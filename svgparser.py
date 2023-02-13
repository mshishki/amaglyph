from itertools import repeat
import re
from xml.dom import minidom

import numpy as np

# Regex helpers
FLAGS = re.IGNORECASE
NODES = re.compile(r'[mlvhcsqtaz]', flags=FLAGS)
COMMAND = re.compile(r'(?P<node>[mlvhcsqta])\s?(?P<coords>[+-]?[+\-\d,.\s[e\-\d]*]*)\s', flags=FLAGS)


def parse_svg(path_to_file):  # TODO include cases for paths within layers and for standalone paths
    with minidom.parse(path_to_file) as doc:
        svg = doc.getElementsByTagName("svg")[0]

        # Assume we have one path per SVG and one optional effect applied to it
        path_elem = dict(svg.getElementsByTagName('path')[0].attributes.items())
        path = [path_elem["d"]]

        # if path has effects applied, add the initial path "inkscape:original-d" and get params for cross-validation
        if 'inkscape:path-effect' in path_elem.keys():
            path_effect = svg.getElementsByTagName('inkscape:path-effect')[0]
            path_elem['path-effect'] = dict(path_effect.attributes.items())
            path.append(path_elem["inkscape:original-d"])  # .getAttributeNode('method').value

        # Parse dimensions (we only need viewBox so far)
        dimensions = {tag: svg.getAttribute(tag) for tag in ['width', 'height', 'viewBox']}
        dimensions['viewBox'] = [float(coord) for coord in dimensions['viewBox'].split(" ")]

        # doc.unlink()
    # Return path(s) and a merged dictionary w/ essential properties
    return path, path_elem | dimensions


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
        #print(node,coords)
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
                    # print('OOPSIE')
                    # breakpoint()
                    pass
            else:
                [coordinates.append(c) for c in coords]
        elif node in 'z':
            continue

    coordinates.append(coordinates[0]) # Connect the last dots
    # Flip the y axis https://jenkov.com/tutorials/svg/svg-coordinate-system.html - NVM, CAN BE DONE IN MATPLOTLIB
    # coordinates = [[c[0], -c[1]] for c in coordinates]
    return np.asarray(coordinates)


def path_to_points(pth):
    # Get avai
    cmds = re.findall(NODES, pth)  # e.g. ['m', 'v', 'l', 'h', 'l', 'L', 'h', 'l', 'h', 'l', 'H', 'l', 'z', 'm', 'h', 'l', 'z']

    if set([e.lower() for e in cmds]).intersection('csqta'):
        raise NotImplementedError('Curve-based nodes are not supported')

    data_points = []

    subpaths = [cm for cm in cmds if cm.lower() == 'm']

    if len(subpaths) == 1:
        data_points.append(extract_points(pth))

    elif len(subpaths) > 1:  # cmds.count("m") + cmds.count("M") > 1:
        print("Compound path detected. Processing {} subpaths separately".format(len(subpaths)))
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

    return data_points
