#!/usr/bin/env python

import os
from distutils.core import setup

requirements = []

PACKAGE_NAME = 'crasa'
__version__ = '1.0.2'

setup(name = PACKAGE_NAME,
    version = __version__,
    description = "Simple Python Interface to CASA",
    author = "Sphesihle Makhathini",
    author_email = "sphemakh@gmail.com",
    url = "https://github.com/SpheMakh/crasa",
    packages=["Crasa"], 
    install_requires = requirements,
    include_package_data = True,
    license=["GNU GPL v2"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Astronomy"
    ]
     )
