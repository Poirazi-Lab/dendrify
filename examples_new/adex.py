import brian2 as b
from brian2.units import ms, mV, nA, nS, pA, pF

from dendrify import PointNeuronModel

b.prefs.codegen.target = 'numpy'  # faster for simple simulations

# Create model
model = PointNeuronModel(model='adex',
                         cm_abs=281*pF,
                         gl_abs=30*nS, 
                         v_rest=-70.6*mV)

model.add_params({'Vth': -50.4*mV,
                  'DeltaT': 2*mV,
                  'tauw': 144*ms,
                  'a': 4*nS,
                  'b': 0.0805*nA,
                  'Vr': -70.6*mV,
                  'Vcut': -50.4*mV + 5 * 2*mV})


# Create a NeuronGroup
neuron = model.make_neurongroup(N=1,
                                threshold='V>Vcut',
                                reset='V=Vr; w+=b',
                                method='euler')

# Add noise and create a new NeuronGroup
model.noise(mean=20*pA, sigma=200*pA, tau=10*ms)
noisy_neuron = model.make_neurongroup(N=1,
                                      threshold='V>Vcut',
                                      reset='V=Vr; w+=b',
                                      method='euler')



# Set monitors
trace = b.StateMonitor(neuron, 'V', record=True)
spikes = b.SpikeMonitor(neuron)
noisy_trace = b.StateMonitor(noisy_neuron, 'V', record=True)
noisy_spikes = b.SpikeMonitor(noisy_neuron)

# Run simulation
b.run(20 * ms)
neuron.I_ext = 1*nA
noisy_neuron.I_ext = 1*nA
b.run(100 * ms)
neuron.I_ext = 0*nA
noisy_neuron.I_ext = 0*nA
b.run(20 * ms)

# Trick to draw nicer spikes
vm = trace[0].V[:]
for t in spikes.t:
    i = int(t / b.defaultclock.dt)
    vm[i] = 20*mV

noisy_vm = noisy_trace[0].V[:]
for t in noisy_spikes.t:
    i = int(t / b.defaultclock.dt)
    noisy_vm[i] = 20*mV

# Plot results
fig, axes = b.subplots(2, 1, figsize=[6, 6])
ax1, ax2 = axes
ax1.plot(trace.t / ms, vm / mV)
ax1.set_ylabel('Voltage (mV)')
ax2.plot(noisy_trace.t / ms, noisy_vm / mV)
ax2.set_ylabel('Voltage (mV)')
ax2.set_xlabel('Time (ms)')
fig.tight_layout()
b.show()




