import svgparser as svgp

# TODO SEE https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d: also applicable to glyphs
if __name__ == '__main__':

    pth, props = svgp.parse_svg("test_assets/a500.svg")
    data_points = svgp.path_to_points(pth[0])

    from matplotlib import pyplot as plt

    viewbox = [55.76775, 87.166107]
    ratio = (viewbox[0]/viewbox[1])
    fSize = (2*ratio, 2 )
    fig = plt.figure(figsize=fSize,dpi=100)  # ,figsize = ...

    for d in data_points:
        plt.plot(d[:, 0], d[:, 1])

    plt.gca().invert_yaxis()
    plt.show()
    # fig.savefig('test.png')
