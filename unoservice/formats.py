from lxml import etree
from collections import defaultdict, OrderedDict
from celestial import normalize_mimetype
from unoservice.util import parse_extensions

NS = {'oor': 'http://openoffice.org/2001/registry'}
NAME = '{%s}name' % NS['oor']


class Formats(object):
    FILES = [
        '/usr/lib/libreoffice/share/registry/writer.xcd',
        '/usr/lib/libreoffice/share/registry/impress.xcd',
        '/usr/lib/libreoffice/share/registry/draw.xcd',
        # '/usr/lib/libreoffice/share/registry/calc.xcd',
    ]

    def __init__(self):
        self.media_types = defaultdict(list)
        self.extensions = defaultdict(list)
        for xcd_file in self.FILES:
            doc = etree.parse(xcd_file)
            path = './*[@oor:package="org.openoffice.TypeDetection"]/node/node'
            for tnode in doc.xpath(path, namespaces=NS):
                node = {}
                for prop in tnode.findall('./prop'):
                    name = prop.get(NAME)
                    for value in prop.findall('./value'):
                        node[name] = value.text

                name = node.get('PreferredFilter', tnode.get(NAME))
                media_type = normalize_mimetype(node.get('MediaType'),
                                                default=None)
                if media_type is not None:
                    self.media_types[media_type].append(name)

                for ext in parse_extensions(node.get('Extensions')):
                    self.extensions[ext].append(name)

    def get_filters(self, extension, media_type):
        filters = OrderedDict()
        for filter_name in self.media_types.get(media_type, []):
            filters[filter_name] = None
        for filter_name in self.extensions.get(extension, []):
            filters[filter_name] = None
        return filters.keys()

    def to_json(self):
        return {
            'media_types': dict(self.media_types),
            'extensions': dict(self.extensions),
        }


if __name__ == "__main__":
    formats = Formats()
    print(formats.get_filters('doc', None))