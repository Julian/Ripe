from setuptools import find_packages, setup

from ripe import __version__


with open("README.rst") as readme:
    long_description = readme.read()


classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.1",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
]

setup(
    name="ripe",
    version=__version__,
    packages=find_packages(),
    author="Julian Berman",
    author_email="Julian@GrayVines.com",
    classifiers=classifiers,
    description="",
    license="MIT/X",
    long_description=long_description,
    url="http://github.com/Julian/Ripe",
    entry_points={"console_scripts" : ["ripe = ripe.cmdline:main"]},
    install_requires=["rply"],
    dependency_links = [
        "https://github.com/alex/rply/archive/master.tar.gz#egg=rply-dev",
    ],
)
