Somatic
=======

Brian requires models to be expressed as systems of first order ordinary differential equations,
and the effect of spikes to be expressed as (possibly delayed) one-off changes. However, many
neuron models are given in *integrated form*. For example, one form of the Spike Response Model
(SRM; Gerstner and Kistler 2002) is defined as

.. math::


where :math:`V(t)` is the membrane potential, :math:`V_\mathrm{rest}` is the rest potential,
:math:`w_i` is the synaptic weight of synapse :math:`i`, and :math:`t_i` are the timings of
the spikes coming from synapse :math:`i`, and PSP is a postsynaptic potential function.