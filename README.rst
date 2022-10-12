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

Although neuronal dendrites are known to greatly influence how single neurons
process synaptic information, their role in network-level functions remain 
largely unexplored. This is partly because existing tools do not allow the
development of realistic and efficient network models that account for dendrites.
Current SNNs are usually quite simplistic, overlooking essential dendritic
properties. Conversely, circuit models with morphologically detailed neuron
models are computationally costly, thus impractical for large-network
simulations.

To bridge the gap between these two extremes, we introduce Dendrify, a free,
open-source Python package compatible with the Brian 2 simulator. Dendrify,
through simple commands, automatically generates reduced compartmental neuron
models with simplified yet biologically relevant dendritic and synaptic
integrative properties. Such models strike a good balance between flexibility,
performance, and biological accuracy, allowing us to explore dendritic
contributions to network-level functions.

.. image:: docs_sphinx/source/_static/intro.png
   :width: 75 %
   :align: center

If you use Dendrify for your published research, we kindly ask you to cite our
article:|br|
**Dendrify: a new framework for seamless incorporation of dendrites in Spiking Neural Networks** |br|
M Pagkalos, S Chavlis, P Poirazi |br|
DOI: https://doi.org/10.1101/2022.05.03.490412 |br|
|br|

Documentation for Dendrify can be found at https://dendrify.readthedocs.io/en/latest/

.. |br| raw:: html

     <br>
