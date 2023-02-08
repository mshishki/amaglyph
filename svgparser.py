from itertools import accumulate
import re
from xml.dom import minidom

doc = minidom.parse("test_assets/example3_lin_rough_ink2.svg")

# SEE https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d: also applicable to glyphs

# path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')] # path with noisy data
pth = [path.getAttribute('inkscape:original-d') for path in doc.getElementsByTagName('path')]  # original path (pre-Roughen)
if len(pth) == 1:
    pth = pth[0]
# pth = "M 0.30000001,0.30000001 H 13.933077 25.256744 59.06775 81.189417 100.34851 126.17069 l 0.0895,15.27252499 -0.0895,20.698758 0.37429,18.30026 -0.37429,8.663799 -10.09651,-0.290976 -10.72236,0.368376 -9.745941,1.491605 -9.632542,2.969155 -5.49938,2.073665 -6.844074,2.580713 -6.096106,2.562712 -6.574017,2.76362 -9.175204,2.743334 L 39.20731,82.737762 26.004762,82.329527 18.821459,81.244242 9.2512131,78.245567 0.30000001,73.724522 0.23307432,61.51054 0.19531793,54.619974 0.06588414,30.998224 0.23148782,9.2835971 Z"

# TODO check if multiple paths
cmds = re.findall(r'[mlvhcsqtaz]', pth, flags=re.IGNORECASE)  # ['H', 'l', 'L', 'Z']
if set([e.lower() for e in cmds]).intersection('csqta'):
    print("Not implemented")
# print(cmds)  # ['H', 'l', 'L', 'Z']
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


test = [[0.3, 0.3], [13.9331, 0.3], [25.2567, 0.3], [59.0677, 0.3], [81.1894, 0.3], [100.3485, 0.3], [126.1707, 0.3],
        [126.2602, 15.5725], [126.1707, 36.2713], [126.545, 54.5715], [126.1707, 63.2353],
        [116.0742, 62.9444], [105.3518, 63.3127], [95.6059, 64.8043], [85.9733, 67.7735], [80.474, 69.8472],
        [73.6299, 72.4279], [67.5338, 74.9906], [60.9598, 77.7542], [51.7846, 80.4975], [39.2073, 82.7378],
        [26.0048, 82.3295], [18.8215, 81.2442], [9.2512, 78.2456], [0.3, 73.7245], [0.2331, 61.5105], [0.1953, 54.62],
        [0.0659, 30.9982], [0.2315, 9.2836]]

curr_pos = [0, 0]

for i in re.finditer(command, pth):
    node, coords = i.groups()
    coords = parse_coords(coords)
    if not coordinates:  # (meaning node is m) and todo if there is only one path
        coordinates.append([x + y for x, y in zip(curr_pos, coords)])
        continue
    curr_pos = coordinates[-1]
    relative, node = node.islower(), node.lower()
    if type(coords[0]) == float:
        alignment = 0 if node == 'h' else 1  # h: (x, 0); v: (0, y)

        if relative:
            coords = map(lambda x: x + curr_pos[alignment], coords)
            coords = accumulate(coords)

        if alignment:
            coords = [[curr_pos[0], c] for c in coords]
        else:
            coords = [[c, curr_pos[1]] for c in coords]  # itertools.repeat(10, 3) --> 10 10 10
        coordinates += coords
    else:

        if relative:
            for c in coords:
                coord = [x + y for x, y in zip(coordinates[-1], c)]
                coordinates.append(coord)

        else:
            [coordinates.append(c) for c in coords]
