from itertools import accumulate, repeat
import re
from xml.dom import minidom

doc = minidom.parse("test_assets/example3_lin_rough_ink2.svg")

# SEE https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d: also applicable to glyphs
pth = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]  # path with noisy data
#pth = [path.getAttribute('inkscape:original-d') for path in doc.getElementsByTagName('path')]  # original path (pre-Roughen)
if len(pth) == 1:
    pth = pth[0]

# TODO check if multiple paths
cmds = re.findall(r'[mlvhcsqtaz]', pth, flags=re.IGNORECASE)  # ['H', 'l', 'L', 'Z']
if set([e.lower() for e in cmds]).intersection('csqta'):
    print("Not implemented")

command = re.compile(r'(?P<node>[mlvhcsqtaz])\s?(?P<coords>[+-]?[+\-\d,.\s[e\-\d]*]*)\s', flags=re.IGNORECASE)
coordinates = []


def parse_coords(clist):
    clist = clist.split(" ")
    if "," in clist[0]:
        clist = [c.split(",") for c in clist]
        clist = [list(map(float, c)) for c in clist]
    else:
        clist = list(map(float, clist))
    return clist if len(clist) > 1 else clist[0]


curr_pos = [0, 0]

for i in re.finditer(command, pth):
    node, coords = i.groups()
    coords = parse_coords(coords)

    relative, node = node.islower(), node.lower()

    if node in "m":  # only one coord so exit as you should
        if type(coords[0]) == float:
            coordinates.append([x + y for x, y in zip(curr_pos, coords)])
            continue
        #FIXME
        else:  # there are multiple coords after m, minified input, interpret as every coord after as a line and keep going
            m = coords.pop(0)
            coordinates.append([x + y for x, y in zip(curr_pos, m)])
            node = "l"

    curr_pos = coordinates[-1]

    if node in 'hvl':  # linear segments only
        if type(coords[0]) == float:
            alignment = 0 if node == 'h' else 1  # h: (x, 0); v: (0, y)
            missing_axis = 0.0 if relative else curr_pos[alignment]
            second = repeat(missing_axis, len(coords))

            coords = map(list, zip(coords, second))  # "h" only lists x -> add other axis with previous value
            if alignment:  # flip the axis for "v" - we already made sure the value is right in "missing_axis"
                coords = [c[::-1] for c in coords]

        if relative:
            [coordinates.append([x + y for x, y in zip(coordinates[-1], c)]) for c in coords]
        else:
            [coordinates.append(c) for c in coords]

doc.unlink()
