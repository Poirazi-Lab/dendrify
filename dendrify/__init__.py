from .compartment import Compartment, Dendrite, Soma
from .ephysproperties import (EphysProperties, default_params,
                              update_default_params)
from .equations import library
from .neuronmodel import NeuronModel, PointNeuronModel

from ._version import __version__

__author__ = 'Michalis Pagkalos'
__email__ = 'mpagkalos93@gmail.com'
