import pprint as pp
from typing import List, Optional, Tuple, Union

from brian2 import NeuronGroup, defaultclock
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
    kwargs : :class:`~brian2.units.fundamentalunits.Quantity`, optional
        Kwargs are used to specify important electrophysiological properties,
        such as the specific capacitance or resistance. For all available options
        see: :class:`.EphysProperties`.

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
    >>> soma = Soma('s', ...)
    >>> prox = Dendrite('p', ...)
    >>> dist = Dendrite('d', ...)
    >>> connections = [(soma, prox, 15*nS), (prox, dist, 10*nS)]
    >>> model = NeuronModel(connections)
    """

    def __init__(
        self,
        connections: List[Tuple[Compartment,
                                Compartment,
                                Union[str, Quantity, None]]],
        cm=None,
        gl=None,
        r_axial=None,
        v_rest=None,
        scale_factor=None,
        spine_factor=None
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
        self._connect_compartments(connections)

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

        error_msg = (
            "\n\nValid format: [*(x, y, z)] \n"
            "- x -> Soma or Dendrite object.\n"
            "- y -> Soma or Dendrite object other than x.\n"
            "- z -> 'half_cylinders' or 'cylinder_ + name' or conductance unit\n"
            "       (default: 'half_cylinders').\n\n"
            "Example:\n"
            "[(comp1, comp2), \n(comp2, comp3, 10*nS), \n"
            "(comp3, comp4, 'cylinder_comp3')]\n")

        self._compartments = []
        self._graph = []
        for comp in comp_list:
            pre, post = comp[0], comp[1]

            # Prohibit self connections
            if pre is post:
                raise ValueError(
                    f"ERROR: Cannot connect '{pre.name}' to itself. {error_msg}"
                )

            # Ensure that users do not use objects that make no sense
            if not (isinstance(pre, Compartment) and
                    isinstance(post, Compartment)):
                raise TypeError(
                    f"Invalid compartment type provided. {error_msg}"
                )

            # Store graph-like representation for debugging or visualization
            self._graph.append((pre.name, post.name))

            # Include all compartments in a list for easy access
            if pre not in self._compartments:
                self._compartments.append(pre)
            if post not in self._compartments:
                self._compartments.append(post)

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

    def _connect_compartments(self, comp_list):
        for comp in comp_list:
            pre, post = comp[0], comp[1]

            # Call the connect method from the Compartment class
            if len(comp) == 2:
                pre.connect(post)
            else:
                pre.connect(post, g=comp[2])

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
                         init_rest: bool = True,
                         init_events: bool = True,
                         show: bool = False,
                         *args, **kwargs
                         ) -> NeuronGroup:

        group = NeuronGroup(N, model=self.equations,
                            events=self.events,
                            namespace=self.parameters,
                            *args, **kwargs)

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

    def as_graph(self, fontsize: int = 10, fontcolor: str = 'white',
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
        fig, ax = plt.subplots()
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

    @property
    def equations(self) -> str:
        """
        Merges all compartments' equations into a single string.

        Returns
        -------
        str
            All model equations.
        """
        all_eqs = [i._equations for i in self._compartments]
        if self._extra_equations:
            all_eqs.append(self._extra_equations)
        return '\n\n'.join(all_eqs)

    @property
    def parameters(self) -> dict:
        """
        Merges all compartments' parameters into a dictionary.

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

    @property
    def events(self) -> dict:
        """
        Organizes all custom events for dendritic spiking into a dictionary.

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

    @property
    def event_names(self) -> list:
        """
        Creates a list of all event names for dendritic spiking.

        Returns
        -------
        list
            All event names for dendritic spiking
        """
        return list(self.events.keys())

    @property
    def event_actions(self) -> dict:
        """
        Creates a list of all event actions for dendritic spiking.

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

    def connect(self):
        raise NotImplementedError(
            "Point neurons do not comprise compartments that must be connected."
        )
