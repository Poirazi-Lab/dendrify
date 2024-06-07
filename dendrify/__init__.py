from .compartment import Compartment, Dendrite, Soma
from .ephysproperties import (EphysProperties, default_params,
                              update_default_params)
from .equations import library
from .neuronmodel import NeuronModel, PointNeuronModel

__version__ = '2.1.4'
__author__ = 'Michalis Pagkalos'
__email__ = 'mpagkalos93@gmail.com'
