Dendritic attenuation
=====================


The attenuation of currents traveling along the somatodendritic axis is an
intrinsic property of biological neurons and is due to the morphology and cable
properties of their dendritic trees. (also see `Tran-van-Minh et al, 2015 
<https://www.frontiersin.org/articles/10.3389/fncel.2015.00067>`_).

In this example, we show:

- How to measure the dendritic, distance-dependent voltage attenuation of a long
  current pulse injected at the soma.



.. code-block:: python

    import brian2 as b
    from brian2.units import cm, ms, mV, ohm, pA, pF, uF, um, uS
    
    from dendrify import Dendrite, NeuronModel, Soma
    
    b.prefs.codegen.target = 'numpy'  # faster for simple simulations
    
    # Create neuron model
    soma = Soma('soma', length=25*um, diameter=25*um)
    trunk = Dendrite('trunk', length=100*um, diameter=1.5*um)
    prox = Dendrite('prox', length=100*um, diameter=1.2*um)
    dist = Dendrite('dist', length=100*um, diameter=1*um)
    
    # Create a neuron group
    connections = [(soma, trunk), (trunk, prox), (prox, dist)]
    model = NeuronModel(connections, cm=1*uF/(cm**2), gl=50*uS/(cm**2),
                        v_rest=-70*mV, r_axial=400*ohm*cm)
    neuron = model.make_neurongroup(1, method='euler')  # no spiking for simplicity
    
    # Monitor voltages
    M = b.StateMonitor(neuron, ['V_soma', 'V_trunk', 'V_prox', 'V_dist'],
                       record=True)
    
    # Run simulation
    b.run(20*ms)
    neuron.I_ext_soma = -10*pA
    b.run(500*ms)
    neuron.I_ext_soma = 0*pA
    b.run(100*ms)
    
    # Analyse and plot results
    time = M.t/ms
    vs = M.V_soma[0]/mV
    vt = M.V_trunk[0]/mV
    vp = M.V_prox[0]/mV
    vd = M.V_dist[0]/mV
    voltages = [vs, vt, vp, vd]
    delta_v = [min(v) - v[0] for v in voltages]
    ratio = [i/delta_v[0] for i in delta_v]
    distances = range(0, 400, 100)
    names = ['soma', 'trunk', 'prox', 'dist']
    
    fig, axes = b.subplots(1, 2, figsize=(6, 3))
    ax0, ax1 = axes
    for i, v in enumerate(voltages):
        ax0.plot(time, v, label=names[i])
    ax0.set_ylabel('Voltage (mV)')
    ax0.set_xlabel('Time (ms)')
    ax0.legend()
    
    ax1.plot(distances, ratio, 'ko-', ms=4)
    ax1.set_ylabel(r'$dV_{dend}$ / $dV_{soma}$')
    ax1.set_xlabel('Distance from soma (μm)')
    ax1.set_yticks(b.arange(.7, 1, .1))
    
    fig.tight_layout()
    b.show()


.. image:: _static/val_dendritic_attenuation.png
   :align: center