Release notes
=============

Version 2.2.0
-------------
    * **New Feature: dSpike Playground**
      |br|
      Introducing a new graphical tool for interactively visualizing, exploring,
      and calibrating dendritic spikes in Dendrify. Check out the new
      example: :doc:`examples/playground` and the
      relevant :class:`documentation <.Playground>` for more details.

    * **New Functionality: Model Customization**
      |br|
      Users can now fully customize the built-in models by adding new equations,
      replacing existing ones, and introducing new parameters. For more details,
      refer to the new tutorial: :doc:`tutorials/Dendrify_custom_models`.

    * **Installation**
      |br| 
      By default, Dendrify now installs the latest versions of Brian 2,
      Matplotlib, and NetworkX. Learn more in the
      updated :doc:`installation guide <installation>`.

    * **Documentation Improvements**
      |br|
      Key updates include:

      - Fixed a bug that prevented tutorials from rendering correctly.
      - Added new tutorials and examples.
      - Child classes now inherit documentation from parent classes.
      - Introduced a new section: :doc:`known_issues`.
      - Numerous aesthetic and language enhancements.


Version 2.1.5
-------------
    * Ensured compatibility with Brian 2.7.1.
    * Improved tutorials and documentation

Version 2.1.4
-------------
    * Fixed a bug that raised an error when config_dspikes was called multiple times
      to configure different dSpike types. Thank you Tim Bax for discovering and
      reporting this issue.
    * Checked compatibility with Brian 2.7.0.
    * Added package metadata (e.g. dendrify.__version__ works now).
    * Minor documentation improvements.

Version 2.1.3
-------------
    * Changed package requirements to fix installation conflicts with Brian 2.6.0.

Version 2.1.2
-------------
    * Fixed a bug that could cause the wrong estimation of a somatic
      compartment's surface area.
    * Other minor improvements.

Version 2.1.1
-------------
    * A minor release to fix some bugs introduced by VS code auto-formatting. 

Version 2.1.0
-------------
    * Changed the order of dSpikes thresholding to be more compatible with other
      Brian 2 objects and increase overall simulation stability.
    * Added the cadIF model as an option to PointNeuronModel.
    * Completely redesigned the Library section of the documentation and added
      more mathematical descriptions for the all built-in Dendrify models.
    * Added many new code examples.
    * Minor improvements in the source code for better readability and maintainability.

Version 2.0.1
-------------
    * Added Integrate-and-Fire with conductance based adaptation (cadIF) model.

Version 2.0.0
-------------
    * New and improved implementation of dendritic spikes.
    * New PointNeuronModel class for creating point-neuron models.
    * New way for specifying the electrophysiological properties of neurons.
    * Significantly improved error catching and exception handling.
    * Fixed compatibility issues with Jupyter notebooks.
    * More stable and robust code overall.
    * Added tutorials and code examples.
    * Improved documentation page.
    * Added a support e-mail address.
    * Many minor improvements, bug fixes and quality of life improvements.
    * New logo.

    Special thanks to Marcel Stimberg, Spyros Chavlis, Nikos Malakasis, Christos
    Karageorgiou Kaneen and Elisavet Kapetanou for their valuable feedback
    and suggestions for improving Dendrify.


Version 1.0.9
-------------
    * Minor improvements.


Version 1.0.8
-------------
    * Improved documentation.
    * Minor improvements.


Version 1.0.5
-------------
    * Improved documentation.
    * Minor bug fixes.


Version 1.0.4
-------------
    * Redesigned documentation page.
    * Added more type hints.
    * Improved compatibility with older Python versions.
    * Minor bug fixes.


.. |br| raw:: html

     <br>




