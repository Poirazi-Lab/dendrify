Installation
============

Dendrify is included in the Python package index: https://pypi.org/project/dendrify.
The easiest way to install it is through ``pip``, using the command::
  
  pip install dendrify

The above command will automatically install Brian 2.5.4, if it is not already
installed. If you wish to work with a different version of Brian, you can do so
using the command::

  pip install dendrify --no-deps

and then install the desired version of Brian separately (see bellow).

Dependencies
------------

* `Brian 2 <https://brian2.readthedocs.io/en/stable/index.html>`_ (required) is
  a simulator for spiking neural networks. It is written in Python and is available
  on almost all platforms. Brian is designed to be easy to learn and use, highly
  flexible and easily extensible.
  
  * :doc:`How to install Brian 2 <brian2:introduction/install>`
  
* `Networkx <https://networkx.org/>`_ (optional) is a Python package for the creation,
  manipulation, and study of the structure, dynamics, and functions of complex
  networks. If you wish Dendrify to have access to certain experimental model
  visualization features, you can install it using the command::

    pip install networkx


GPU support
-----------
Dendrify is compatible with `Brian2CUDA <https://brian2cuda.readthedocs.io/>`_,
a Python package for simulating spiking neural networks on graphics processing
units (GPUs). Brian2CUDA is an extension of Brian2 that uses the code generation
system of the latter to generate simulation code in C++/CUDA, which is then executed
on NVIDIA GPUs.

* :doc:`How to install Brian2CUDA <brian2cuda:introduction/install>`

