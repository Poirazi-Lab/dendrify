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


Although neuronal dendrites play a crucial role in shaping how individual 
neurons process synaptic information, their contribution to network-level 
functions has remained largely unexplored. Current spiking neural networks 
(SNNs) often oversimplify dendritic properties or overlook their essential 
functions. On the other hand, circuit models with morphologically detailed 
neuron representations are computationally intensive, making them impractical 
for simulating large networks.

In an effort to bridge this gap, we present Dendrify—a freely available,
open-source Python package that seamlessly integrates with the
`Brian 2 simulator <https://brian2.readthedocs.io/en/stable/>`_. Dendrify,
through simple commands, automatically generates reduced compartmental neuron
models with simplified yet biologically relevant dendritic and synaptic
integrative properties. These models offer a well-rounded compromise between
flexibility, performance, and biological accuracy, enabling us to investigate
the impact of dendrites on network-level functions.

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
