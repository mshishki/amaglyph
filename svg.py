from xml.dom import minidom
from svgpath import Path, MorphedPath


NUM_ATTRS = {'style': ['opacity', 'width'], 'path-effect': []}


def parse_str_as_dict(properties: str, attributes: list[str]):
    prop_dict = dict(p.split(":") for p in properties.split(";"))
    prop_dict.update({k: float(v) for k, v in prop_dict.items() if any(k.endswith(s) for s in attributes)}) #
    return prop_dict


class SVGShape:
    style: dict = None
    path = None

    def __init__(self, path_dict, *effect):
        self.style = parse_str_as_dict(path_dict['style'], NUM_ATTRS['style'])
        if effect:
            self.path = MorphedPath(path_dict['d'], effect, path_dict['inkscape:original-d'])
        else:
            self.path = Path(path_dict['d'])


class SVGDocument:
    shape = None

    def __init__(self, filepath, original_only=False):
        self.filepath = filepath
        with minidom.parse(filepath) as doc:
            svg = doc.documentElement   # getElementsByTagName("svg")[0]
            # TODO parse attrs from svg.attributes.items() like width, height, viewBox; from svg.children: 'namedview''inkscape:document-units', 'pt'),
            attrs = dict(svg.attributes.items())
            self.dimensions = [float(coord) for coord in attrs['viewBox'].split(" ")]
            # We work with one path and assume there will be one path and one path only
            path_dict = dict(svg.getElementsByTagName('path')[0].attributes.items())

            if 'inkscape:path-effect' in path_dict.keys() and not original_only:
                path_id = path_dict['inkscape:path-effect'].replace('#', '')  # '#path-effect2437' is referenced in 'defs' without the '#'
                for pe in svg.getElementsByTagName('inkscape:path-effect'):
                    attrs = dict(pe.attributes.items())
                    if attrs['effect'] == 'roughen' and path_id in attrs.values():   # any([at in path_id for at in attrs.values()]):  # attrs['id'] = 'path-effect2437', without the octothorp
                        # create MorphedShape, pass path and attrs
                        self.shape = SVGShape(path_dict, attrs)
                        break
            else:
                self.shape = SVGShape(path_dict)

    def path(self, original=False):
        # TODO distinction
        return self.shape.path

    def get_path(self):
        return self.shape.path
