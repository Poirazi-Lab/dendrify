"""
This module defines the classes for different types of compartments in a neuron
model.

The `Compartment` class is a base class that provides the basic functionality for
a single compartment. It handles all differential equations and parameters needed
to describe a single compartment and any currents passing through it.

The `Soma` and `Dendrite` classes inherit from the `Compartment` class and represent
specific types of compartments.

Classes:
    Compartment: Represents a single compartment in a neuron model.
    Soma: Represents the somatic compartment in a neuron model.
    Dendrite: Represents a dendritic compartment in a neuron model.
"""

from __future__ import annotations

import pprint as pp
from typing import Optional, Union

import numpy as np
from brian2 import defaultclock
from brian2.core.functions import timestep
from brian2.units import Quantity, ms, pA

from .ephysproperties import EphysProperties
from .equations import library
from .utils import (DimensionlessCompartmentError, DuplicateEquationsError,
                    get_logger)

logger = get_logger(__name__)


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
        same :class:`.NeuronModel`.
    model : str, optional
        A keyword for accessing Dendrify's library models. Custom models can
        also be provided but they should be in the same formattable structure as
        the library models. Available options: ``'passive'`` (default),
        ``'adaptiveIF'``, ``'leakyIF'``, ``'adex'``.
    length : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's length.
    diameter : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's diameter.
    cm : ~brian2.units.fundamentalunits.Quantity, optional
        Specific capacitance (usually μF / cm^2).
    gl : ~brian2.units.fundamentalunits.Quantity, optional
        Specific leakage conductance (usually μS / cm^2).
    cm_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute capacitance (usually pF).
    gl_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute leakage conductance (usually nS).
    r_axial : ~brian2.units.fundamentalunits.Quantity, optional
        Axial resistance (usually Ohm * cm).
    v_rest : ~brian2.units.fundamentalunits.Quantity, optional
        Resting membrane voltage.
    scale_factor : float, optional
        A global area scale factor, by default ``1.0``.
    spine_factor : float, optional
        A dendritic area scale factor to account for spines, by default ``1.0``.

    Examples
    --------
    >>> # specifying equations only:
    >>> compX = Compartment('nameX', 'leakyIF')
    >>> # specifying equations and ephys properties:
    >>> compY = Compartment('nameY', 'adaptiveIF', length=100*um, diameter=1*um,
    >>>                     cm=1*uF/(cm**2), gl=50*uS/(cm**2))
    >>> # specifying equations and absolute ephys properties:
    >>> compY = Compartment('nameZ', 'adaptiveIF', cm_abs=100*pF, gl_abs=20*nS)
    """

    def __init__(
        self,
        name: str,
        model: str = 'passive',
        length: Optional[Quantity] = None,
        diameter: Optional[Quantity] = None,
        cm: Optional[Quantity] = None,
        gl: Optional[Quantity] = None,
        cm_abs: Optional[Quantity] = None,
        gl_abs: Optional[Quantity] = None,
        r_axial: Optional[Quantity] = None,
        v_rest: Optional[Quantity] = None,
        scale_factor: Optional[float] = 1.0,
        spine_factor: Optional[float] = 1.0
    ):
        self.name = name
        self._equations = None
        self._params = None
        self._connections = None
        self._synapses = None
        # Add membrane equations:
        self._add_equations(model)
        # Keep track of electrophysiological properties:
        self._ephys_object = EphysProperties(
            name=self.name,
            length=length,
            diameter=diameter,
            cm=cm,
            gl=gl,
            cm_abs=cm_abs,
            gl_abs=gl_abs,
            r_axial=r_axial,
            v_rest=v_rest,
            scale_factor=scale_factor,
            spine_factor=spine_factor
        )

    def __str__(self):
        equations = self.equations
        parameters = pp.pformat(self.parameters)
        user = pp.pformat(self._ephys_object.__dict__)
        txt = (f"\nOBJECT\n{6*'-'}\n{self.__class__}\n\n\n"
               f"EQUATIONS\n{9*'-'}\n{equations}\n\n\n"
               f"PARAMETERS\n{10*'-'}\n{parameters}\n\n\n"
               f"USER PARAMETERS\n{15*'-'}\n{user}")
        return txt

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
            logger.warning(("The model you provided is not found. The default "
                            "'passive' membrane model will be used instead."))
            self._equations = library['passive'].format('_'+self.name)

    def connect(self,
                other: Compartment,
                g: Union[Quantity, str] = 'half_cylinders'):
        """
        Connects two compartments (electrical coupling).

        Parameters
        ----------
        other : Compartment
            Another compartment.
        g : str or :class:`~brian2.units.fundamentalunits.Quantity`, optional
            The coupling conductance. It can be set explicitly or calculated
            automatically (provided all necessary parameters exist).
            Available options: ``'half_cylinders'`` (default),
            ``'cylinder_<compartment name>'``.

        Warning
        -------
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
            raise ValueError(
                "Cannot connect compartments with the same name.\n")
        if (self.dimensionless or other.dimensionless) and isinstance(g, str):
            raise DimensionlessCompartmentError(
                ("Cannot automatically calculate the coupling \nconductance of "
                 "dimensionless compartments. To resolve this error, perform\n"
                 "one of the following:\n\n"
                 f"1. Provide [length, diameter, r_axial] for both '{
                     self.name}'"
                 f" and '{other.name}'.\n\n"
                 f"2. Turn both compartment into dimensionless by providing only"
                 " values for \n   [cm_abs, gl_abs] and then connect them using "
                 "an exact coupling conductance."
                 )
            )

        # Current from Comp2 -> Comp1
        forward_current = 'I_{1}_{0} = (V_{1}-V_{0}) * g_{1}_{0}  :amp'.format(
            self.name, other.name)
        # Current from Comp1 -> Comp2
        backward_current = 'I_{0}_{1} = (V_{0}-V_{1}) * g_{0}_{1}  :amp'.format(
            self.name, other.name)

        # Add them to their respective compartments:
        self._equations += '\n'+forward_current
        other._equations += '\n'+backward_current

        # Include them to the I variable (I_ext -> Inj + new_current):
        self_change = f'= I_ext_{self.name}'
        other_change = f'= I_ext_{other.name}'
        self._equations = self._equations.replace(
            self_change, self_change + ' + ' + forward_current.split('=')[0])
        other._equations = other._equations.replace(
            other_change, other_change + ' + ' + backward_current.split('=')[0])

        # add them to connected comps
        if not self._connections:
            self._connections = []
        if not other._connections:
            other._connections = []

        g_to_self = f'g_{other.name}_{self.name}'
        g_to_other = f'g_{self.name}_{other.name}'

        # when g is specified by user
        if isinstance(g, Quantity):
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
            raise ValueError(
                "Please provide a valid conductance option."
            )

    def synapse(self, channel: str,
                tag: str,
                g: Optional[Quantity] = None,
                t_rise: Optional[Quantity] = None,
                t_decay: Optional[Quantity] = None,
                scale_g: bool = False):
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
        channel : str
            Synaptic channel type. Available options: ``'AMPA'``, ``'NMDA'``,
            ``'GABA'``.
        tag : str
            A unique name to distinguish synapses of the same type.
        g : :class:`~brian2.units.fundamentalunits.Quantity`
            Maximum synaptic conductance
        t_rise : :class:`~brian2.units.fundamentalunits.Quantity`
            Rise time constant
        t_decay : :class:`~brian2.units.fundamentalunits.Quantity`
            Decay time constant
        scale_g : bool, optional
            Option to add a normalization factor to scale the maximum
            conductance at 1 when synapses are modelled as a difference of
            exponentials (have both rise and decay kinetics), by default
            ``False``.

        Examples
        --------
        >>> comp = Compartment('comp')
        >>> # adding an AMPA synapse with instant rise & exponential decay:
        >>> comp.synapse('AMPA', tag='X', g=1*nS, t_decay=5*ms)
        >>> # same channel, different conductance & source:
        >>> comp.synapse('AMPA', tag='Y', g=2*nS, t_decay=5*ms)
        >>> # different channel with both rise & decay kinetics:
        >>> comp.synapse('NMDA', tag='X' g=1*nS, t_rise=5*ms, t_decay=50*ms)
        """

        synapse_id = "_".join([channel, tag, self.name])

        if self._synapses:
            # Check if this synapse already exists
            if synapse_id in self._synapses:
                raise DuplicateEquationsError(
                    f"The equations of '{channel}_{tag}' have already been "
                    f"added to '{self.name}'. \nPlease use a different "
                    f"combination of [channel, tag] when calling the synapse() "
                    "method \nmultiple times on a single compartment. You might"
                    " also see this error if you are using \nJupyter/iPython "
                    "which store variable values in memory. Try cleaning all "
                    "variables or \nrestart the kernel before running your "
                    "code. If this problem persists, please report it \n"
                    "by creating a new issue here: "
                    "https://github.com/Poirazi-Lab/dendrify/issues."
                )
        else:
            self._synapses = []

        # Switch to rise/decay equations if t_rise & t_decay are provided
        key = f"{channel}_rd" if all([t_rise, t_decay]) else channel
        current_name = f'I_{channel}_{tag}_{self.name}'
        current_eqs = library[key].format(self.name, tag)

        to_replace = f'= I_ext_{self.name}'
        self._equations = self._equations.replace(
            to_replace,
            f'{to_replace} + {current_name}'
        )
        self._equations += '\n'+current_eqs

        if not self._params:
            self._params = {}

        weight = f"w_{channel}_{tag}_{self.name}"
        self._params[weight] = 1.0

        # If user provides a value for g, then add it to _params
        if g:
            self._params[f'g_{channel}_{tag}_{self.name}'] = g
        if t_rise:
            self._params[f't_{channel}_rise_{tag}_{self.name}'] = t_rise
        if t_decay:
            self._params[f't_{channel}_decay_{tag}_{self.name}'] = t_decay
        if scale_g:
            if all([t_rise, t_decay, g]):
                norm_factor = Compartment.g_norm_factor(t_rise, t_decay)
                self._params[f'g_{channel}_{tag}_{self.name}'] *= norm_factor

        self._synapses.append(synapse_id)

    def noise(self, tau: Quantity = 20*ms, sigma: Quantity = 1*pA,
              mean: Quantity = 0*pA):
        """
        Adds a stochastic noise current. For more information see the Noise
        section: of :doc:`brian2:user/models`

        Parameters
        ----------
        tau : :class:`~brian2.units.fundamentalunits.Quantity`, optional
            Time constant of the Gaussian noise, by default ``20*ms``
        sigma : :class:`~brian2.units.fundamentalunits.Quantity`, optional
            Standard deviation of the Gaussian noise, by default ``3*pA``
        mean : :class:`~brian2.units.fundamentalunits.Quantity`, optional
            Mean of the Gaussian noise, by default ``0*pA``
        """
        noise_current = f'I_noise_{self.name}'

        if noise_current in self.equations:
            raise DuplicateEquationsError(
                f"The equations of '{noise_current}' have already been "
                f"added to '{self.name}'. \nYou might be seeing this error if "
                "you are using Jupyter/iPython "
                "which store variable values \nin memory. Try cleaning all "
                "variables or restart the kernel before running your "
                "code. If this \nproblem persists, please report it "
                "by creating a new issue here:\n"
                "https://github.com/Poirazi-Lab/dendrify/issues."
            )
        noise_eqs = library['noise'].format(self.name)
        to_change = f'= I_ext_{self.name}'
        self._equations = self._equations.replace(
            to_change,
            f'{to_change} + {noise_current}'
        )
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
        Returns all the parameters that have been generated for a single
        compartment.

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
        Returns a compartment's surface area (open cylinder) based on its length
        and diameter.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        return self._ephys_object.area

    @property
    def capacitance(self) -> Quantity:
        """
        Returns a compartment's absolute capacitance.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        return self._ephys_object.capacitance

    @property
    def g_leakage(self) -> Quantity:
        """
        A compartment's absolute leakage conductance.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        return self._ephys_object.g_leakage

    @property
    def equations(self) -> str:
        """
        Returns all differential equations that describe a single compartment
        and the mechanisms that have been added to it.

        Returns
        -------
        str
        """
        return self._equations

    @property
    def _g_couples(self) -> Union[dict, None]:
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
    def g_norm_factor(t_rise: Quantity, t_decay: Quantity):
        """
        Calculates the normalization factor for synaptic conductance with 
        t_rise and t_decay kinetics.

        Parameters:
        t_rise (Quantity): The rise time of the function.
        t_decay (Quantity): The decay time of the function.

        Returns:
        float: The normalization factor for the g function.
        """
        t_peak = (t_decay*t_rise / (t_decay-t_rise)) * np.log(t_decay/t_rise)
        factor = (((t_decay*t_rise) / (t_decay-t_rise))
                  * (-np.exp(-t_peak/t_rise) + np.exp(-t_peak/t_decay))
                  / ms)
        return 1/factor

    @property
    def dimensionless(self) -> bool:
        """
        Checks if a compartment has been flagged as dimensionless.

        Returns
        -------
        bool
        """
        return bool(self._ephys_object._dimensionless)


class Soma(Compartment):
    """
    A class representing a somatic compartment in a neuron model.

    This class automatically generates and handles all differential equations
    and parameters needed to describe a somatic compartment and any currents
    (synaptic, dendritic, noise) passing through it.

    .. seealso::

       Soma acts as a wrapper for Compartment with slight changes to account for
       certain somatic properties. For a full list of its methods and attributes,
       please see: :class:`.Compartment`.

    Parameters
    ----------
    name : str
        A unique name used to tag compartment-specific equations and parameters.
        It is also used to distinguish the various compartments belonging to the
        same :class:`.NeuronModel`.
    model : str, optional
        A keyword for accessing Dendrify's library models. Custom models can
        also be provided but they should be in the same formattable structure as
        the library models. Available options: ``'leakyIF'`` (default),
        ``'adaptiveIF'``, ``'adex'``.
    length : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's length.
    diameter : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's diameter.
    cm : ~brian2.units.fundamentalunits.Quantity, optional
        Specific capacitance (usually μF / cm^2).
    gl : ~brian2.units.fundamentalunits.Quantity, optional
        Specific leakage conductance (usually μS / cm^2).
    cm_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute capacitance (usually pF).
    gl_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute leakage conductance (usually nS).
    r_axial : ~brian2.units.fundamentalunits.Quantity, optional
        Axial resistance (usually Ohm * cm).
    v_rest : ~brian2.units.fundamentalunits.Quantity, optional
        Resting membrane voltage.
    scale_factor : float, optional
        A global area scale factor, by default ``1.0``.
    spine_factor : float, optional
        A dendritic area scale factor to account for spines, by default ``1.0``.

    Examples
    --------
    >>> # specifying equations only:
    >>> compX = Soma('nameX', 'leakyIF')
    >>> # specifying equations and ephys properties:
    >>> compY = Soma('nameY', 'adaptiveIF', length=100*um, diameter=1*um,
    >>>                     cm=1*uF/(cm**2), gl=50*uS/(cm**2))
    >>> # specifying equations and absolute ephys properties:
    >>> compY = Soma('nameZ', 'adaptiveIF', cm_abs=100*pF, gl_abs=20*nS)
    """

    def __init__(
        self,
        name: str,
        model: str = 'leakyIF',
        length: Optional[Quantity] = None,
        diameter: Optional[Quantity] = None,
        cm: Optional[Quantity] = None,
        gl: Optional[Quantity] = None,
        cm_abs: Optional[Quantity] = None,
        gl_abs: Optional[Quantity] = None,
        r_axial: Optional[Quantity] = None,
        v_rest: Optional[Quantity] = None,
        scale_factor: Optional[float] = 1.0,
        spine_factor: Optional[float] = 1.0
    ):
        super().__init__(
            name=name,
            model=model,
            length=length,
            diameter=diameter,
            cm=cm,
            gl=gl,
            cm_abs=cm_abs,
            gl_abs=gl_abs,
            r_axial=r_axial,
            v_rest=v_rest,
            scale_factor=scale_factor,
            spine_factor=spine_factor
        )


class Dendrite(Compartment):
    """
    A class that automatically generates and handles all differential equations
    and parameters needed to describe a dendritic compartment, its active
    mechanisms, and any currents (synaptic, dendritic, ionic, noise) passing
    through it.

    .. seealso::
       Dendrite inherits all the methods and attributes of its parent class
       :class:`.Compartment`. For a complete list, please
       refer to the documentation of the latter.

    Parameters
    ----------
    name : str
        A unique name used to tag compartment-specific equations and parameters.
        It is also used to distinguish the various compartments belonging to the
        same :class:`.NeuronModel`.
    model : str, optional
        A keyword for accessing Dendrify's library models. Dendritic compartments
        are by default set to ``'passive'``.
    length : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's length.
    diameter : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's diameter.
    cm : ~brian2.units.fundamentalunits.Quantity, optional
        Specific capacitance (usually μF / cm^2).
    gl : ~brian2.units.fundamentalunits.Quantity, optional
        Specific leakage conductance (usually μS / cm^2).
    cm_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute capacitance (usually pF).
    gl_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute leakage conductance (usually nS).
    r_axial : ~brian2.units.fundamentalunits.Quantity, optional
        Axial resistance (usually Ohm * cm).
    v_rest : ~brian2.units.fundamentalunits.Quantity, optional
        Resting membrane voltage.
    scale_factor : float, optional
        A global area scale factor, by default ``1.0``.
    spine_factor : float, optional
        A dendritic area scale factor to account for spines, by default ``1.0``.

    Examples
    --------
    >>> # specifying equations only:
    >>> compX = Dendrite('nameX')
    >>> # specifying equations and ephys properties:
    >>> compY = Dendrite('nameY', length=100*um, diameter=1*um,
    >>>                     cm=1*uF/(cm**2), gl=50*uS/(cm**2))
    >>> # specifying equations and absolute ephys properties:
    >>> compY = Dendrite('nameZ', cm_abs=100*pF, gl_abs=20*nS)
    """

    def __init__(
        self,
        name: str,
        model: str = 'passive',
        length: Optional[Quantity] = None,
        diameter: Optional[Quantity] = None,
        cm: Optional[Quantity] = None,
        gl: Optional[Quantity] = None,
        cm_abs: Optional[Quantity] = None,
        gl_abs: Optional[Quantity] = None,
        r_axial: Optional[Quantity] = None,
        v_rest: Optional[Quantity] = None,
        scale_factor: Optional[float] = 1.0,
        spine_factor: Optional[float] = 1.0
    ):
        super().__init__(
            name=name,
            model=model,
            length=length,
            diameter=diameter,
            cm=cm,
            gl=gl,
            cm_abs=cm_abs,
            gl_abs=gl_abs,
            r_axial=r_axial,
            v_rest=v_rest,
            scale_factor=scale_factor,
            spine_factor=spine_factor
        )
        self._events = None
        self._event_actions = None
        self._dspike_params = None

    def __str__(self):
        equations = self.equations
        parameters = pp.pformat(self.parameters)
        events = pp.pformat(self.events, width=120)
        event_names = pp.pformat(self.event_names)
        user = self._ephys_object.__dict__
        user_clean = pp.pformat({k: v for k, v in user.items() if v})
        txt = (f"\nOBJECT\n{6*'-'}\n{self.__class__}\n\n\n"
               f"EQUATIONS\n{9*'-'}\n{equations}\n\n\n"
               f"PARAMETERS\n{10*'-'}\n{parameters}\n\n\n"
               f"EVENTS\n{6*'-'}\n{event_names}\n\n\n"
               f"EVENT CONDITIONS\n{16*'-'}\n{events}\n\n\n"
               f"USER PARAMETERS\n{15*'-'}\n{user_clean}")
        return txt

    def dspikes(self, name: str,
                threshold: Optional[Quantity] = None,
                g_rise: Optional[Quantity] = None,
                g_fall: Optional[Quantity] = None,
                duration_rise: Optional[Quantity] = None,
                duration_fall: Optional[Quantity] = None,
                reversal_rise: Union[Quantity, str, None] = None,
                reversal_fall: Union[Quantity, str, None] = None,
                offset_fall: Optional[Quantity] = None,
                refractory: Optional[Quantity] = None
                ):
        """
        Adds the ionic mechanisms and parameters needed for dendritic spiking.
        Under the hood, this method creates the equations, conditions and
        actions to take advantage of Brian's custom events. dSpikes are
        generated through the sequential activation of a positive (sodium or
        calcium-like) and a negative current (potassium-like current) when a
        specified dSpike threshold is crossed.

        .. hint::

           The dendritic spiking mechanism as implemented here has three
           distinct phases.

           **INACTIVE PHASE:**\n
           When the dendritic voltage is subthreshold OR the simulation step is
           within the refractory period. dSpikes cannot be generated during this
           phase.

           **RISE PHASE:**\n
           When the dendritic voltage crosses the dSpike threshold AND the
           refractory period has elapsed. This triggers the instant activation
           of a positive current that is deactivated after a specified amount
           of time (``duration_rise``). Also a new refractory period begins.

           **FALL PHASE:**\n
           This phase starts automatically with a delay (``offset_fall``) after
           the dSpike threshold is crossed. A negative current is activated
           instantly and then is deactivated after a specified amount of time
           (``duration_fall``). 

        Parameters
        ----------
        name : str
            A unique name to describe a single dSpike type.
        threshold : ~brian2.units.fundamentalunits.Quantity, optional
            The membrane voltage threshold for dendritic spiking.
        g_rise : ~brian2.units.fundamentalunits.Quantity, optional
            The max conductance of the channel that is activated during the rise
            (depolarization phase).
        g_fall : ~brian2.units.fundamentalunits.Quantity, optional
            The max conductance of the channel that is activated during the fall
            (repolarization phase).
        duration_rise : ~brian2.units.fundamentalunits.Quantity, optional
            The duration of g_rise staying open.
        duration_fall : ~brian2.units.fundamentalunits.Quantity, optional
            The duration of g_fall staying open.
        reversal_rise : (~brian2.units.fundamentalunits.Quantity, str), optional
            The reversal potential of the channel that is activated during the rise
            (depolarization) phase.
        reversal_fall : (~brian2.units.fundamentalunits.Quantity, str), optional
            The reversal potential of the channel that is activated during the fall
            (repolarization) phase.
        offset_fall : ~brian2.units.fundamentalunits.Quantity, optional
            The delay for the activation of g_rise.
        refractory : ~brian2.units.fundamentalunits.Quantity, optional
            The time interval required before dSpike can be activated again.
        """

        # The following code creates all necessary equations for dspikes:
        comp = self.name
        event_id = f"{name}_{comp}"
        event_name = f"spike_{event_id}"

        if self._events:
            # Check if this event already exists
            if event_name in self._events:
                raise DuplicateEquationsError(
                    f"The equations for '{event_name}' have already been "
                    f"added to '{self.name}'. \nPlease use a different "
                    f"[name] when adding multiple dSpike mechanisms to "
                    " a single compartment. \nYou might"
                    " also see this error if you are using Jupyter/iPython "
                    "which store variable values in \nmemory. Try cleaning all "
                    "variables or restart the kernel before running your "
                    "code. If this \nproblem persists, please report it "
                    "by creating a new issue here: \n"
                    "https://github.com/Poirazi-Lab/dendrify/issues."
                )
        else:
            self._events = {}

        dspike_currents = f"I_rise_{event_id} + I_fall_{event_id}"

        # Both currents take into account the reversal potential of Na/K
        current_rise_eqs = f"I_rise_{event_id} = g_rise_{
            event_id} * (E_rise_{name}-V_{comp})  :amp"
        current_fall_eqs = f"I_fall_{event_id} = g_fall_{
            event_id} * (E_fall_{name}-V_{comp})  :amp"

        # Ion conductances
        g_rise_eqs = (
            f"g_rise_{event_id} = "
            f"g_rise_max_{event_id} * "
            f"int(t_in_timesteps <= spiketime_{
                event_id} + duration_rise_{event_id}) * "
            f"gate_{event_id} "
            ":siemens"
        )
        g_fall_eqs = (
            f"g_fall_{event_id} = "
            f"g_fall_max_{event_id} * "
            f"int(t_in_timesteps <= spiketime_{
                event_id} + offset_fall_{event_id} + duration_fall_{event_id}) * "
            f"int(t_in_timesteps >= spiketime_{
                event_id} + offset_fall_{event_id}) *  "
            f"gate_{event_id} "
            ":siemens"
        )
        spiketime = f'spiketime_{event_id}  :1'  # in units of timestep
        gate = f'gate_{event_id}  :1'  # zero or one

        # Add equations to a compartment
        to_replace = f'= I_ext_{comp}'
        self._equations = self._equations.replace(
            to_replace,
            f'{to_replace} + {dspike_currents}'
        )
        self._equations += '\n'.join(['', current_rise_eqs, current_fall_eqs,
                                      g_rise_eqs, g_fall_eqs,
                                      spiketime, gate]
                                     )

        # Create and add custom dspike event
        event_name = f"spike_{event_id}"
        condition = (f"V_{comp} >= Vth_{event_id} and "
                     f"t_in_timesteps >= spiketime_{
                         event_id} + refractory_{event_id} * gate_{event_id}"
                     )

        self._events[event_name] = condition

        # Specify what is going to happen inside run_on_event()
        action = {f"spike_{event_id}": f"spiketime_{
            event_id} = t_in_timesteps; gate_{event_id} = 1"}
        if not self._event_actions:
            self._event_actions = action
        else:
            self._event_actions.update(action)

        # Include params needed
        if not self._dspike_params:
            self._dspike_params = {}

        dt = defaultclock.dt

        params = [
            threshold,
            g_rise,
            g_fall,
            self._ionic_param(reversal_rise),
            self._ionic_param(reversal_fall),
            self._timestep(duration_rise, dt),
            self._timestep(duration_fall, dt),
            self._timestep(offset_fall, dt),
            self._timestep(refractory, dt)]

        variables = [
            f"Vth_{event_id}",
            f"g_rise_max_{event_id}",
            f"g_fall_max_{event_id}",
            f"E_rise_{name}",
            f"E_fall_{name}",
            f"duration_rise_{event_id}",
            f"duration_fall_{event_id}",
            f"offset_fall_{event_id}",
            f"refractory_{event_id}"]

        d = dict(zip(variables, params))
        self._dspike_params[event_id] = d

    def _timestep(self,
                  param: Union[Quantity, None], dt
                  ) -> Union[int, None]:
        if not param:
            return None
        if isinstance(param, Quantity):
            return timestep(param, dt)
        raise ValueError(
            f"Please provide a valid time parameter for '{self.name}'."
        )

    def _ionic_param(self,
                     param: Union[str, Quantity, None],
                     ) -> Union[Quantity, None]:
        default_params = EphysProperties.DEFAULT_PARAMS
        valid_params = {k: v for k, v in default_params.items() if k[0] == 'E'}
        if not param:
            return None
        if isinstance(param, Quantity):
            return param
        if isinstance(param, str):
            try:
                return default_params[param]
            except KeyError:
                raise ValueError(
                    f"Please provide a valid ionic parameter for '{
                        self.name}'."
                    " Available options:\n"
                    f"{pp.pformat(valid_params)}"
                )
        else:
            raise ValueError(
                f"Please provide a valid ionic parameter for '{self.name}'."
                " Available options:\n"
                f"{pp.pformat(valid_params)}"
            )

    @property
    def parameters(self) -> dict:
        """
        Returns a dictionary of all parameters that have been generated for a
        single compartment.

        Returns
        -------
        dict
        """
        d_out = {}
        for i in [self._params, self._g_couples]:
            if i:
                d_out.update(i)
        if self._dspike_params:
            for d in self._dspike_params.values():
                d_out.update(d)
        if self._ephys_object:
            d_out.update(self._ephys_object.parameters)
        return d_out

    @property
    def events(self) -> dict:
        """
        Returns a dictionary of all dSpike events created for a single dendrite.

        Returns
        -------
        dict
            Keys: event names, values: events conditions.
        """
        return self._events if self._events else {}

    @property
    def event_names(self) -> list:
        """
        Returns a list of all dSpike event names created for a single dendrite.

        Returns
        -------
        list
        """
        if not self._events:
            return []
        return list(self._events.keys())
