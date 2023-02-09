from itertools import accumulate, repeat
import re
from xml.dom import minidom

doc = minidom.parse("test_assets/example3_lin_rough_ink2.svg")

# SEE https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d: also applicable to glyphs

# pth = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]  # path with noisy data
pth = [path.getAttribute('inkscape:original-d') for path in
       doc.getElementsByTagName('path')]  # original path (pre-Roughen)
if len(pth) == 1:
    pth = pth[0]
# pth = "M 0.30000001,0.30000001 H 13.933077 25.256744 59.06775 81.189417 100.34851 126.17069 l 0.0895,15.27252499 -0.0895,20.698758 0.37429,18.30026 -0.37429,8.663799 -10.09651,-0.290976 -10.72236,0.368376 -9.745941,1.491605 -9.632542,2.969155 -5.49938,2.073665 -6.844074,2.580713 -6.096106,2.562712 -6.574017,2.76362 -9.175204,2.743334 L 39.20731,82.737762 26.004762,82.329527 18.821459,81.244242 9.2512131,78.245567 0.30000001,73.724522 0.23307432,61.51054 0.19531793,54.619974 0.06588414,30.998224 0.23148782,9.2835971 Z"

# TODO check if multiple paths
cmds = re.findall(r'[mlvhcsqtaz]', pth, flags=re.IGNORECASE)  # ['H', 'l', 'L', 'Z']
if set([e.lower() for e in cmds]).intersection('csqta'):
    print("Not implemented")


command = re.compile(r'(?P<node>[mlvhcsqtaz])\s?(?P<coords>[+-]?[+\-\d,.\s]*)\s', flags=re.IGNORECASE)
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

            coords = zip(coords, second)  # "h" only lists x -> add other axis with previous value
            if alignment:  # flip the axis for "v" - we already made sure the value is right in "missing_axis"
                coords = [c[::-1] for c in coords]

        if relative:
            [coordinates.append([x + y for x, y in zip(coordinates[-1], c)]) for c in coords]
        else:
            [coordinates.append(c) for c in coords]
