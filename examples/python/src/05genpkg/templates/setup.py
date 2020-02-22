import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


try:
    with open(os.path.join(here, "README.rst")) as f:
        README = f.read()
    with open(os.path.join(here, "CHANGES.rst")) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ""


install_requires = []
docs_extras = []
tests_requires = []
testing_extras = tests_requires + []


setup(
    name="<<c.name>>",
    version="<<c.version>>",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords="",
    author="",
    author_email="",
    url="",
    packages=find_packages(exclude=["<<c.package_dirname>>.tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"testing": testing_extras, "docs": docs_extras},
    tests_require=tests_requires,
    test_suite="<<c.package_dirname>>.tests",
    entry_points="",
)
