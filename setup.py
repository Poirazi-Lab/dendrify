from setuptools import find_packages, setup

VERSION = '1.0.2'
DESCRIPTION = 'A package for adding dendrites to SNNs'
LONG_DESCRIPTION = 'A package for adding dendrites to SNNs in Brian 2'

# Setting up
setup(
    name="dendrify",
    version=VERSION,
    author="Michalis Pagkalos",
    author_email="<mpagkalos93@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'brian2', 'dendrites', 'SNNs', 'network models'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
