Model library
=============

Leaky membrane
--------------
.. math::

   C\dfrac{dV}{dt}=-g_L(V-E_L)+I

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`C`
     - membrane capacitance
   * - :math:`V`
     - membrane potential
   * - :math:`g_L`
     - leakage conductance
   * - :math:`E_L`
     - leakage reversal potential
   * - :math:`I`
     - input current

.. _somatic_models:

Somatic spiking models
----------------------
|

Leaky Integrate-and-Fire
~~~~~~~~~~~~~~~~~~~~~~~~
.. math::

   C\dfrac{dV}{dt}=-g_L(V-E_L)+I

Spike mechanism:

.. math::

   \text{if } V \geq V_\theta \text{ then } V \rightarrow V_r

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`V_\theta`
     - spike threshold
   * - :math:`V_r`
     - reset potential

**Examples:**

* :doc:`../examples/val_fi_curve`
* :doc:`../examples/point_lif_inhibition`

|

Adaptive Integrate-and-Fire
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. math::

   C\dfrac{dV}{dt}=-g_L(V-E_L)-w+I

.. math::

   \tau_w\dfrac{dw}{dt}=a(V-E_L)-w

Spike mechanism:

.. math::

   \text{if } V \geq V_\theta \text{ then } 
   \begin{cases}
   V \rightarrow V_r \\
   w \rightarrow w + b 
   \end{cases}

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`w`
     - adaptation current
   * - :math:`a`
     - maximal adaptation conductance
   * - :math:`b`
     - spike-triggered adaptation current
   * - :math:`τ_w`
     - adaptation time constant
   * - :math:`V_\theta`
     - spike threshold
   * - :math:`V_r`
     - reset potential

**Examples:**

* Example 1
* Example 2

|

Conductance-based Adaptive Integrate-and-Fire
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. math::

   C\dfrac{dV}{dt}=-g_L(V-E_L)-w+I

.. math::

   w=g_A(V-E_A)

.. math::

   \tau_A\dfrac{dg_A}{dt}=\bar{g_A}|V-E_A|\gamma - g_A

Spike mechanism:

.. math::

   \text{if } V \geq V_\theta \text{ then } 
   \begin{cases}
   V \rightarrow V_r \\
   g_A \rightarrow g_A + \delta g_A
   \end{cases}

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`w`
     - adaptation current
   * - :math:`\bar{g_A}`
     - maximal adaptation conductance
   * - :math:`E_A`
     - reversal potential of the adaptation
   * - :math:`τ_A`
     - adaptation time constant
   * - :math:`\delta g_A`
     - spike-triggered adaptation conductance
   * - :math:`\gamma`
     - steepness of the adaptation
   * - :math:`V_\theta`
     - spike threshold
   * - :math:`V_r`
     - reset potential

**Examples:**

* Example 1
* Example 2

|

Adaptive Exponential Integrate-and-Fire
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. math::

   C\dfrac{dV}{dt}=-g_L(V-E_L)+g_L\Delta_T\exp\left(\dfrac{V-V_T}{\Delta_T}\right)-w+I

.. math::

   \tau_w\dfrac{dw}{dt}=a(V-E_L)-w

Spike mechanism:

.. math::

   \text{if } V \geq V_\theta \text{ then } 
   \begin{cases}
   V \rightarrow V_r \\
   w \rightarrow w + b 
   \end{cases}

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`w`
     - adaptation current
   * - :math:`a`
     - maximal adaptation conductance
   * - :math:`b`
     - spike-triggered adaptation current
   * - :math:`V_T`
     - voltage threshold
   * - :math:`\Delta_T`
     - slope factor
   * - :math:`τ_w`
     - adaptation time constant
   * - :math:`V_\theta`
     - effective spike threshold
   * - :math:`V_r`
     - reset potential

**Examples:**

* :doc:`../examples/point_adex`
* :doc:`../examples/point_adex_synapses`

----

.. .. _dendritic_models:

.. Dendritic models
.. ----------------

.. _synaptic_models:

Synaptic models [3]_ [4]_
-------------------------
|

AMPA
~~~~
.. math::

   I_{\text{AMPA}}=\bar{g}_{\text{AMPA}}(E_{\text{AMPA}}-V)s(t)

.. math::

   \dfrac{ds}{dt}=\dfrac{-s}{\tau_{\text{AMPA}}^{\text{decay}}}

At presynaptic firing time:

.. math::
   
   s \rightarrow s+1

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\bar{g}_{\text{AMPA}}`
     - maximal AMPA conductance
   * - :math:`E_{\text{AMPA}}`
     - AMPA reversal potential
   * - :math:`\tau_{\text{AMPA}}^{\text{decay}}`
     - AMPA decay time constant
   * - :math:`s`
     - channel state variable
   * - :math:`V`
     - membrane potential


**Examples:**

* Example 1
* Example 2

|

AMPA (rise & decay)
~~~~~~~~~~~~~~~~~~~~
.. math::

   I_{\text{AMPA}}=\bar{g}_{\text{AMPA}}(E_{\text{AMPA}}-V)x(t)

.. math::

   \dfrac{dx}{dt}=\dfrac{-x}{\tau_{\text{AMPA}}^{\text{decay}}}+s(t)

.. math::

   \dfrac{ds}{dt}=\dfrac{-s}{\tau_{\text{AMPA}}^{\text{rise}}}

At presynaptic firing time:

.. math::
   
   s \rightarrow s+1

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\bar{g}_{\text{AMPA}}`
     - maximal AMPA conductance
   * - :math:`E_{\text{AMPA}}`
     - AMPA reversal potential
   * - :math:`\tau_{\text{AMPA}}^{\text{decay}}`
     - AMPA decay time constant
   * - :math:`s`
     - rise state variable
   * - :math:`x`
     - decay state variable
   * - :math:`V`
     - membrane potential

**Examples:**

* Example 1
* Example 2

|

NMDA
~~~~
.. math::

   I_{\text{NMDA}}=\bar{g}_{\text{NMDA}}(E_{\text{NMDA}}-V)s(t)\sigma(V)

.. math::

   \dfrac{ds}{dt}=\dfrac{-s}{\tau_{\text{NMDA}}^{\text{decay}}}

.. math::

   \sigma(V)=\dfrac{1}{1+\dfrac{{\left[{\rm{Mg}}^{2+}\right]}_{o}}{\beta }\cdot {{\exp }}\left(-\alpha \left(V-\gamma \right)\right)}
   
At presynaptic firing time:

.. math::

  s \rightarrow s+1

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\bar{g}_{\text{NMDA}}`
     - maximal NMDA conductance
   * - :math:`E_{\text{NMDA}}`
     - NMDA reversal potential
   * - :math:`\tau_{\text{NMDA}}^{\text{decay}}`
     - NMDA decay time constant
   * - :math:`s`
     - channel state variable
   * - :math:`\alpha`
     - the steepness of Magnesium unblock
   * - :math:`\beta`
     - the sensitivity of Magnesium unblock
   * - :math:`\gamma`
     - offset of the Magnesium unblock
   * - :math:`[\rm{Mg}^{2+}]_{o}`
     - external Magnesium concentration

**Examples:**

* Example 1
* Example 2

|

NMDA (rise & decay)
~~~~~~~~~~~~~~~~~~~~
.. math::

   I_{\text{NMDA}}=\bar{g}_{\text{NMDA}}(E_{\text{NMDA}}-V)x(t)\sigma(V)

.. math::

   \dfrac{dx}{dt}=\dfrac{-x}{\tau_{\text{NMDA}}^{\text{decay}}}+s(t)

.. math::

   \dfrac{ds}{dt}=\dfrac{-s}{\tau_{\text{NMDA}}^{\text{rise}}}

.. math::

   \sigma(V)=\dfrac{1}{1+\dfrac{{\left[{\rm{Mg}}^{2+}\right]}_{o}}{\beta }\cdot {{\exp }}\left(-\alpha \left(V-\gamma \right)\right)}

At presynaptic firing time:

.. math::
   
   s \rightarrow s+1

.. list-table::
   :align: left
   :header-rows: 1

   * - Symbol
     - Description
   * - :math:`\bar{g}_{\text{NMDA}}`
     - maximal NMDA conductance
   * - :math:`E_{\text{NMDA}}`
     - NMDA reversal potential
   * - :math:`\tau_{\text{NMDA}}^{\text{decay}}`
     - NMDA decay time constant
   * - :math:`s`
     - rise state variable
   * - :math:`x`
     - decay state variable
   * - :math:`\alpha`
     - the steepness of Magnesium unblock
   * - :math:`\beta`
     - the sensitivity of Magnesium unblock
   * - :math:`\gamma`
     - offset of the Magnesium unblock
   * - :math:`[\rm{Mg}^{2+}]_{o}`
     - external Magnesium concentration

**Examples:**

* Example 1
* Example 2
  
----

References
~~~~~~~~~~

.. [1] https://neuronaldynamics.epfl.ch/online/Ch1.S3.html
.. [2] https://neuronaldynamics.epfl.ch/online/Ch6.S1.html
.. [3] https://neuronaldynamics.epfl.ch/online/Ch3.S1.html
.. [4] https://link.springer.com/chapter/10.1007/978-0-387-87708-2_7#Sec1