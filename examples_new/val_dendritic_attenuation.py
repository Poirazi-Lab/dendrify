"""
Title
-----
Dendritic attenuation

Description
-----------
The attenuation of currents traveling along the somatodendritic axis is an
intrinsic property of biological neurons and is due to the morphology and cable
properties of their dendritic trees. (also see `Tran-van-Minh et al, 2015 
<https://www.frontiersin.org/articles/10.3389/fncel.2015.00067>`_).

In this example, we show:

- How to measure thr distance-dependent voltage attenuation of a long current
pulse injected at the soma.

"""

import brian2 as b
from brian2.units import cm, ms, mV, nS, ohm, pF, uF, um, uS

from dendrify import Dendrite, NeuronModel, Soma

b.prefs.codegen.target = 'numpy' # faster for simple simulations

# Create neuron model
soma = Soma('soma', length=30*um, diameter=30*um)
trunk = Dendrite('trunk', length=100*um, diameter=2*um)
prox = Dendrite('prox', length=100*um, diameter=1.25*um)
dist = Dendrite('dist', length=100*um, diameter=0.8*um)

# Create a neuron group
connections = [(soma, trunk), (trunk, prox), (prox, dist)]
model = NeuronModel(connections, cm=1*uF/(cm**2), gl=40*uS/(cm**2),
                    v_rest=-70*mV, r_axial=150*ohm*cm)
neuron = model.make_neurongroup(1, method='euler')

# Monitor voltages

M = b.StateMonitor(neuron, ['V_soma', 'V_trunk', 'V_prox', 'V_dist'], record=True)

# Run simulation
