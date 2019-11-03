import sys
import logging
from os.path import join, exists
from os import mkdir
import dataclasses

# prompt = "{varname} ({description})[{default!r}]:"
@dataclasses.dataclass
class Config:
    name: str = dataclasses.field(
        default="foo-bar", metadata={"description": "package name"}
    )
    version: str = dataclasses.field(
        default="0.0.0", metadata={"description": "version"}
    )


# _G0 = AskString("package", description="package name", default="foo-bar")
# c.version = AskString("version", description="version", default="0.0.0")
logger = logging.getLogger(__name__)


def gen(rootpath: str, c: Config) -> None:
    file0 = (
        join(rootpath, "")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
    )
    file1 = (
        join(rootpath, "<<c.name>>")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
    )
    file2 = (
        join(rootpath, "<<c.name>>/.gitignore")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
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
        "<<c.name>>", str(c.name)
    ).replace(
        "<<c.version>>", str(c.version)
    )
    file3 = (
        join(rootpath, "<<c.name>>/README.rst")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
    )
    val1 = """<<c.name>>========================================""".replace(
        "<<c.name>>", str(c.name)
    ).replace("<<c.version>>", str(c.version))
    file4 = (
        join(rootpath, "<<c.name>>/CHANGES.rst")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
    )
    val2 = """""".replace("<<c.name>>", str(c.name)).replace(
        "<<c.version>>", str(c.version)
    )
    file5 = (
        join(rootpath, "<<c.name>>/<<c.name>>")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
    )
    file6 = (
        join(rootpath, "<<c.name>>/<<c.name>>/__init__.py")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
    )
    file7 = (
        join(rootpath, "<<c.name>>/<<c.name>>/tests")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
    )
    file8 = (
        join(rootpath, "<<c.name>>/<<c.name>>/tests/__init__.py")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
    )
    file9 = (
        join(rootpath, "<<c.name>>/setup.py")
        .replace("<<c.name>>", str(c.name))
        .replace("<<c.version>>", str(c.version))
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
    name='<<c.name>>',
    version='<<c.version>>',
    classifiers=['Programming Language :: Python', 'Programming Language :: Python :: Implementation :: CPython'],
    keywords='',
    author='',
    author_email='',
    url='',
    packages=find_packages(exclude=['<<c.name>>.tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
   'testing': testing_extras,
   'docs': docs_extras},
    tests_require=tests_requires,
    test_suite='<<c.name>>.tests',
    entry_points='')""".replace(
        "<<c.name>>", str(c.name)
    ).replace(
        "<<c.version>>", str(c.version)
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
    root_path = sys.argv[1]
    c = Config()
    gen(root_path, c)
