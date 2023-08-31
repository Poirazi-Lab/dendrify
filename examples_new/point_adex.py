import brian2 as b
from brian2.units import ms, mV, nA, nS, pA, pF

from dendrify import PointNeuronModel

b.prefs.codegen.target = 'numpy'  # faster for simple simulations

# Create neuron model
model = PointNeuronModel(model='adex',
                         cm_abs=281*pF,
                         gl_abs=30*nS, 
                         v_rest=-70.6*mV)

# Include adex parameters
model.add_params({'Vth': -50.4*mV,
                  'DeltaT': 2*mV,
                  'tauw': 144*ms,
                  'a': 4*nS,
                  'b': 0.0805*nA,
                  'Vr': -70.6*mV,
                  'Vcut': -50.4*mV + 5 * 2*mV})

# Create a NeuronGroup
neuron = model.make_neurongroup(N=1, threshold='V>Vcut',
                                reset='V=Vr; w+=b',
                                method='euler')

# Record voltages and spike times
trace = b.StateMonitor(neuron, 'V', record=True)
spikes = b.SpikeMonitor(neuron)

# Run simulation
b.run(20 * ms)
neuron.I_ext = 1*nA
b.run(100 * ms)
neuron.I_ext = 0*nA
b.run(20 * ms)

# Trick to draw nicer spikes in I&F models
vm = trace[0].V[:]
for t in spikes.t:
    i = int(t / b.defaultclock.dt)
    vm[i] = 20*mV

# Plot results
b.plot(trace.t / ms, vm / mV, label='V')
b.xlabel('Time (ms)')
b.ylabel('Voltage (mV)')
b.legend()
b.tight_layout()
b.show()