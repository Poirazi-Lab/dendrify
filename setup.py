from setuptools import find_packages, setup

VERSION = '2.1.0'
DESCRIPTION = 'A package for adding dendrites to SNNs'
with open("README.rst") as f:
    LONG_DESCRIPTION = f.read()

# Setting up
setup(
    name="dendrify",
    version=VERSION,
    author="Michalis Pagkalos",
    author_email="<mpagkalos93@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/x-rst; charset=UTF-8",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['brian2==2.5.4'],
    keywords=['python', 'brian2', 'dendrites', 'SNNs', 'network models'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    project_urls={
        'Documentation': 'https://dendrify.readthedocs.io/en/latest/',
        'Source': 'https://github.com/Poirazi-Lab/dendrify',
        'Tracker': 'https://github.com/Poirazi-Lab/dendrify/issues'
    }
)
