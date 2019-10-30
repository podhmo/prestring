import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, "README.rst")) as f:
        README = f.read()
    with open(os.path.join(here, "CHANGES.txt")) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ""


install_requires = []
if sys.version_info[:2] <= (3, 6):
    install_requires.append("dataclasses")
dev_extras = ["black", "flake8"]
docs_extras = []
tests_require = ["evilunit"]
testing_extras = tests_require + []

setup(
    name="prestring",
    version=open(os.path.join(here, "VERSION")).read().strip(),
    description="source code generation library (with overuse with-syntax)",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="prestring, srcgen, python",
    author="podhmo",
    author_email="ababjam61@gmail.com",
    url="https://github.com/podhmo/prestring",
    packages=find_packages(exclude=["prestring.tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"testing": testing_extras, "docs": docs_extras, "dev": dev_extras},
    tests_require=tests_require,
    test_suite="prestring.tests",
    entry_points="""
""",
)
