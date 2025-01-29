Installation
============

Dendrify is available on the Python Package Index (PyPI): https://pypi.org/project/dendrify.
The easiest way to install it is through ``pip``, using the command::
  
  pip install dendrify

This command will automatically install the latest version of Brian 2 and other
optional dependencies (recommended for most users). If you prefer to install
Dendrify without any of its dependencies, you can use the command::

  pip install dendrify --no-deps

Dependencies
------------

* :doc:`Brian 2 <brian2:index>` (required) is a simulator for
  spiking neural networks. It is written in Python and is available
  on almost all platforms. Brian is designed to be easy to learn and use,
  highly flexible, and easily extensible.
  
  * :doc:`Brian 2 installation guidelines <brian2:introduction/install>`


* :doc:`Matplotlib <matplotlib:index>` (optional) is a comprehensive Python
  library for creating static, animated, and interactive visualizations. If you 
  wish to use dSpike Playground, you can install it using the command::

    pip install matplotlib


* :doc:`Networkx <networkx:index>` (optional) is a Python package for the creation,
  manipulation, and study of the structure, dynamics, and functions of complex
  networks. If you wish to create graph-like representations of multicompartmental
  models, you can install it with the command::

    pip install networkx


GPU support
-----------
Dendrify is compatible with :doc:`Brian2CUDA <brian2cuda:index>`,
a Python package for simulating spiking neural networks on graphics processing
units (GPUs). Brian2CUDA is an extension of Brian2 that uses the code generation
system of the latter to generate simulation code in C++/CUDA, which is then
executed on NVIDIA GPUs.

* :doc:`Brian2CUDA installation guidelines <brian2cuda:introduction/install>`
