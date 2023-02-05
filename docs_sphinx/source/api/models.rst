Model library
=============

.. image:: ../_static/under-construction.png
   :width: 20 %
   :align: center

.. note::

   Dendrify relies on Brian's :doc:`Equations-based <brian2:user/equations>`
   approach to define models as systems of first order ordinary differential
   equations. For convenience, Dendrify includes a library of default models
   (see below) however users can also provide custom model equations.

.. _somatic_models:

Somatic models [1]_ [2]_
------------------------

Leaky Integrate-and-Fire
~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   C\frac{dV}{dt}=-g_L(V-E_L)+I

where
:math:`C` is the membrane capacitance, 
:math:`V` the membrane potential, 
:math:`g_L` the leak conductance, 
:math:`E_L` the leak reversal potential and
:math:`I` is the input current.
When the firing threshold :math:`V_\theta` is crossed, :math:`V` resets to a
fixed value :math:`V_r`.

Adaptive Integrate-and-Fire
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   C\frac{dV}{dt}=-g_L(V-E_L)-w+I

.. math::

   \tau_w\frac{dw}{dt}=a(V-E_L)-w

where
:math:`w` is the adaptation variable, 
:math:`a` the adaptation coupling parameter and 
:math:`τ_w` is the adaptation time constant.
When the firing threshold :math:`V_\theta` is crossed, :math:`V` resets to a
fixed value :math:`V_r` and :math:`w \rightarrow w+b`, where :math:`b` is the 
spike-triggered adaptation current.


Adaptive Exponential Integrate-and-Fire
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. math::

   C\frac{dV}{dt}=-g_L(V-E_L)+g_L\Delta_T\exp\left(\frac{V-V_T}{\Delta_T}\right)-w+I

.. math::

   \tau_w\frac{dw}{dt}=a(V-E_L)-w

where
:math:`\Delta_T` is the slope factor and
:math:`V_T` the voltage threshold.
When the firing threshold :math:`V_\theta` is crossed, :math:`V` resets to a
fixed value :math:`V_r` and :math:`w \rightarrow w+b`, where :math:`b` is the 
spike-triggered adaptation current.

----

.. _dendritic_models:

Dendritic models
----------------



.. _synaptic_models:

Synaptic models [3]_ [4]_
-------------------------

AMPA
~~~~

.. math::

   I_{\text{AMPA}}=\bar{g}_{\text{AMPA}}(E_{\text{AMPA}}-V)s(t)

.. math::

   \frac{ds}{dt}=\frac{-s}{\tau_{\text{AMPA}}^{\text{decay}}}


where
:math:`\bar{g}_{\text{AMPA}}` is the AMPA synaptic conductance, 
:math:`s` the channel state variable,
:math:`E_{\text{AMPA}}` the AMPA reversal potential,
:math:`V` the membrane potential and 
:math:`\tau_{\text{AMPA}}^{\text{decay}}` the AMPA decay time constant. When a
pre-synaptic spike arrives :math:`s \rightarrow s+1`.

AMPA (rise & decay)
~~~~~~~~~~~~~~~~~~~~

.. math::

   I_{\text{AMPA}}=\bar{g}_{\text{AMPA}}(E_{\text{AMPA}}-V)x(t)

.. math::

   \frac{dx}{dt}=\frac{-x}{\tau_{\text{AMPA}}^{\text{decay}}}+s(t)

.. math::

   \frac{ds}{dt}=\frac{-s}{\tau_{\text{AMPA}}^{\text{rise}}}


where
:math:`s` and
:math:`x` describe the rise and decay kinetics of the channel respectively,
:math:`\tau_{\text{AMPA}}^{\text{rise}}` is the AMPA rise time constant and
:math:`\tau_{\text{AMPA}}^{\text{decay}}` is the AMPA decay time constant.
When a pre-synaptic spike arrives :math:`s \rightarrow s+1`.

NMDA
~~~~

.. math::

   I_{\text{NMDA}}=\bar{g}_{\text{NMDA}}(E_{\text{NMDA}}-V)s(t)\sigma(V)

.. math::

   \frac{ds}{dt}=\frac{-s}{\tau_{\text{NMDA}}^{\text{decay}}}

.. math::

   \sigma(V)=\frac{1}{1+\frac{{\left[{\rm{Mg}}^{2+}\right]}_{o}}{\beta }\cdot {{\exp }}\left(-\alpha \left(V-\gamma \right)\right)}


where
:math:`\bar{g}_{\text{NMDA}}` is the NMDA synaptic conductance, 
:math:`s` the channel state variable,
:math:`E_{\text{NMDA}}` the NMDA reversal potential,
:math:`\tau_{\text{NMDA}}^{\text{decay}}` the NMDA decay time constant,
:math:`\beta` (mM), :math:`\alpha` (mV\ :sup:`-1`) and :math:`\gamma` (mV) control the
magnesium and voltage dependencies and :math:`[\rm{Mg}^{2+}]_{o}`
denotes the external magnesium concentration (mM).
When a pre-synaptic spike arrives :math:`s \rightarrow s+1`.


References
~~~~~~~~~~

.. [1] https://neuronaldynamics.epfl.ch/online/Ch1.S3.html
.. [2] https://neuronaldynamics.epfl.ch/online/Ch6.S1.html
.. [3] https://neuronaldynamics.epfl.ch/online/Ch3.S1.html
.. [4] https://link.springer.com/chapter/10.1007/978-0-387-87708-2_7#Sec1