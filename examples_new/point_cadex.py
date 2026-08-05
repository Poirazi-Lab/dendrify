"""
Title
-----
CAdEx neuron + noise

Description
-----------
The Dendrify implementation of the Conductance-based adaptive exponential integrate-and-fire model

In this example, we also explore:

- How to add brian2 specific flags in the equations

Resources:

- https://doi.org/10.1162/neco_a_01342
"""


import brian2 as b
from brian2.units import ms, mV, nA, nS, pA, pF

from dendrify import PointNeuronModel

b.prefs.codegen.target = 'numpy'  # faster for simple simulations
b.seed(1234)  # for reproducibility

# parameters
params = {'Vth': -50*mV,
          'DeltaT': 2*mV,
          'tauA': 200*ms,
          'gAmax': 10*nS,
          'delta_gA': 10*nS,
          'DeltaA': 5*mV,
          'EA': -70*mV,
          'VA': -40*mV,
          'VD': -40*mV,
          'Vr': -70*mV}


# Create neuron model
model_a = PointNeuronModel(model='cadex',
                           cm_abs=200*pF,
                           gl_abs=10*nS,
                           v_rest=-70*mV)

model_a.add_params(params)

# Create neuron model
model_b = PointNeuronModel(model='cadex',
                           cm_abs=200*pF,
                           gl_abs=10*nS,
                           v_rest=-70*mV)

# Update model's equation to add brian2 flag `unless_refractory`
# for more see: <https://brian2.readthedocs.io/en/latest/user/refractoriness.html>`_
updated_eq_str = model_b.equations.replace(':volt', ':volt (unless refractory)')
model_b.replace_equations(model_b.equations, updated_eq_str)

model_b.add_params(params)

# Create a NeuronGroup
neuron_a = model_a.make_neurongroup(N=1, threshold='V>VD',
                                    reset='V=Vr; gA+=delta_gA',
                                    refractory=5*ms,
                                    method='euler')

neuron_b = model_b.make_neurongroup(N=1, threshold='V>VD',
                                    reset='V=Vr; gA+=delta_gA',
                                    refractory=5*ms,
                                    method='euler')

# Record voltages and gA
trace_a = b.StateMonitor(neuron_a, ['V', 'gA'], record=True)
trace_b = b.StateMonitor(neuron_b, ['V', 'gA'], record=True)
spikes_a = b.SpikeMonitor(neuron_a)
spikes_b = b.SpikeMonitor(neuron_b)

# Run simulation
b.run(20 * ms)
neuron_a.I_ext = 1.2*nA
neuron_b.I_ext = 1.2*nA
b.run(1000 * ms)
neuron_a.I_ext = 0*nA
neuron_b.I_ext = 0*nA
b.run(500 * ms)

# Trick to draw nicer spikes in I&F models
vm_a = trace_a[0].V[:]
vm_b = trace_b[0].V[:]
for t1, t2 in zip(spikes_a.t, spikes_b.t):
    i = int(t1 / b.defaultclock.dt)
    j = int(t2 / b.defaultclock.dt)
    vm_a[i] = 20*mV
    vm_b[j] = 20*mV

# Plot the results
fig, axes = b.subplots(2, 2, figsize=[10, 6], sharex=True)
ax1, ax2 = axes

axes[0,0].plot(trace_a.t / ms, vm_a / mV)
axes[0,0].set_ylabel('Voltage (mV)')
axes[0,0].set_title('no clamped V during refractory')

axes[0,1].plot(trace_b.t / ms, vm_b / mV)
axes[0,1].set_ylabel('Voltage (mV)')
axes[0,1].set_title('clamped V during refractory')

axes[1,0].plot(trace_a.t / ms, trace_a[0].gA[:] / nS)
axes[1,0].set_ylabel('gA (nS)')
axes[1,0].set_xlabel('Time (ms)')

axes[1,1].plot(trace_b.t / ms, trace_b[0].gA[:] / nS)
axes[1,1].set_ylabel('gA (nS)')
axes[1,1].set_xlabel('Time (ms)')
fig.tight_layout()
b.show()