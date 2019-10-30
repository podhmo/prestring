import sys
import logging
from os.path import join, exists
from os import mkdir


class AskStringCache(object):
    prompt = "{varname} ({description})[{default!r}]:"

    def __init__(self, inp=sys.stdin, err=sys.stderr):
        self.description_map = {}
        self.default_map = {}
        self.cache = {}
        self.inp = inp
        self.err = err
        self.hooks = []

    def __getitem__(self, name):
        try:
            return self.cache[name]
        except KeyError:
            return self.load(name)

    def load(self, name):
        description = self.description_map.get(name, "")
        default = self.default_map.get(name)
        self.err.write(
            self.prompt.format(varname=name, description=description, default=default)
        )
        self.err.flush()
        value = self.inp.readline().rstrip() or self.default_map.get(name, "")
        self.cache[name] = value
        return value

    def add_description(self, name, description):
        self.description_map[name] = description

    def add_default(self, name, default):
        self.default_map[name] = default


_ask_string_cache = AskStringCache()


def get_ask_string_cache():
    global _ask_string_cache
    return _ask_string_cache


def set_ask_string_cache(cache):
    global _ask_string_cache
    _ask_string_cache = cache


class AskString(object):
    def __init__(self, name, description=None, default=None, cache=None):
        self.cache = cache or get_ask_string_cache()
        self.name = name
        if description is not None:
            self.cache.add_description(name, description)
        if default is not None:
            self.cache.add_default(name, default)

    def __str__(self):
        return self.cache[self.name]


_G0 = AskString("package", description="package name", default="foo-bar")
_G1 = AskString("version", description="version", default="0.0.0")
logger = logging.getLogger(__name__)


def gen(rootpath):
    file0 = join(rootpath, "").replace("<<_G0>>", str(_G0)).replace("<<_G1>>", str(_G1))
    file1 = (
        join(rootpath, "<<_G0>>")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    file2 = (
        join(rootpath, "<<_G0>>/.gitignore")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    val0 = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]

# C extensions
*.so

# Distribution / packaging
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml

# Translations
*.mo
*.pot

# Django stuff:
*.log

# Sphinx documentation
docs/_build/

# PyBuilder
target/
""".replace(
        "<<_G0>>", str(_G0)
    ).replace(
        "<<_G1>>", str(_G1)
    )
    file3 = (
        join(rootpath, "<<_G0>>/README.rst")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    val1 = """<<_G0>>========================================""".replace(
        "<<_G0>>", str(_G0)
    ).replace("<<_G1>>", str(_G1))
    file4 = (
        join(rootpath, "<<_G0>>/CHANGES.rst")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    val2 = """""".replace("<<_G0>>", str(_G0)).replace("<<_G1>>", str(_G1))
    file5 = (
        join(rootpath, "<<_G0>>/<<_G0>>")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    file6 = (
        join(rootpath, "<<_G0>>/<<_G0>>/__init__.py")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    file7 = (
        join(rootpath, "<<_G0>>/<<_G0>>/tests")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    file8 = (
        join(rootpath, "<<_G0>>/<<_G0>>/tests/__init__.py")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    file9 = (
        join(rootpath, "<<_G0>>/setup.py")
        .replace("<<_G0>>", str(_G0))
        .replace("<<_G1>>", str(_G1))
    )
    val3 = """import os
from setuptools import(
    setup,
    find_packages
)
here = os.path.abspath(os.path.dirname(__file__))


try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.rst')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''


install_requires = []
docs_extras = []
tests_requires = []
testing_extras = tests_requires + []


setup(
    name='<<_G0>>',
    version='<<_G1>>',
    classifiers=['Programming Language :: Python', 'Programming Language :: Python :: Implementation :: CPython'],
    keywords='',
    author='',
    author_email='',
    url='',
    packages=find_packages(exclude=['<<_G0>>.tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
   'testing': testing_extras,
   'docs': docs_extras},
    tests_require=tests_requires,
    test_suite='<<_G0>>.tests',
    entry_points='')""".replace(
        "<<_G0>>", str(_G0)
    ).replace(
        "<<_G1>>", str(_G1)
    )
    if not (exists(file0)):
        logger.info("[d] create: %s", file0)
        mkdir(file0)
    if not (exists(file1)):
        logger.info("[d] create: %s", file1)
        mkdir(file1)
    logger.info("[f] create: %s", file2)
    with open(file2, "w") as wf:
        wf.write(val0)
    logger.info("[f] create: %s", file3)
    with open(file3, "w") as wf:
        wf.write(val1)
    logger.info("[f] create: %s", file4)
    with open(file4, "w") as wf:
        wf.write(val2)
    if not (exists(file5)):
        logger.info("[d] create: %s", file5)
        mkdir(file5)
    logger.info("[f] create: %s", file6)
    with open(file6, "w") as wf:
        wf.write(val2)
    if not (exists(file7)):
        logger.info("[d] create: %s", file7)
        mkdir(file7)
    logger.info("[f] create: %s", file8)
    with open(file8, "w") as wf:
        wf.write(val2)
    logger.info("[f] create: %s", file9)
    with open(file9, "w") as wf:
        wf.write(val3)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gen(sys.argv[1])
