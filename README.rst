Dendrify
========

*Introducing dendrites to spiking neural networks*

.. image:: https://img.shields.io/pypi/v/Dendrify.svg
        :target: https://pypi.python.org/pypi/Dendrify

.. image:: https://readthedocs.org/projects/dendrify/badge/?version=latest
  :target: https://dendrify.readthedocs.io/en/stable/?badge=stable
  :alt: Documentation Status

.. image:: https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg
        :target: CODE_OF_CONDUCT.md
        :alt: Contributor Covenant


Neuronal dendrites play a crucial role in shaping how individual neurons process
synaptic information, yet their contributions to network-level functions remain
largely underexplored. While current spiking neural networks (SNNs) often
oversimplify or neglect essential dendritic properties, circuit models with
morphologically detailed neuron representations are computationally expensive,
limiting their practicality for large-scale network simulations.

To address these challenges, we introduce Dendrify, a free and open-source Python
package designed to work seamlessly with the 
`Brian 2 simulator <https://brian2.readthedocs.io/en/stable/>`_. Dendrify enables
users to generate reduced compartmental neuron models with biologically relevant
dendritic and synaptic properties using simple commands. These models strike a
good balance between flexibility, performance, and accuracy, making it possible 
to study the impact of dendrites on network-level functions.

.. image:: https://github.com/Poirazi-Lab/dendrify/assets/30598350/b6db9876-6de4-458a-b27e-61d4edd360db
   :width: 70 %
   :align: center

If you use Dendrify for your published research, we kindly ask you to cite our article:

Pagkalos, M., Chavlis, S., & Poirazi, P. (2023). Introducing the Dendrify framework
for incorporating dendrites to spiking neural networks.
Nature Communications, 14(1), 131. https://doi.org/10.1038/s41467-022-35747-8


Documentation for Dendrify can be found at https://dendrify.readthedocs.io/en/latest/


The project presentation for the INCF/OCNS Software Working Group is available 
`on google drive <https://docs.google.com/presentation/d/1LUUh2ja3YSHcmByU0Vyn7vcDEnDq6fWfVxFfuK8FzE0/edit?usp=sharing>`_.
