import sys
import logging
import dataclasses
from prestring.output import output


@dataclasses.dataclass
class Config:
    name: str = dataclasses.field(
        default="foo-bar", metadata={"description": "package name"}
    )
    version: str = dataclasses.field(
        default="0.0.0", metadata={"description": "version"}
    )


def gen(rootpath: str, c: Config) -> None:
    file2 = f"{c.name}/.gitignore"
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
    file3 = f"{c.name}/README.rst"
    val1 = """<<c.name>>========================================""".replace(
        "<<c.name>>", str(c.name)
    ).replace("<<c.version>>", str(c.version))

    file4 = f"{c.name}/CHANGES.rst"
    val2 = """""".replace("<<c.name>>", str(c.name)).replace(
        "<<c.version>>", str(c.version)
    )
    file6 = f"{c.name}/{c.name}/__init__.py"
    file8 = f"{c.name}/{c.name}/tests/__init__.py"
    file9 = f"{c.name}/setup.py"
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
    with output(rootpath) as fs:
        with fs.open(file2, "w") as wf:
            wf.write(val0)
        with fs.open(file3, "w") as wf:
            wf.write(val1)
        with fs.open(file4, "w") as wf:
            wf.write(val2)
        with fs.open(file6, "w") as wf:
            wf.write(val2)
        with fs.open(file8, "w") as wf:
            wf.write(val2)
        with fs.open(file9, "w") as wf:
            wf.write(val3)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root_path = sys.argv[1]
    c = Config()
    gen(root_path, c)
