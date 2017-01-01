# -*- coding:utf-8 -*-
import logging
import os.path
import glob
from collections import namedtuple, defaultdict


logger = logging.getLogger(__name__)
File = namedtuple("File", "name, m")


class SeparatedOutput(object):
    @staticmethod
    def module_factory():
        raise NotImplementedError("e.g. python.PythonModule()")

    def __init__(self, dirname, prefix="autogen_", module_factory=None):
        self.dirname = dirname
        self.prefix = prefix
        self.arrived = set()
        self.files = defaultdict(self.new_file)
        self.module_factory = module_factory or self.__class__.module_factory

    def new_file(self, file_name, m=None):
        dirname, basename = os.path.split(file_name)
        fname = "{}{}".format(self.prefix, basename)
        m = m or self.module_factory()
        return File(name=os.path.join(dirname, fname), m=m)

    def prepare(self, f):
        dirname = os.path.dirname(f.name)
        if dirname in self.arrived:
            return
        self.arrived.add(dirname)
        logger.info("make directory path=%s", dirname)
        os.makedirs(dirname, exist_ok=True)
        if self.prefix:
            for f in glob.glob(os.path.join(dirname, "{}*.py".format(self.prefix))):
                os.remove(f)

    def output(self):
        for file in self.files.values():
            self.output_file(file)

    def output_file(self, file):
        self.prepare(file)

        path = os.path.join(self.dirname, file.name)
        logger.info("make file path=%s", path)
        with open(path, "w") as wf:
            wf.write(str(file.m))
