import sys

import __main__ as main
from brian2.units import mV

from .compartment import Compartment, Dendrite, Soma

# The as_graph() method also imports matplotlib and networkx when called.


class NeuronModel:
    """
    Merges multiple Compartment objects into a single model. It also comptains
    useful functions for custom event handling and parameter initialisation.

    ---------------------------------------------------------------------------
    * PARAMETERS (user-defined)

    neuron: str
        Specifies which _compartments to collect from Compartment._neuron_types.

    namespace: dict, optional
        A dictionary mapping identifier names to parameter objects.

    ---------------------------------------------------------------------------
    * PROPERTIES (handled by class functions but accessible to user)

    _compartments: list
        A list of Compartment objects that are grouped by their neuron
        attribute.

    _linked_neurongroup: brian2.NeuronGroup
        Reference to a NeuronGroup object that is linked to a specified
        NeuronModel onject.

    _varscope: dict
        Used to allow access to global variables of the main simulation script.
    """
    defaults = {"E_AMPA": 0 * mV,
                "E_NMDA": 0 * mV,
                "E_GABA": -80 * mV,
                "alpha": 0.062,
                "E_Na": 70 * mV,
                "E_K": -89 * mV,
                "E_Ca": 136 * mV,
                "Mg": 1.0,
                "beta": 3.57,
                "gamma": 0}

    def __init__(self, connections, **kwargs):
        self._namespace = None
        self._compartments = None
        self._linked_neurongroup = None
        self._varscope = None
        self._extra_equations = None
        self._extra_params = None
        self._graph = None
        self.parse_compartments(connections)
        self.set_properties(**kwargs)

    def __str__(self):
        """
        Prints useful information about a NeuronModel object.
        Usage -> print(onjectName)
        """

        equations = self.equations.replace('\n', '\n    ')

        if self.parameters:
            params_sorted = {key: self.parameters[key]
                             for key in sorted(self.parameters)}

            parameters = '\n'.join([f"    '{i[0]}': {i[1]}"
                                    for i in params_sorted.items()])
        else:
            parameters = '   None'

        if self._extra_params:
            extra_params_sorted = {key: self._extra_params[key]
                                   for key in sorted(self._extra_params)}
            extra_params = '\n'.join([f"    '{i[0]}': {i[1]}"
                                      for i in extra_params_sorted.items()])
        else:
            extra_params = '   None'

        events = '\n'.join([f"    '{key}': '{self.events[key]}'"
                            for key in self.events
                            ]) if self.events else '    None'

        msg = (f"OBJECT TYPE:\n\n  {self.__class__}\n\n"
               f"{'-'*45}\n\n"
               "PROPERTIES (type): \n\n"
               f"\u2192 equations (str):\n    {equations}\n\n"
               f"\u2192 parameters (dict):\n{parameters}\n\n"
               f"\u2192 events (dict):\n{events}\n"
               f"\n{'-'*45}\n\n"
               f"USEFUL ATTRIBUTES:\n\n"
               f"\u2192 _linked_neurongroup:\n    {self._linked_neurongroup}\n\n"
               f"\u2192 _extra_equations:\n    {self._extra_equations}\n\n"
               f"\u2192 _extra_params:\n{extra_params}\n")
        return msg

    def parse_compartments(self, comp_list):
        error_msg = (
            "\nValid format: [*(x, y, z)] \n"
            "- x -> Soma or Dendrite object\n"
            "- y -> Soma or Dendrite object other than x\n"
            "- z -> 'half_cylinders' or 'cylinder_ + name' or brian2.nS unit\n"
            "       (default is 'half_cylinders' if left blank)\n\n"
            "Example:\n"
            "[(comp1, comp2), (comp2, comp3, 10*nS), "
            "(comp3, comp4, 'cylinder_c3')]\n")

        self._compartments = []
        self._graph = []
        for comp in comp_list:
            pre, post = comp[0], comp[1]
            # Prohibit self connections
            if pre is post:
                print(f"ERROR: Cannot connect '{pre.tag}' to itself.")
                print(error_msg)
                sys.exit()
            # Ensure that users do not use objects that make no sense
            if not (isinstance(pre, Compartment) and
                    isinstance(post, Compartment)):
                print(f"ERROR: Unknown compartment type provided.")
                print(error_msg)
                sys.exit()
            # Store graph-like representation for debugging or visualization
            self._graph.append((pre.tag, post.tag))
            # Include all compartments in a list for easy access
            if pre not in self._compartments:
                self._compartments.append(pre)
            if post not in self._compartments:
                self._compartments.append(post)
            # Call the connect method from the Compartment class
            if len(comp) == 2:
                pre.connect(post)
            else:
                pre.connect(post, g=comp[2])

    def set_properties(self, cm=None, gl=None, r_axial=None, v_rest=None,
                       scale_factor=None, spine_factor=None):
        for i in self._compartments:
            if cm and (not i._ephys_object.cm):
                i._ephys_object.cm = cm
            if gl and (not i._ephys_object.gl):
                i._ephys_object.gl = gl
            if r_axial and (not i._ephys_object.r_axial):
                i._ephys_object.r_axial = r_axial
            if v_rest and (not i._ephys_object.v_rest):
                i._ephys_object.v_rest = v_rest
            if scale_factor:
                i._ephys_object.scale_factor = scale_factor
            if spine_factor:
                if isinstance(i, Dendrite):
                    i._ephys_object.spine_factor = spine_factor

    def dspike_properties(self, channel=None, tau_rise=None, tau_fall=None,
                          offset_fall=None, refractory=None):
        # Make sure user provides a valid option:
        if channel not in ['Na', 'Ca']:
            print("Please select a valid dendritic spike type ('Na' or 'Ca')")
            sys.exit()
        # Choose param names based on user input:
        if channel == 'Na':
            dspike_params = {'refractory_Na': refractory,
                             'offset_Kn': offset_fall,
                             'tau_Na': tau_rise,
                             'tau_Kn': tau_fall}
        else:
            dspike_params = {'refractory_Ca': refractory,
                             'offset_Kc': offset_fall,
                             'tau_Ca': tau_rise,
                             'tau_Kc': tau_fall}
        self.add_params(dspike_params)

    def add_params(self, params_dict):
        if not self._extra_params:
            self._extra_params = {}
        self._extra_params.update(params_dict)

    def add_equations(self, eqs):
        if not self._extra_equations:
            self._extra_equations = f"{eqs}"
        else:
            self._extra_equations += f"\n{eqs}"

    def link(self, ng, automate='all', verbose=None):
        """
        Used to create a link between a NeuronModel and its corresponding
        NeuronGroup object. Unlocks set_rest and handle_dspikes methods
        """
        self._namespace = ng.namespace
        self._varscope = main.__dict__

        items = main.__dict__.items()
        ng_name = [k for k, v in items if v is ng][0]
        self._linked_neurongroup = ng_name, ng

        if automate == 'all':
            self.set_rest(verbose)
            self.handle_events(verbose)

        elif automate == 'v_rest':
            self.set_rest(verbose)

        elif automate == 'events':
            self.handle_events(verbose)

    def set_rest(self, verbose=None):
        """
        Creates and runs executable code that initialises V rest across
        all NeuronModel _compartments. Setting verbose=True just prints it.
        """
        command = '{0}.V_{1} = {2}'

        # When model parameters are passed as dict to the NeuronGroup:
        if self._namespace:
            commands = [command.format(self._linked_neurongroup[0], i.tag,
                                       repr(self._namespace['EL_'+i.tag]))
                        for i in self._compartments]
        executable = '\n'.join(commands)
        if verbose:
            print(executable)
        exec(executable, self._varscope)

    def handle_events(self, verbose=None):
        """
        Creates and runs executable code that:
        a) Initialises custom event checkpoint variables.
        b) Specifies what happens during custom events.
        Setting verbose=True just prints all the code.
        """
        ng_name = self._linked_neurongroup[0]
        # Find all active _compartments:
        active_comps = [i for i in self._compartments if i._events]
        if active_comps == []:
            if verbose:
                print("\n<No custom events found>")
            return
        # Na spike vs Ca spike branches
        comps_Na = filter(lambda x: '_I_Na_' in x.event_actions, active_comps)
        comps_Ca = filter(lambda x: '_I_Ca_' in x.event_actions, active_comps)
        # Initial compditions for the custom events needed for dspikes:
        checks_Na = ('{0}.allow_I_Na_{1} = True \n'
                     '{0}.allow_I_Kn_{1} = False')
        checks_Ca = ('{0}.allow_I_Ca_{1} = True \n'
                     '{0}.allow_I_Kc_{1} = False')
        # Compartment specific initial compditions:
        checks_Na_comp = [checks_Na.format(ng_name, i.tag) for i in comps_Na]
        checks_Ca_comp = [checks_Ca.format(ng_name, i.tag) for i in comps_Ca]
        # All initial compditions and actions needed for dspikes:
        all_checks = checks_Na_comp + checks_Ca_comp
        all_actions = [i.event_actions for i in active_comps]
        # Megrge all actions and checks into a single string:
        commands = '\n'.join(all_checks + all_actions)

        executable = commands.replace('run_on_event',
                                      f'{ng_name}.run_on_event')
        if verbose:
            print(executable)
        exec(executable, self._varscope)

    def as_graph(self, fontsize=10, fontcolor='white', scale_nodes=1,
                 color_soma='#4C6C92', color_dendrites='#A7361C', alpha=1,
                 scale_edges=1, seed=None):
        import matplotlib.pyplot as plt
        import networkx as nx

        # Separate soma from dendrites
        soma, dendrites = [], []
        for comp in self._compartments:
            target = soma if isinstance(comp, Soma) else dendrites
            target.append(comp.tag)

        # Make graph
        G = nx.Graph()
        G.add_edges_from(self._graph)

        # Visualise it
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
    def equations(self):
        """
        Merges all compartment equations into a single string
        """
        all_eqs = [i._equations for i in self._compartments]
        if self._extra_equations:
            all_eqs.append(self._extra_equations)
        return '\n\n'.join(all_eqs)

    @property
    def parameters(self):
        d = {}
        for i in self._compartments:
            d.update(i.parameters)
        d.update(self.defaults)
        if self._extra_params:
            d.update(self._extra_params)
        return d

    @property
    def events(self):
        """
        Creates a dict of all custom events
        """
        d_out = {}
        all_events = [i._events for i in self._compartments
                      if i._events and isinstance(i, Dendrite)]
        for d in all_events:
            d_out.update(d)
        return d_out

    @property
    def event_actions(self):
        """
        Returns a string of all event_actions
        """
        all_actions = [i._event_actions for i in self._compartments
                       if i._event_actions and isinstance(i, Dendrite)]
        # for d in all_actions:
        #     d_out.update(d)
        return all_actions
