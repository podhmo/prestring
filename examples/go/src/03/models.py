import copy
import json
import logging
import os.path
from prestring.go import Module


logger = logging.getLogger(__name__)


class Reader(object):
    def read_world(self, data, parent=None):
        world = World(parent=parent, reader=self)
        for name, module in data["module"].items():
            world.read_module(name, module)
        return world

    def read_module(self, data, parent=None):
        module = Module(data["name"], parent=parent, reader=self)
        for name, file in data["file"].items():
            module.read_file(name, file)
        return module

    def read_file(self, data, parent=None):
        file = File(data["name"], parent=parent, reader=self)
        for name, alias in data["alias"].items():
            file.read_alias(name, alias)
        for name, struct in data["struct"].items():
            file.read_struct(name, struct)
        return file

    def read_struct(self, data, parent=None):
        struct = Struct(data["name"], data, parent=parent, reader=self)
        return struct

    def read_alias(self, data, parent=None):
        alias = Alias(data["name"], data, parent=parent, reader=self)
        return alias


class GOWriter(object):
    prestring_module = Module

    def write_file(self, file, m=None):
        m = m or self.prestring_module()
        self.write_packagename(file, m=m)
        for struct in file.structs.values():
            self.write_struct(struct, m=m)
        for alias in file.aliases.values():
            self.write_alias(alias, m=m)
        return m

    def write_packagename(self, file, m=None):
        m = m or self.prestring_module()
        package_name = file.package_name
        if package_name is not None:
            m.package(package_name)
        return m

    def write_struct(self, struct, m=None):
        m = m or self.prestring_module()
        struct = struct.data
        self.write_comment(struct, m=m)
        with m.type_(struct["name"], "struct"):
            for field in sorted(struct["fields"].values(), key=lambda f: f["name"]):
                self.write_comment(field, m=m)
                if field["embed"]:
                    m.stmt(as_type(field["type"]))
                else:
                    m.stmt("{} {}".format(field["name"], as_type(field["type"])))
                if "tags" in field:
                    m.insert_after("  ")
                    for tag in field["tags"]:
                        m.insert_after(tag)
        return m

    def write_alias(self, alias, m=None):
        m = m or self.prestring_module()
        alias = alias.data
        m.type_alias(alias["name"], alias["original"]["value"])
        with m.const_group() as const:
            for c in alias.get("candidates", []):
                self.write_comment(c, m=const) or const.comment("{} : a member of {}".format(c["name"], alias["name"]))
                const("{} {} = {}".format(c["name"], alias["name"], c["value"]))
        return m

    def write_comment(self, target, m=None):
        m = m or self.prestring_module()
        if "comment" in target:
            m.comment(target["comment"])
            return m
        else:
            return None


def as_type(type_dict):
    kind = type_dict.get("kind", "primitive")
    if kind == "primitive":
        return type_dict["value"]
    elif kind == "pointer":
        return "*{}".format(as_type(type_dict["value"]))
    elif kind == "selector":
        return "{}".format(type_dict["value"])
    else:
        raise ValueError("unknown type: {}".format(type_dict))


class World(object):
    def __init__(self, parent=None, reader=None):
        self.parent = parent
        self.reader = reader
        self.modules = {}

    def read_module(self, name, module):
        self.modules[name] = self.reader.read_module(module, parent=self)

    def normalize(self):
        for module in self.modules.values():
            module.normalize()


class Module(object):
    def __init__(self, name, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.files = {}

    def read_file(self, name, file):
        self.files[name] = self.reader.read_file(file, parent=self)

    def normalize(self):
        for files in self.files.values():
            files.normalize()


class File(object):
    def __init__(self, name, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.aliases = {}
        self.structs = {}

    @property
    def package_name(self):
        if self.parent is None:
            return None
        return self.parent.name

    def normalize(self):
        for struct in self.structs.values():
            struct.normalize()
        for alias in self.aliases.values():
            alias.normalize()

    def read_alias(self, name, alias):
        self.aliases[name] = self.reader.read_alias(alias, parent=self)

    def read_struct(self, name, struct):
        self.structs[name] = self.reader.read_struct(struct, parent=self)

    def dump(self, writer):
        return writer.write_file(self)


class Alias(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.data = data

    def dump(self, writer):
        return writer.write_alias(self)

    def normalize(self):
        pass


class Struct(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.rawdata = data
        self.data = data

    def dump(self, writer):
        return writer.write_struct(self)

    def normalize(self):
        self.rawdata = copy.deepcopy(self.rawdata)
        for k in list(self.data.keys()):
            self.data[k.lower()] = self.data.pop(k)


def main():
    fname = os.path.join(os.path.abspath(os.path.dirname(__file__)), "./models.json")
    writer = GOWriter()
    reader = Reader()
    with open(fname) as rf:
        data = json.load(rf)
        world = reader.read_world(data)
        world.normalize()
        # print(world)
        # print(world.modules["models"])
        # print(world.modules["models"].files["examples/models/person.go"])
        # print(world.modules["models"].files["examples/models/person.go"].structs["Person"])
        for name, file in world.modules["models"].files.items():
            outname = "output_{}".format(os.path.basename(file.name))
            logger.info("write %s", outname)
            print(file.dump(writer))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
