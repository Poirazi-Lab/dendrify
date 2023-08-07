import pprint as pp
from copy import deepcopy
from typing import List, Optional, Tuple, Union

from brian2 import NeuronGroup, Synapses, defaultclock
from brian2.units import Quantity, mV

from .compartment import Compartment, Dendrite, Soma
from .utils import DimensionlessCompartmentError, get_logger

logger = get_logger(__name__)


class NeuronModel:
    """
    Creates a multicompartmental neuron model by connecting individual
    compartments and merging their equations, parameters and custom events.This
    model can then be used for creating a population of neurons through Brian's
    :doc:`NeuronGroup <brian2:reference/brian2.groups.neurongroup.NeuronGroup>`.
    This class also contains useful methods for managing model properties and
    for automating the initialization of custom events and simulation parameters.

    .. tip::

       Dendrify aims to facilitate the development of reduced,
       **few-compartmental** I&F models that help us study how key dendritic
       properties may affect network-level functions. It is not designed to
       substitute morphologically and biophysically detailed neuron models,
       commonly used for highly-accurate, single-cell simulations. If you are
       interested in the latter category of models, please see Brian's
       :doc:`SpatialNeuron
       <brian2:reference/brian2.spatialneuron.spatialneuron.SpatialNeuron>`.

    Parameters
    ----------
    connections : list[tuple[Compartment, Compartment, str  | Quantity]]
        A description of how the various compartments belonging to the same
        neuron model should be connected.
    cm : ~brian2.units.fundamentalunits.Quantity, optional
        Specific capacitance (usually μF / cm^2).
    gl : ~brian2.units.fundamentalunits.Quantity, optional
        Specific leakage conductance (usually μS / cm^2).
    r_axial : ~brian2.units.fundamentalunits.Quantity, optional
        Axial resistance (usually Ohm * cm).
    v_rest : ~brian2.units.fundamentalunits.Quantity, optional
        Resting membrane voltage.
    scale_factor : float, optional
        A global area scale factor, by default ``1.0``.
    spine_factor : float, optional
        A dendritic area scale factor to account for spines, by default ``1.0``.

    Warning
    -------
    Parameters set here affect all model compartments and can override any
    compartment-specific parameters.

    Example
    -------
    >>> # Valid format: [*(x, y, z)], where
    >>> # x -> Soma or Dendrite object
    >>> # y -> Soma or Dendrite object other than x
    >>> # z -> 'half_cylinders' or 'cylinder_ + name' or brian2.nS unit
    >>> #      (by default 'half_cylinders')
    >>> soma = Soma(...)
    >>> prox = Dendrite(...)
    >>> dist = Dendrite(...)
    >>> connections = [(soma, prox, 15*nS), (prox, dist, 10*nS)]
    >>> model = NeuronModel(connections)
    """

    def __init__(
        self,
        connections: List[Tuple[Compartment,
                                Compartment,
                                Union[str, Quantity, None]]],
        cm: Optional[Quantity] = None,
        gl: Optional[Quantity] = None,
        r_axial: Optional[Quantity] = None,
        v_rest: Optional[Quantity] = None,
        scale_factor: Optional[float] = 1.0,
        spine_factor: Optional[float] = 1.0
    ):
        self._compartments = None
        self._extra_equations = None
        self._extra_params = None
        self._graph = None
        self._parse_compartments(connections)
        self._set_properties(cm=cm, gl=gl,
                             r_axial=r_axial,
                             v_rest=v_rest,
                             scale_factor=scale_factor,
                             spine_factor=spine_factor)

    def __str__(self):
        equations = self.equations
        parameters = pp.pformat(self.parameters)
        events = pp.pformat(self.events, width=120)
        event_names = pp.pformat(self.event_names)
        txt = (f"\nOBJECT\n{6*'-'}\n{self.__class__}\n\n\n"
               f"EQUATIONS\n{9*'-'}\n{equations}\n\n\n"
               f"PARAMETERS\n{10*'-'}\n{parameters}\n\n\n"
               f"EVENTS\n{6*'-'}\n{event_names}\n\n\n"
               f"EVENT CONDITIONS\n{16*'-'}\n{events}\n\n\n"
               )
        return txt

    def _parse_compartments(self, comp_list):
        # Ensure that all compartments have a unique names
        ids, names = [], []
        for tup in comp_list:
            for i in tup:
                if isinstance(i, Compartment):
                    ids.append(id(i))
                    names.append(i.name)
        if len(set(ids)) != len(set(names)):
            raise ValueError(
                ("Please make sure that all compartments included to a single  "
                 "NeuronModel have unique names.")
            )
        # Start parsing
        self._compartments = []
        self._graph = []
        # Copy compartments to avoid modifying the original objects
        copied_list = self._copy_compartments(comp_list)
        for tup in copied_list:
            pre, post = tup[0], tup[1]
            # Store graph-like representation for debugging or visualization
            self._graph.append((pre.name, post.name))
            # Include all compartments in a list for easy access
            if pre not in self._compartments:
                self._compartments.append(pre)
            if post not in self._compartments:
                self._compartments.append(post)
             # Call the connect method from the Compartment class
            if len(tup) == 2:
                pre.connect(post)
            else:
                pre.connect(post, g=tup[2])
            # Check if all compartments are dimensionless or not
            is_dimensionless = [i.dimensionless for i in self._compartments]
            if True in is_dimensionless and False in is_dimensionless:
                raise DimensionlessCompartmentError(
                    "When creating a NeuronModel, either all of its\n"
                    "compartments must be dimensionless or none of them. "
                    "To resolve this issue, you\n"
                    "can perform one of the following:\n\n"
                    "1. Discard these parameters [length, diameter, cm,"
                    "gl, r_axial]\n   if you want to create dimensionless "
                    "compartments.\n\n"
                    "2. Discard these parameters [cm_abs, gl_abs] if you want to\n"
                    "   create compartments with physical dimensions."
                )

    def _copy_compartments(self, comp_list):
        error_msg = (
            "\n\nValid format: [*(x, y, z)]\n"
            f"{26*'-'}\n"
            "x -> Soma or Dendrite object.\n"
            "y -> Soma or Dendrite object other than x.\n"
            "z -> 'half_cylinders' or 'cylinder_ + name' or conductance unit.\n"
            "     (default: 'half_cylinders' if left blank).\n\n"
            "Example:\n"
            "[(comp1, comp2), (comp2, comp3, 10*nS)] \n"
        )
        used = {}  # Keep track of copied compartments to avoid duplicates
        new_list = []
        for tup in comp_list:
            # Ensure that users provide correct format
            if len(tup) < 2 or len(tup) > 3:
                raise ValueError(
                    f"Invalid number of arguments provided. {error_msg}"
                )
            # Ensure that users do not use objects that make no sense
            if not (isinstance(tup[0], Compartment) and
                    isinstance(tup[1], Compartment)):
                raise TypeError(
                    f"Invalid compartment type provided. {error_msg}"
                )
            # Prohibit self connections
            if tup[0] is tup[1]:
                raise ValueError(
                    f"ERROR: Cannot connect '{tup[0].name}' to itself. "
                    f"{error_msg}"
                )

            if tup[0].name in used:
                pre = used[tup[0].name]
            else:
                pre = deepcopy(tup[0])
                used[pre.name] = pre
            if tup[1].name in used:
                post = used[tup[1].name]
            else:
                post = deepcopy(tup[1])
                used[post.name] = post
            if len(tup) == 2:
                new_tup = (pre, post)
            elif len(tup) == 3:
                new_tup = (pre, post, tup[2])
            new_list.append(new_tup)
        return new_list

    def _set_properties(self, cm=None, gl=None, r_axial=None, v_rest=None,
                        scale_factor=1.0, spine_factor=1.0):

        params = {'cm': cm, 'gl': gl, 'r_axial': r_axial,
                  'scale_factor': scale_factor, 'spine_factor': spine_factor}

        for comp in self._compartments:
            if v_rest:
                comp._ephys_object.v_rest = v_rest
            if not comp.dimensionless and any(params.values()):
                for param, value in params.items():
                    setattr(comp._ephys_object, param, value)
            elif comp.dimensionless and any(params.values()):
                raise DimensionlessCompartmentError(
                    f"The dimensionless compartment '{comp.name}' cannot take "
                    "the \nfollowing parameters: "
                    "[cm, gl, r_axial, scale_factor, spine_factor]."
                )

    def config_dspikes(self, event_name: str,
                       threshold: Union[Quantity, None] = None,
                       duration_rise: Union[Quantity, None] = None,
                       duration_fall: Union[Quantity, None] = None,
                       reversal_rise: Union[Quantity, str, None] = None,
                       reversal_fall: Union[Quantity, str, None] = None,
                       offset_fall: Union[Quantity, None] = None,
                       refractory: Union[Quantity, None] = None
                       ):
        """
        Configure the parameters for dendritic spiking.

        Parameters
        ----------
        event_name : str
            A unique name referring to a specific dSpike type.
        threshold : ~brian2.units.fundamentalunits.Quantity, optional
            The membrane voltage threshold for dendritic spiking.
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

        for comp in self._compartments:
            if isinstance(comp, Dendrite) and comp._dspike_params:
                ID = f"{event_name}_{comp.name}"
                dt = defaultclock.dt
                d = {f"Vth_{ID}": threshold,
                     f"duration_rise_{ID}": comp._timestep(duration_rise, dt),
                     f"duration_fall_{ID}": comp._timestep(duration_fall, dt),
                     f"E_rise_{event_name}": comp._ionic_param(reversal_rise),
                     f"E_fall_{event_name}": comp._ionic_param(reversal_fall),
                     f"offset_fall_{ID}": comp._timestep(offset_fall, dt),
                     f"refractory_{ID}": comp._timestep(refractory, dt)}
                comp._dspike_params[ID].update(d)

    def make_neurongroup(self,
                         N: int,
                         method: str = 'euler',
                         threshold: Optional[str] = None,
                         reset: Optional[str] = None,
                         second_reset: Optional[str] = None,
                         spike_width: Optional[Quantity] = None,
                         refractory: Union[Quantity, str, bool] = False,
                         init_rest: bool = True,
                         init_events: bool = True,
                         show: bool = False,
                         **kwargs
                         ) -> Union[NeuronGroup, Tuple]:
        """
        Returns a Brian2 NeuronGroup object from a NeuronModel. If a second
        reset is provided, it also returns a Synapses object to implement
        somatic action potentials with a more realistic shape which also unlocks 
        dendritic backpropagation. This method can also take all parameters that
        are accepted by Brian's
        :doc:`NeuronGroup <brian2:reference/brian2.groups.neurongroup.NeuronGroup>`.

        Parameters
        ----------
        N : int
            The number of neurons in the group.
        method : str, optional
            The numerical integration method. Either a string with the name of a
            registered method (e.g. "euler") or a function that receives an
            `Equations` object and returns the corresponding abstract code, by
            default ``'euler'``.
        threshold : str, optional
            The condition which produces spikes. Should be a single line boolean
            expression.
        reset : str, optional
            The (possibly multi-line) string with the code to execute on reset.
        refractory : (Quantity, str), optional
            Either the length of the refractory period (e.g. ``2*ms``), a string
            expression that evaluates to the length of the refractory period
            after each spike (e.g. ``'(1 + rand())*ms'``), or a string expression
            evaluating to a boolean value, given the condition under which the
            neuron stays refractory after a spike (e.g. ``'v > -20*mV'``).
        second_reset : str, optional
            Option to include a second reset for more realistic somatic spikes.
        spike_width : Quantity, optional
            The time interval between the two resets.
        init_rest : bool, optional
            Option to automatically initialize the voltages of all compartments
            at the specified resting potentials, by default True.
        init_events : bool, optional
            Option to automatically initialize all custom events that required
            for dendritic spiking, by default True.
        show : bool, optional
            Option to print the automatically initialized parameters, by default
            False.
        **kwargs: optional
            All other parameters accepted by Brian's NeuronGroup.

        Returns
        -------
        Union[NeuronGroup, Tuple]
            If no second reset is added, it returns a NeuronGroup object.
            Otherwise, it returns a tuple of (NeuronGroup, Synapses) objects.
        """

        group = NeuronGroup(N,
                            method=method,
                            threshold=threshold,
                            reset=reset,
                            refractory=refractory,
                            model=self.equations,
                            events=self.events,
                            namespace=self.parameters,
                            **kwargs)

        if init_rest:
            for comp in self._compartments:
                if show:
                    print(
                        f"Setting V_{comp.name} = {comp._ephys_object.v_rest}")
                setattr(group, f'V_{comp.name}', comp._ephys_object.v_rest)

        if init_events:
            if self.event_actions:
                for event, action in self.event_actions.items():
                    if show:
                        print(f"Setting run_on_event('{event}', '{action}')")
                    group.run_on_event(event, action)

        ap_reset = None
        if any([second_reset, spike_width]):
            txt = (
                "If you wish to have a more realistic action potential shape, "
                "please provide \nvalid values for both [second_reset] and "
                "[spike_width]."
            )
            if not all([second_reset, spike_width]):
                raise ValueError(txt)
            try:
                ap_reset = Synapses(group, group,
                                    on_pre=second_reset,
                                    delay=spike_width)
                ap_reset.connect(j='i')

            except Exception:
                raise ValueError(txt)

        return group, ap_reset if ap_reset else group

    def add_params(self, params_dict: dict):
        """
        Allows specifying extra/custom parameters.

        Parameters
        ----------
        params_dict : dict
            A dictionary of parameters.
        """
        if not self._extra_params:
            self._extra_params = {}
        self._extra_params.update(params_dict)

    def add_equations(self, eqs: str):
        """
        Allows adding custom equations.

        Parameters
        ----------
        eqs : str
            A string of Brian-compatible equations.
        """
        if not self._extra_equations:
            self._extra_equations = f"{eqs}"
        else:
            self._extra_equations += f"\n{eqs}"

    def as_graph(self, figsize: list = [6, 4], fontsize: int = 10, fontcolor: str = 'white',
                 scale_nodes: float = 1, color_soma: str = '#4C6C92',
                 color_dendrites: str = '#A7361C', alpha: float = 1,
                 scale_edges: float = 1, seed: Optional[int] = None):
        """
        Plots a graph-like representation of a NeuronModel using the
        :doc:`Graph <networkx:reference/classes/graph>` class and the
        :doc:`Fruchterman-Reingold force-directed algorithm
        <networkx:reference/generated/networkx.drawing.layout.spring_layout>`
        from `Networkx <https://networkx.org/>`_.

        Parameters
        ----------
        fontsize : int, optional
            The size in pt of each node's name, by default ``10``.
        fontcolor : str, optional
            The color of each node's name, by default ``'white'``.
        scale_nodes : float, optional
            Percentage change in node size, by default ``1``.
        color_soma : str, optional
            Somatic node color, by default ``'#4C6C92'``.
        color_dendrites : str, optional
            Dendritic nodes color, by default ``'#A7361C'``.
        alpha : float, optional
            Nodes color opacity, by default ``1``.
        scale_edges : float, optional
            The percentage change in edges length, by default ``1``.
        seed : int, optional
            Set the random state for deterministic node layouts, by default
            ``None``.
            .
        """
        import matplotlib.pyplot as plt
        import networkx as nx

        # Separate soma from dendrites
        soma, dendrites = [], []
        for comp in self._compartments:
            target = soma if isinstance(comp, Soma) else dendrites
            target.append(comp.name)

        # Make graph
        G = nx.Graph()
        G.add_edges_from(self._graph)

        # Visualize it
        fig, ax = plt.subplots(figsize=figsize)
        for d in ['right', 'top', 'left', 'bottom']:
            ax.spines[d].set_visible(False)
        pos = nx.spring_layout(G, fixed=soma, pos={soma[0]: (0, 0)},
                               k=0.05*scale_edges, iterations=100,
                               seed=seed)
        nx.draw_networkx_nodes(G, pos, nodelist=dendrites,
                               node_color=color_dendrites,
                               node_size=1200*scale_nodes, margins=0.1,
                               ax=ax, alpha=alpha)
        nx.draw_networkx_nodes(G, pos, nodelist=soma, node_color=color_soma,
                               node_size=1200*scale_nodes, ax=ax, alpha=alpha)
        nx.draw_networkx_edges(G, pos, alpha=0.5, width=1, ax=ax)
        nx.draw_networkx_labels(G, pos, ax=ax, font_color=fontcolor,
                                font_size=fontsize)
        ax.set_title('Model graph', weight='bold')
        fig.tight_layout()
        plt.show()

    @ property
    def equations(self) -> str:
        """
        Returns a string containing all model equations.

        Returns
        -------
        str
            All model equations.
        """
        all_eqs = [i._equations for i in self._compartments]
        if self._extra_equations:
            all_eqs.append(self._extra_equations)
        return '\n\n'.join(all_eqs)

    @ property
    def parameters(self) -> dict:
        """
        Returns a dictionary containing all model parameters.

        Returns
        -------
        dict
            All model parameters.
        """
        d = {}
        for i in self._compartments:
            d.update(i.parameters)
        if self._extra_params:
            d.update(self._extra_params)
        return d

    @ property
    def events(self) -> dict:
        """
        Returns a dictionary containing all model custom events for dendritic
        spiking.

        Returns
        -------
        dict
            All model custom events for dendritic spiking.
        """
        d_out = {}
        dendrites = [i for i in self._compartments if isinstance(i, Dendrite)]
        all_events = [i._events for i in dendrites if i._events]
        for d in all_events:
            d_out.update(d)
        return d_out

    @ property
    def event_names(self) -> list:
        """
        Returns a list of all event names for dendritic spiking.

        Returns
        -------
        list
            All event names for dendritic spiking
        """
        return list(self.events.keys())

    @ property
    def event_actions(self) -> dict:
        """
        Returns a dictionary containing all event actions for dendritic
        spiking.

        Returns
        -------
        list
            All event actions for dendritic spiking
        """
        d_out = {}
        dendrites = [i for i in self._compartments if isinstance(i, Dendrite)]
        all_actions = [i._event_actions for i in dendrites if i._event_actions]
        for d in all_actions:
            d_out.update(d)
        return d_out


class PointNeuronModel(Compartment):
    """
    Like a :class:`.NeuronModel` but for point-neuron (single-compartment)
    models.

    Parameters
    ----------
    name : str
        A name used to tag all equations and parameters.
    model : str, optional
        A keyword for accessing Dendrify's library models. Custom models can
        also be provided but they should be in the same formattable structure as
        the library models. Available options: ``'leakyIF'`` (default),
        ``'adaptiveIF'``, ``'adex'``.
    length : ~brian2.units.fundamentalunits.Quantity, optional
        The point neuron's length.
    diameter : ~brian2.units.fundamentalunits.Quantity, optional
        The point neuron's diameter.
    cm : ~brian2.units.fundamentalunits.Quantity, optional
        Specific capacitance (usually μF / cm^2).
    gl : ~brian2.units.fundamentalunits.Quantity, optional
        Specific leakage conductance (usually μS / cm^2).
    cm_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute capacitance (usually pF).
    gl_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute leakage conductance (usually nS).
    v_rest : ~brian2.units.fundamentalunits.Quantity, optional
        Resting membrane voltage.
    """

    def __init__(
        self,
        name: str,
        model: str = 'leakyIF',
        cm_abs: Optional[Quantity] = None,
        gl_abs: Optional[Quantity] = None,
        v_rest: Optional[Quantity] = None,
        length: Optional[Quantity] = None,
        diameter: Optional[Quantity] = None,
        cm: Optional[Quantity] = None,
        gl: Optional[Quantity] = None,

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
            v_rest=v_rest,
        )

    def make_neurongroup(self, N: int, **kwargs) -> NeuronGroup:
        group = NeuronGroup(N, model=self.equations,
                            namespace=self.parameters,
                            **kwargs)
        setattr(group, f'V_{self.name}', self._ephys_object.v_rest)
        return group

    def add_params(self, params_dict: dict):
        """
        Allows specifying extra/custom parameters.

        Parameters
        ----------
        params_dict : dict
            A dictionary of parameters.
        """
        if not self._extra_params:
            self._extra_params = {}
        self._extra_params.update(params_dict)

    def add_equations(self, eqs: str):
        """
        Allows adding custom equations.

        Parameters
        ----------
        eqs : str
            A string of Brian-compatible equations.
        """
        if not self._extra_equations:
            self._extra_equations = f"{eqs}"
        else:
            self._extra_equations += f"\n{eqs}"

    def connect(self):
        raise NotImplementedError(
            "Point neurons do not have compartments that need to be connected."
        )

    def dspikes(self):
        raise NotImplementedError(
            "Dendritic spikes have not been implemented fot point-neuron models."
        )
