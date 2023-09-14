"""
Title
-----
Dendritic I/O curve

Description
-----------
Dendritic integration can be quantified by comparing the observed depolarization
resulting from the simultaneous activation of the same synaptic inputs, also
called a compound EPSP, and the arithmetic sum of individual EPSPs (expected
membrane depolarization). The dendritic input-output (I/O) relationship is
easily described by plotting observed vs. expected depolarizations for different
numbers of co-activated synapses (also see `Tran-van-Minh et al, 2015 
<https://www.frontiersin.org/articles/10.3389/fncel.2015.00067>`_).

In this example, we show:

- How to calculate the dendritic I/O curve in a simple compartmental model.
- How active dendritic conductances affect the I/O curve.
- How to perform the above experiment in a vectorized and efficient manner.
"""

import brian2 as b
from brian2.units import ms, mV, nS, pA, pF

from dendrify import Dendrite, NeuronModel, Soma

b.prefs.codegen.target = 'numpy' # faster for simple simulations

# Create neuron model
soma = Soma('soma', cm_abs=200*pF, gl_abs=10*nS)
dend = Dendrite('dend', cm_abs=50*pF, gl_abs=2.5*nS)

model = NeuronModel([(soma, dend, 15*nS)], v_rest=-65*mV)
dend.synapse('AMPA', tag='x', g=3*nS,  t_decay=2*ms)
# dend.synapse('NMDA', tag='x', g=3*nS,  t_decay=60*ms)


# Experiment setup
Nsyn_d = 15    # 15 synapses are enough since distal dendrites are very excitable

# create a Brian NeuronGroup and link it to the neuron model
pyr_group2 = b.NeuronGroup(Nsyn_d, model=pyr_model.equations, method='euler',
                          refractory=4*ms, events=pyr_model.events,
                          namespace=pyr_model.parameters)
pyr_model.link(pyr_group2)

# synaptic protocol: Nsyn_d presynaptic spikes with isi of 0.1 ms commonly used
# by experimental labs
start = 20*ms
isi = 0.1*ms
spiketimes = [(start + (i*isi)) for i in range(Nsyn_d)]
I = b.SpikeGeneratorGroup(Nsyn_d, range(Nsyn_d), spiketimes)

synaptic_effect = "s_AMPA_pathX_dist += 1.0; s_NMDA_pathX_dist += 1.0"
S = b.Synapses(I, pyr_group2, on_pre=synaptic_effect)
S.connect('j >= i')



