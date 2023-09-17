"""
Title
-----
Understanding dSpikes

Description
-----------
Dendrify introduces a new event-driven mechanism for modeling dendritic spiking,
which is significantly simpler and more efficient than the traditional
Hodgkin-Huxley formalism. This mechanism has three distinct phases.

**INACTIVE PHASE:** 
When the dendritic voltage is subthreshold OR the simulation step is within the
refractory period. dSpikes cannot be generated during this phase.

**RISE PHASE:**
When the dendritic voltage crosses the dSpike threshold AND the refractory
period has elapsed. This triggers the instant activation of a positive current
that is deactivated after a specified amount of time (``duration_rise``). Also a
new refractory period begins.

**FALL PHASE:** 
This phase starts automatically with a delay (``offset_fall``) after the dSpike
threshold is crossed. A negative current is activated instantly and then is
deactivated after a specified amount of time (``duration_fall``).


In this example:

- How dendritic spiking is implemented in Dendrify.
"""

import brian2 as b
from brian2.units import ms, mV, nS, pF

from dendrify import Dendrite, NeuronModel, Soma

b.prefs.codegen.target = 'numpy' # faster for simple simulations

# Create neuron model
soma = Soma('soma', cm_abs=200*pF, gl_abs=10*nS)
dend = Dendrite('dend', cm_abs=50*pF, gl_abs=2.5*nS)
dend.dspikes('Na', g_rise=30*nS, g_fall=15*nS)
dend.synapse('AMPA', tag='x', g=3*nS,  t_decay=2*ms)
dend.synapse('NMDA', tag='x', g=3*nS,  t_decay=50*ms)

model = NeuronModel([(soma, dend, 15*nS)], v_rest=-65*mV)
model.config_dspikes('Na', threshold=-35*mV,
                     duration_rise=1.2*ms, duration_fall=2.4*ms,
                     offset_fall=0.2*ms, refractory=5*ms,
                     reversal_rise='E_Na', reversal_fall='E_K')

