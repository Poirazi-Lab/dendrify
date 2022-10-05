#!/usr/bin/env python
# -*- coding: utf-8 -*-
# conda version : 4.8.3
# conda-build version : 3.18.12
# python version : 3.7.6.final.0
# brian2 version : 2.3 (py37hc9558a2_0)

from __future__ import annotations

import sys

import brian2
import numpy as np
from brian2.units import Quantity, ms, pA

from .ephysproperties import EphysProperties
from .equations import library


class Compartment:
    """
    A class that automatically generates and handles all differential
    equations and parameters needed to describe a single compartment and
    any currents (synaptic, dendritic, noise) passing through it.

    Parameters
    ----------

    name : str
        A unique name used to tag compartment-specific equations and parameters.
        It is also used to distinguish the various compartments belonging to the
        same :class:`~dendrify.neuronmodel.NeuronModel`.
    model : str, optional
        A keyword for accessing Dendrify's library models. Custom models can
        also be provided but they should be in the same formattable structure as
        the library models. Available options: ``'passive'`` (default),
        ``'adaptiveIF'``, ``'leakyIF'``, ``'adex'``.
    kwargs : brian2.units.fundamentalunits.Quantity, optional
        Kwargs are used to specify important electrophysiological properties,
        such as the specific capacitance or resistance. For more information
        see: :class:`~dendrify.ephysproperties.EphysProperties`.

    Examples
    --------
    >>> # specifying equations only:
    >>> compX = Compartment('nameX', 'leakyIF')
    >>> # specifying equations and ephys properties:
    >>> compY = Compartment('nameY', 'adaptiveIF', length=100*um, diameter=1*um,
    >>>                     cm=1*uF/(cm**2), gl=50*uS/(cm**2))
    """

    def __init__(self, name: str, model: str = 'passive', **kwargs: Quantity):
        self.name = name
        self._equations = None
        self._params = None
        self._connections = None
        # Add membrane equations:
        self._add_equations(model)
        # Keep track of electrophysiological properties:
        self._ephys_object = EphysProperties(name=self.name, **kwargs)

    def __str__(self):
        ephys_dict = self._ephys_object.__dict__
        ephys = '\n'.join([f"\u2192 {i}:\n  [{ephys_dict[i]}]\n"
                           for i in ephys_dict])
        equations = self.equations.replace('\n', '\n   ')

        parameters = '\n'.join([f"   '{i[0]}': {i[1]}"
                                for i in self.parameters.items()
                                ]) if self.parameters else '   None'
        msg = (f"OBJECT TYPE:\n\n  {self.__class__}\n\n"
               f"{'-'*45}\n\n"
               f"USER PARAMETERS:\n\n{ephys}"
               f"\n{'-'*45}\n\n"
               "PROPERTIES: \n\n"
               f"\u2192 equations:\n   {equations}\n\n"
               f"\u2192 parameters:\n{parameters}\n")
        return msg

    def _add_equations(self, model: str):
        """
        Adds equations to a compartment.

        Parameters
        ----------
        model : str
        """
        # Pick a model template or provide a custom model:
        if model in library:
            self._equations = library[model].format('_'+self.name)
        else:
            self._equations = model.format('_'+self.name)

    def connect(self, other: Compartment, g: Quantity | str = 'half_cylinders'):
        """
        Allows the connection (electrical coupling) of two compartments.

        Parameters
        ----------
        other : Compartment
            Another compartment.
        g : str | brian2.units.fundamentalunits.Quantity, optional
            The coupling conductance. It can be set explicitly or calculated
            automatically (provided all necessary parameters exist). 
            Available options: ``'half_cylinders'`` (default), 
            ``'cylinder_<compartment name>'``.

        Note
        ----
        The automatic approaches require that both compartments to be connected 
        have specified **length**, **diameter** and **axial resistance**.

        Examples
        --------
        >>> compX, compY = Compartment('x', **kwargs), Compartment('y', **kwargs)
        >>> # explicit approach:
        >>> compX.connect(compY, g=10*nS)
        >>> # half cylinders (default):
        >>> compX.connect(compY)
        >>> # cylinder of one compartment:
        >>> compX.connect(compY, g='cylinder_x')
        """

        # Prohibit connecting compartments with the same name
        if self.name == other.name:
            print(("ERROR: Cannot connect to compartments with the same name.\n"
                   "Program exited"))
            sys.exit()

        # Current from Comp2 -> Comp1
        I_forward = 'I_{1}_{0} = (V_{1}-V_{0}) * g_{1}_{0}  :amp'.format(
            self.name, other.name)
        # Current from Comp1 -> Comp2
        I_backward = 'I_{0}_{1} = (V_{0}-V_{1}) * g_{0}_{1}  :amp'.format(
                     self.name, other.name)

        # Add them to their respective compartments:
        self._equations += '\n'+I_forward
        other._equations += '\n'+I_backward

        # Include them to the I variable (I_ext -> Inj + new_current):
        self_change = f'= I_ext_{self.name}'
        other_change = f'= I_ext_{other.name}'
        self._equations = self._equations.replace(
            self_change, self_change + ' + ' + I_forward.split('=')[0])
        other._equations = other._equations.replace(
            other_change, other_change + ' + ' + I_backward.split('=')[0])

        # add them to connected comps
        if not self._connections:
            self._connections = []
        if not other._connections:
            other._connections = []

        g_to_self = f'g_{other.name}_{self.name}'
        g_to_other = f'g_{self.name}_{other.name}'

        # when g is specified by user
        if isinstance(g, brian2.units.fundamentalunits.Quantity):
            self._connections.append((g_to_self, 'user', g))
            other._connections.append((g_to_other, 'user', g))

        # when g is a string
        elif isinstance(g, str):
            if g == 'half_cylinders':
                self._connections.append((g_to_self, g, other._ephys_object))
                other._connections.append((g_to_other, g, self._ephys_object))

            elif g.split('_')[0] == "cylinder":
                ctype, name = g.split('_')
                comp = self if self.name == name else other
                self._connections.append(
                    (g_to_self, ctype, comp._ephys_object))
                other._connections.append(
                    (g_to_other, ctype, comp._ephys_object))
        else:
            print('Please select a valid conductance.')

    def synapse(self, channel: str | None = None, pre: str | None = None,
                g: Quantity | None = None, t_rise: Quantity | None = None,
                t_decay: Quantity | None = None, scale_g: bool | None = False):
        """
        Adds synaptic currents equations and parameters. When only the decay
        time constant ``t_decay`` is provided, the synaptic model assumes an
        instantaneous rise of the synaptic conductance followed by an exponential
        decay. When both the  rise ``t_rise`` and decay ``t_decay`` constants are
        provided, synapses are modelled as a sum of two exponentials. For more
        information see: 
        `Modeling Synapses by Arnd Roth & Mark C. W. van Rossum 
        <https://doi.org/10.7551/mitpress/9780262013277.003.0007>`_

        Parameters
        ----------
        channel : str, optional
            Synaptic channel type. Available options: ``'AMPA'``, ``'NMDA'``,
            ``'GABA'``, by default ``None``
        pre : str, optional
            A unique name to distinguish synapses of the same type coming from
            different input sources, by default ``None``
        g : brian2.units.fundamentalunits.Quantity, optional
            Maximum synaptic conductance, by default ``None``
        t_rise : brian2.units.fundamentalunits.Quantity, optional
            Rise time constant, by default ``None``
        t_decay : brian2.units.fundamentalunits.Quantity, optional
            Decay time constant, by default ``None``
        scale_g : bool, optional
            Option to add a normalization factor to scale the maximum
            conductance at 1 when synapses are modelled as a difference of
            exponentials (have both rise and decay kinetics), by default
            ``False``.

        Examples
        --------
        >>> comp = Compartment('comp')
        >>> # adding an AMPA synapse with instant rise & exponential decay:
        >>> comp.synapse('AMPA', g=1*nS, t_decay=5*ms, pre='X')
        >>> # same channel, different conductance & source:
        >>> comp.synapse('AMPA', g=2*nS, t_decay=5*ms, pre='Y')
        >>> # different channel with both rise & decay kinetics: 
        >>> comp.synapse('NMDA', g=1*nS, t_rise=5*ms, t_decay=50*ms, pre='X')
        """

        # Make sure that the user provides a synapse source
        if not pre:
            print((f"Warning: <pre> argument missing for '{channel}' "
                   f"synapse @ '{self.name}'\n"
                   "Program exited.\n"))
            sys.exit()
        # Switch to rise/decay equations if t_rise & t_decated are provided
        if all([t_rise, t_decay]):
            key = f"{channel}_rd"
        else:
            key = channel

        current_name = f'I_{channel}_{pre}_{self.name}'
        current_eqs = library[key].format(self.name, pre)

        to_replace = f'= I_ext_{self.name}'
        self._equations = self._equations.replace(
            to_replace, f'{to_replace} + {current_name}')
        self._equations += '\n'+current_eqs

        if not self._params:
            self._params = {}

        weight = f"w_{channel}_{pre}_{self.name}"
        self._params[weight] = 1
        # If user provides a value for g, then add it to _params
        if g:
            self._params[f'g_{channel}_{pre}_{self.name}'] = g
        if t_rise:
            self._params[f't_{channel}_rise_{pre}_{self.name}'] = t_rise
        if t_decay:
            self._params[f't_{channel}_decay_{pre}_{self.name}'] = t_decay
        if scale_g:
            if all([t_rise, t_decay, g]):
                norm_factor = Compartment.g_norm_factor(t_rise, t_decay)
                self._params[f'g_{channel}_{pre}_{self.name}'] *= norm_factor

    def noise(self, tau: Quantity = 20*ms, sigma: Quantity = 3*pA, mean: Quantity = 0*pA):
        """
        Adds a stochastic noise current. For more information see the Noise
        section: of :doc:`brian2:user/models`

        Parameters
        ----------
        tau : brian2.units.fundamentalunits.Quantity, optional
            Time constant of the Gaussian noise, by default 20*ms
        sigma : brian2.units.fundamentalunits.Quantity, optional
            Standard deviation of the Gaussian noise, by default 3*pA
        mean : brian2.units.fundamentalunits.Quantity, optional
            Mean of the Gaussian noise, by default 0*pA
        """
        I_noise_name = f'I_noise_{self.name}'
        noise_eqs = library['noise'].format(self.name)
        to_change = f'= I_ext_{self.name}'
        self._equations = self._equations.replace(
            to_change, f'{to_change} + {I_noise_name}')
        self._equations += '\n'+noise_eqs

        # Add _params:
        if not self._params:
            self._params = {}
        self._params[f'tau_noise_{self.name}'] = tau
        self._params[f'sigma_noise_{self.name}'] = sigma
        self._params[f'mean_noise_{self.name}'] = mean

    @property
    def parameters(self) -> dict:
        """
        All parameters that have been generated for a single compartment.

        Returns
        -------
        dict
        """
        d_out = {}
        for i in [self._params, self._g_couples]:
            if i:
                d_out.update(i)
        if self._ephys_object:
            d_out.update(self._ephys_object.parameters)
        return d_out

    @property
    def area(self) -> Quantity:
        """
        A compartment's surface area (open cylinder) based on its length
        and its diameter.

        Returns
        -------
        brian2.units.fundamentalunits.Quantity
        """
        try:
            return self._ephys_object.area
        except AttributeError:
            print(("Error: Missing Parameters\n"
                   f"Cannot calculate the area of <{self.name}>, "
                   "returned None instead.\n"))

    @property
    def capacitance(self) -> Quantity:
        """
        A compartment's absolute capacitance based on its specific capacitance
        (cm) and its surface area.

        Returns
        -------
        brian2.units.fundamentalunits.Quantity
        """
        try:
            return self._ephys_object.capacitance
        except AttributeError:
            print(("Error: Missing Parameters\n"
                   f"Cannot calculate the capacitance of <{self.name}>, "
                   "returned None instead.\n"))

    @property
    def g_leakage(self) -> Quantity:
        """
        A compartment's leakage conductance based on its specific leakage
        conductance (gl) and its surface area.

        Returns
        -------
        brian2.units.fundamentalunits.Quantity
        """
        try:
            return self._ephys_object.g_leakage
        except AttributeError:
            print(("Error: Missing Parameters\n"
                   f"Cannot calculate the g leakage of <{self.name}>, "
                   "returned None instead.\n"))

    @property
    def equations(self) -> str:
        """
        All differential equations that have been generated for a single
        compartment.

        Returns
        -------
        str
        """
        return self._equations

    @property
    def _g_couples(self) -> dict:
        # If not _connections have been specified yet
        if not self._connections:
            return None

        d_out = {}
        for i in self._connections:
            # If ephys objects are not created yet
            if not i[2]:
                return None

            name, ctype, helper_ephys = i[0], i[1], i[2]

            if ctype == 'half_cylinders':
                value = EphysProperties.g_couple(
                    self._ephys_object, helper_ephys)

            elif ctype == 'cylinder':
                value = helper_ephys.g_cylinder

            elif ctype == 'user':
                value = helper_ephys

            d_out[name] = value
        return d_out

    @staticmethod
    def g_norm_factor(trise: Quantity, tdecay: Quantity):
        tpeak = (tdecay*trise / (tdecay-trise)) * np.log(tdecay/trise)
        factor = (((tdecay*trise) / (tdecay-trise))
                  * (-np.exp(-tpeak/trise) + np.exp(-tpeak/tdecay))
                  / ms)
        return 1/factor


class Soma(Compartment):
    """
    A class that automatically generates and handles all differential equations
    and parameters needed to describe a somatic compartment and any currents
    (synaptic, dendritic, noise) passing through it.

    Note
    ----
    Soma acts as a wrapper for Compartment with slight changes to account for
    certain somatic properties. For a full list of its methods and attributes,
    please see: :class:`~dendrify.compartment.Compartment`.

    Parameters
    ----------
    name : str
        A unique name used to tag compartment-specific equations and parameters.
        It is also used to distinguish the various compartments belonging to the
        same :class:`~dendrify.neuronmodel.NeuronModel`.
    model : str, optional
        A keyword for accessing Dendrify's library models. Custom models can
        also be provided but they should be in the same formattable structure as
        the library models. Available options: ``'leakyIF'`` (default),
        ``'adaptiveIF'``, ``'adex'``.
    kwargs : brian2.units.fundamentalunits.Quantity, optional
        Kwargs are used to specify important electrophysiological properties,
        such as the specific capacitance or resistance. For more information
        see: :class:`~dendrify.ephysproperties.EphysProperties`.

    Examples
    --------
    >>> # specifying equations only:
    >>> somaX = Soma('nameX', 'leakyIF')
    >>> # specifying equations and ephys properties:
    >>> somaY = Soma('nameY', 'adaptiveIF', length=100*um, diameter=1*um,
    >>>              cm=1*uF/(cm**2), gl=50*uS/(cm**2))
    """

    def __init__(self, name: str, model: str = 'leakyIF', **kwargs: Quantity):

        super().__init__(name, model, **kwargs)
        self._events = None
        self._event_actions = None

    def __str__(self):
        ephys_dict = self._ephys_object.__dict__
        ephys = '\n'.join([f"\u2192 {i}:\n  [{ephys_dict[i]}]\n"
                           for i in ephys_dict])
        equations = self.equations.replace('\n', '\n   ')

        parameters = '\n'.join([f"   '{i[0]}': {i[1]}"
                                for i in self.parameters.items()
                                ]) if self.parameters else '   None'

        msg = (f"OBJECT TYPE:\n\n  {self.__class__}\n\n"
               f"{'-'*45}\n\n"
               f"USER PARAMETERS:\n\n{ephys}"
               f"\n{'-'*45}\n\n"
               "PROPERTIES: \n\n"
               f"\u2192 equations:\n   {equations}\n\n"
               f"\u2192 parameters:\n{parameters}\n")
        return msg


class Dendrite(Compartment):
    # TODO: restrict to passive
    """
    A class that automatically generates and handles all differential equations
    and parameters needed to describe a dendritic compartment, its active
    mechanisms, and any currents (synaptic, dendritic, ionic, noise) passing
    through it.

    Note
    ----
    Dendrite inherits all the methods and attributes of its parent class
    :class:`~dendrify.compartment.Compartment`. For a complete list, please refer
    to the documentation of the latter.

    Parameters
    ----------
    name : str
        A unique name used to tag compartment-specific equations and parameters.
        It is also used to distinguish the various compartments belonging to the
        same :class:`~dendrify.neuronmodel.NeuronModel`.
    model : str, optional
        A keyword for accessing Dendrify's library models. Dendritic compartments
        are by default set to ``'passive'``.
    """

    def __init__(self, name: str, model: str = 'passive', **kwargs: Quantity):
        super().__init__(name, model, **kwargs)
        self._events = None
        self._event_actions = None

    def __str__(self):
        ephys_dict = self._ephys_object.__dict__
        ephys = '\n'.join([f"\u2192 {i}:\n    [{ephys_dict[i]}]\n"
                           for i in ephys_dict])
        equations = self.equations.replace('\n', '\n    ')
        events = '\n'.join([f"    '{key}': '{self.events[key]}'"
                            for key in self.events
                            ]) if self.events else '    None'
        parameters = '\n'.join([f"    '{i[0]}': {i[1]}"
                                for i in self.parameters.items()
                                ]) if self.parameters else '    None'
        msg = (f"OBJECT TYPE:\n\n  {self.__class__}\n\n"
               f"{'-'*45}\n\n"
               f"USER PARAMETERS:\n\n{ephys}"
               f"\n{'-'*45}\n\n"
               "PROPERTIES: \n\n"
               f"\u2192 equations:\n    {equations}\n\n"
               f"\u2192 events:\n{events}\n\n"
               f"\u2192 parameters:\n{parameters}\n")
        return msg

    def dspikes(self, channel: str, threshold: Quantity | None = None,
                g_rise: Quantity | None = None, g_fall: Quantity | None = None):
        # TODO: show error if channel does not exist.
        """
        Adds the mechanisms and parameters needed for dendritic spiking. Under
        the hood, this method creates all equations, conditions and actions to
        utilize Brian's custom events functionality. Spikes are generated through
        the sequential activation of a positive (sodium or calcium-like) and a
        negative current (potassium-like current) when a specified dSpike
        threshold is crossed.

        Note
        ----
        The dendritic spiking mechanism as implemented here has three distinct
        phases.

        **INACTIVE PHASE:**\n
        When the dendritic voltage is subthreshold OR the simulation step is
        within the refractory period. dSpikes cannot be generated during this
        phase.

        **DEPOLARIZATION PHASE:**\n
        When the dendritic voltage crosses the dSpike threshold AND the
        refractory period has elapsed. This triggers the instant activation of a
        positive current that enters the dendrite and then decays exponentially.

        **REPOLARIZATION PHASE:**\n
        This phase starts automatically after a specified delay from the
        initiation of the dSpike. A negative current is activated instantly and
        then decays exponentially. Also a new refractory period begins.  

        Parameters
        ----------
        channel : str
            Ion channel type. Available options: ``'Na'``, ``'Ca'`` (coming soon)
        threshold : brian2.units.fundamentalunits.Quantity, optional
            The membrane voltage threshold for dendritic spiking.
        g_rise : brian2.units.fundamentalunits.Quantity, optional
            The conductance of the current that is activated during the
            depolarization phase.
        g_fall : brian2.units.fundamentalunits.Quantity, optional
             The conductance of the current that is activated during the
            repolarization phase.
        """
        if channel == 'Na':
            self._Na_spikes(threshold=threshold, g_rise=g_rise, g_fall=g_fall)
        elif channel == 'Ca':
            self._Ca_spikes(threshold=threshold, g_rise=g_rise, g_fall=g_fall)

    def _Na_spikes(self, threshold: Quantity = None, g_rise: Quantity = None,
                   g_fall: Quantity = None):
        """
        Adds Na spike currents (rise->I_Na, decay->I_Kn) and  other variables
        for controlling custom _events.
        Usage-> object._Na_spikes()
        """
        # The following code creates all necessary equations for dspikes:
        name = self.name
        dspike_currents = f'I_Na_{name} + I_Kn_{name}'
        # Both currents take into account the reversal potential of Na/K
        I_Na_eqs = f'I_Na_{name} = g_Na_{name} * (E_Na-V_{name})  :amp'
        I_Kn_eqs = f'I_Kn_{name} = g_Kn_{name} * (E_K-V_{name})  :amp'
        # Ion conductances simply decay exponentially
        g_Na_eqs = f'dg_Na_{name}/dt = -g_Na_{name}/tau_Na  :siemens'
        g_Kn_eqs = f'dg_Kn_{name}/dt = -g_Kn_{name}/tau_Kn  :siemens'
        # Parameters needed for the dSpike custom events
        I_Na_check = f'allow_I_Na_{name}  :boolean'
        I_Kn_check = f'allow_I_Kn_{name}  :boolean'
        refractory_var = f'timer_Na_{name}  :second'
        # Add equations to a compartment
        to_replace = f'= I_ext_{name}'
        self._equations = self._equations.replace(
            to_replace, f'{to_replace} + {dspike_currents}')
        self._equations += '\n'.join(['', I_Na_eqs, I_Kn_eqs, g_Na_eqs, g_Kn_eqs,
                                      I_Na_check, I_Kn_check, refractory_var])
        # Create all necessary custom _events for dspikes:
        condition_I_Na = library['condition_I_Na']
        condition_I_Kn = library['condition_I_Kn']
        if not self._events:
            self._events = {}
        self._events[f"activate_I_Na_{name}"] = condition_I_Na.format(name)
        self._events[f"activate_I_Kn_{name}"] = condition_I_Kn.format(name)

        # Specify what is going to happen inside run_on_event()
        if not self._event_actions:
            self._event_actions = library['run_on_Na_spike'].format(name)
        else:
            self._event_actions += "\n" + \
                library['run_on_Na_spike'].format(name)
        # Include params needed
        if not self._params:
            self._params = {}
        if threshold:
            self._params[f"Vth_Na_{self.name}"] = threshold
        if g_rise:
            self._params[f"g_Na_{self.name}_max"] = g_rise
        if g_fall:
            self._params[f"g_Kn_{self.name}_max"] = g_fall

    def _Ca_spikes(self, threshold: Quantity = None, g_rise: Quantity = None,
                   g_fall: Quantity = None):
        # TODO: check that it works as expected.
        """
        Coming soon.
        """
        pass

        # # The following code creates all necessary equations for dspikes:
        # name = self.name
        # dspike_currents = f'I_Ca_{name} + I_Kc_{name}'

        # I_Ca_eqs = f'dI_Ca_{name}/dt = -I_Ca_{name}/tau_Ca  :amp'
        # I_Kc_eqs = f'dI_Kc_{name}/dt = -I_Kc_{name}/tau_Kc  :amp'

        # I_Ca_check = f'allow_I_Ca_{name}  :boolean'
        # I_Kc_check = f'allow_I_Kc_{name}  :boolean'

        # refractory_var = f'timer_Ca_{name}  :second'
        # to_replace = f'= I_ext_{name}'

        # self._equations = self._equations.replace(
        #     to_replace, f'{to_replace} + {dspike_currents}')
        # self._equations += '\n'.join(['', I_Ca_eqs, I_Kc_eqs, I_Ca_check,
        #                               I_Kc_check, refractory_var])

        # # Create all necessary custom _events for dspikes:
        # condition_I_Ca = library['condition_I_Ca']
        # condition_I_Kc = library['condition_I_Kc']
        # if not self._events:
        #     self._events = {}
        # self._events[f"activate_I_Ca_{name}"] = condition_I_Ca.format(name)
        # self._events[f"activate_I_Kc_{name}"] = condition_I_Kc.format(name)

        # # Specify what is going to happen inside run_on_event()
        # if not self._event_actions:
        #     self._event_actions = library['run_on_Ca_spike'].format(name)
        # else:
        #     self._event_actions += "\n" + \
        #         library['run_on_Ca_spike'].format(name)
        # # Include params needed
        # if not self._params:
        #     self._params = {}
        # if threshold:
        #     self._params[f"Vth_Ca_{self.name}"] = threshold
        # if g_rise:
        #     self._params[f"g_Ca_{self.name}_max"] = g_rise
        # if g_fall:
        #     self._params[f"g_Kc_{self.name}_max"] = g_fall

    @property
    def events(self) -> dict:
        """
        A dictionary of all dSpike events created for a single dendrite.

        Returns
        -------
        dict
            Keys: event names, values: events conditions.
        """
        return self._events

    @property
    def event_actions(self) -> str:
        """
        A string that is used to tell Brian how to handle the dSpike events.

        Returns
        -------
        str
            Executable code that runs automatically in the background.
        """
        return self._event_actions
