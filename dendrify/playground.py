from time import time

from brian2 import Network, NeuronGroup, StateMonitor
from brian2.units import Quantity, ms, mV, mvolt, nS, pA, pF
from matplotlib.pyplot import draw, rcParams, show, subplots
from matplotlib.widgets import Button, Slider, TextBox


class Playground:
    """
    A class that creates a graphical user interface for interactively visualizing,
    exploring, and calibrating dendritic spikes in Dendrify.
    """
    SIMULATION_PARAMS = {
        'idle_period': 5 * ms,
        'stim_time': 100 * ms,
        'post_stim_time': 50 * ms
    }

    MODEL_PARAMS = {
        'C': 80 * pF,
        'gL': 3 * nS,
        'EL': -70. * mvolt,
        'reversal_fall': -89 * mV
    }

    SLIDER_PARAMS = {
        'current': [0, 200, 120, 2, pA],
        'threshold': [-70, 0, -40, 0.5, mV],
        'g_rise': [0, 40, 20, 0.5, nS],
        'g_fall': [0, 40, 20, 0.5, nS],
        'duration_rise': [0, 50, 2, 0.5, ms],
        'duration_fall': [0, 50, 3, 0.5, ms],
        'offset_fall': [0, 55, 1, 0.5, ms],
        'refractory': [0, 100, 5, 0.5, ms],
        'reversal_rise': [70, 136, 70, (70, 136), mV]
    }

    EQUATIONS = """
        dV/dt = (gL * (EL-V) + I) / C  :volt
        I = I_ext + I_pos + I_neg  :amp
        I_ext  :amp
        I_pos = g_pos * (reversal_rise-V)  :amp
        I_neg = g_neg * (reversal_fall-V)  :amp
        g_pos = g_rise * int(t <= spiketime + duration_rise) * check :siemens
        g_neg = g_fall * int(t <= spiketime + offset_fall + duration_fall) * int(t >= spiketime + offset_fall) * check   :siemens
        spiketime  :second
        check :1
    """

    EVENT = {'dspike': 'V >= threshold and t >= spiketime + refractory * check'}

    def __init__(self):
        self.simulation_params = self.SIMULATION_PARAMS.copy()
        self.model_params = self.MODEL_PARAMS.copy()
        self.slider_params = self.SLIDER_PARAMS.copy()
        self.timeit = False

    def run(self, timeit=False) -> None:
        """
        Initializes the graphical environment, allowing the user to interact with
        the model by adjusting slider values, neuron parameters, and simulation
        parameters.

        Parameters
        ----------
        timeit : bool
            If True, prints the time taken to run a simulation.
        """
        self._setup_plot()
        self._create_brian_objects()
        self.net.store()
        self._run_simulation()
        self._initial_plot()
        self.timeit = timeit

        for slider in self.sliders:
            slider.on_changed(self._update_sliders)
        
        for neuron_box in self.neuron_boxes:
            neuron_box.on_submit(self._update_neuron_params)
            neuron_box.intial_text = neuron_box.text
        
        for sim_box in self.sim_boxes:
            sim_box.on_submit(self._update_simulation_params)
            sim_box.intial_text = sim_box.text

        self.reset_button.on_clicked(self._reset)

        show()

    def set_model_params(self, user_model_params: dict[str, Quantity]) -> None:
        """
        Updates the default model parameters with new values provided by the user.

        Parameters
        ----------
        user_model_params : dict[str, ~brian2.units.fundamentalunits.Quantity]
            A dictionary containing the new model parameters. Valid keys are:
            ``'C'``, ``'gL'``, ``'EL'``, and ``'reversal_fall'``. The
            corresponding values are expected to be in units of ``pF``, ``nS``,
            ``mV``, and ``mV``, respectively.

        Examples
        --------
        >>> playground.set_model_params({'C': 100 * pF, 'gL': 2 * nS, 'EL': -65 * mV})
        """
        self._update_params(self.model_params, user_model_params)

    def set_slider_params(self, user_slider_params: dict[str, list]) -> None:
        """
        Updates the default slider parameters with new values provided by the user.

        Parameters
        ----------
        user_slider_params : dict[str, list]
            A dictionary containing the new slider parameters. Valid keys are:
            
            - ``'current'``
            - ``'threshold'``
            - ``'g_rise'``
            - ``'g_fall'``
            - ``'duration_rise'``
            - ``'duration_fall'``
            - ``'offset_fall'``
            - ``'refractory'``
            - ``'reversal_rise'``
            
            The corresponding values must be in the format:
            ``[min value, max value, initial value, step, unit]``. The first four
            elements are expected to be integers or floats, while the last element
            must be a Brian2 :class:`~brian2.units.fundamentalunits.Quantity`.

        Examples
        --------
        >>> playground.set_slider_params({'current': [0, 300, 150, 5, pA],
        ...                               'threshold': [-65, 0, -30, 1.0, mV]})
        """

        self._update_params(self.slider_params, user_slider_params)

    def _update_params(self, params, user_params):
        invalid_keys = [key for key in user_params if key not in params]
        if invalid_keys:
            raise KeyError(f"Invalid keys: {invalid_keys}. Valid keys are: {list(params.keys())}")
        params.update(user_params)

    def _create_brian_objects(self):
        neuron = NeuronGroup(1, model=self.EQUATIONS, method='euler', events=self.EVENT, namespace=self.model_params)
        neuron.namespace.update(self._initial_slider_values())
        neuron.run_on_event('dspike', 'spiketime = t; check = 1')
        neuron.V = self.model_params['EL']
        neuron.check = 0
        M = StateMonitor(neuron, ['V', 'g_pos', 'g_neg'], record=True)
        net = Network(neuron, M)
        self.neuron, self.M, self.net = neuron, M, net

    def _run_simulation(self):
        if self.timeit:
            start = time()
        self.net.run(self.simulation_params['idle_period'])
        self.neuron.I_ext = self.sliders[0].val * pA
        self.net.run(self.simulation_params['stim_time'])
        self.neuron.I_ext = 0 * pA
        self.net.run(self.simulation_params['post_stim_time'])
        if self.timeit:
            print(f"Simulation run in {time()-start:.4f} s")

    def _setup_plot(self):
        self._configure_plot()
        scale = 0.75
        fig, axes = subplots(2, 1, figsize=[16*scale, 9*scale], sharex=True)
        ax1, ax2 = axes
        fig.canvas.manager.set_window_title('dSpike Playground')
        fig.subplots_adjust(top=0.95, bottom=0.07, left=0.09, right=0.6, hspace=0.15, wspace=0.2)
        ax1.set_ylabel('Voltage (mV)')
        ax2.set_ylabel('Conductance (nS)')
        ax2.set_xlabel('Time (ms)')
        ax1.grid(True)
        ax2.grid(True)
        ax1.set_title('Membrane response', fontsize=11, fontweight='bold', loc='left')
        ax2.set_title('dSpike channels', fontsize=11, fontweight='bold', loc='left')

        self.sliders = self._create_sliders(fig)
        self.neuron_boxes = self._create_neuron_boxes(fig)
        self.sim_boxes = self._create_simulation_boxes(fig)
        self.reset_button = self._create_reset_button(fig)

        self.fig, self.ax1, self.ax2 = fig, ax1, ax2

    def _initial_plot(self):
        self.line1, = self.ax1.plot(self.M.t / ms, self.M.V[0] / mV)
        self.line2, = self.ax2.plot(self.M.t / ms, self.M.g_pos[0] / nS, label='g_rise', c='black')
        self.line3, = self.ax2.plot(self.M.t / ms, -self.M.g_neg[0] / nS, label='- g_fall', c='firebrick')
        self.ax2.legend()

    def _configure_plot(self):
        rcParams.update({
            "axes.edgecolor": '0.97',
            "axes.facecolor": '0.97',
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "font.family": "Arial",
            "grid.color": "0.8",
            'grid.linestyle': ":",
            "legend.edgecolor": 'none',
            "legend.fontsize": 10,
            "xtick.color": 'none',
            "xtick.labelcolor": 'black',
            "xtick.labelsize": 10,
            "ytick.color": 'none',
            "ytick.labelcolor": 'black',
            "ytick.labelsize": 10
        })

    def _create_sliders(self, fig):
        sliders = []
        for i, (label, (valmin, valmax, valinit, valstep, unit)) in enumerate(self.slider_params.items()):
            ax = fig.add_axes([0.78, 0.92 - i * 0.045, 0.15, 0.025])
            slider = Slider(
                ax,
                f'{label} ({unit})  ', valmin, valmax,
                valinit=valinit, valstep=valstep, track_color='0.92'
            )
            sliders.append(slider)
            if i == 0:
                ax.set_title('Parameters', fontsize=11, fontweight='bold', loc='left', x=-0.8, y=1.1)
        return sliders

    def _create_reset_button(self, fig):
        ax_reset = fig.add_axes([0.82, 0.07, 0.07, 0.035])
        return Button(ax_reset, 'Reset', color='indianred', hovercolor='0.95')

    def _create_neuron_boxes(self, fig):
        text_boxes = {
            'C (pF)  ': (self.model_params["C"] / pF),
            'gL (nS)  ': (self.model_params["gL"] / nS),
            'EL (mV)  ': (self.model_params["EL"] / mV)
        }
        text_box_axes = [fig.add_axes([0.78, 0.445 - i * 0.05, 0.15, 0.03]) for i in range(len(text_boxes))]
        text_boxes_widgets = [
            TextBox(ax, label, initial=f'{value:.1f}', textalignment='center', color='0.95', hovercolor='1')
            for ax, (label, value) in zip(text_box_axes, text_boxes.items())
        ]
        text_box_axes[0].set_title('Neuron', fontsize=11, fontweight='bold', loc='left', x=-0.8, y=1.1)
        return text_boxes_widgets
    
    def _create_simulation_boxes(self, fig):
        text_boxes = {
            'idle_period (ms)  ': (self.simulation_params["idle_period"] / ms),
            'stim_time (ms)  ': (self.simulation_params["stim_time"] / ms),
            'post_stim_time (ms)  ': (self.simulation_params["post_stim_time"] / ms)
        }
        text_box_axes = [fig.add_axes([0.78, 0.24 - i * 0.05, 0.15, 0.03]) for i in range(len(text_boxes))]
        text_boxes_widgets = [
            TextBox(ax, label, initial=f'{value:.1f}', textalignment='center', color='0.95', hovercolor='1')
            for ax, (label, value) in zip(text_box_axes, text_boxes.items())
        ]
        text_box_axes[0].set_title('Protocol', fontsize=11, fontweight='bold', loc='left', x=-0.8, y=1.1)
        return text_boxes_widgets

    def _reset(self, event):
        for slider in self.sliders:
            slider.reset()
        for neuron_box in self.neuron_boxes:
            neuron_box.set_val(neuron_box.intial_text)
        for sim_box in self.sim_boxes:
            sim_box.set_val(sim_box.intial_text)
    
    def _update_sliders(self, val):
        self.net.restore()
        self.neuron.namespace.update({
            'threshold': self.sliders[1].val * mV,
            'g_rise': self.sliders[2].val * nS,
            'g_fall': self.sliders[3].val * nS,
            'duration_rise': self.sliders[4].val * ms,
            'duration_fall': self.sliders[5].val * ms,
            'offset_fall': self.sliders[6].val * ms,
            'refractory': self.sliders[7].val * ms,
            'reversal_rise': self.sliders[8].val * mV
        })
        self._run_simulation()
        self._update_plot()

    def _update_neuron_params(self, expr):
        self.net.restore()
        self.neuron.namespace.update({
            'C': float(self.neuron_boxes[0].text) * pF,
            'gL': float(self.neuron_boxes[1].text) * nS,
            'EL': float(self.neuron_boxes[2].text) * mV
        })
        self._run_simulation()
        self._update_plot()

    def _update_simulation_params(self, expr):
        self.net.restore()
        self.simulation_params.update({
            'idle_period': float(self.sim_boxes[0].text) * ms,
            'stim_time': float(self.sim_boxes[1].text) * ms,
            'post_stim_time': float(self.sim_boxes[2].text) * ms
        })
        self._run_simulation()
        self._update_plot(change_x=True)

    def _update_plot(self, change_x=False):
        if change_x:
            x = self.M.t / ms
            self.line1.set_xdata(x)
            self.line2.set_xdata(x)
            self.line3.set_xdata(x)
            self.ax1.set_xlim(left=min(x), right=max(x))
            self.ax2.set_xlim(left=min(x), right=max(x))
            
        self.line1.set_ydata(self.M.V[0] / mV)
        self.line2.set_ydata(self.M.g_pos[0] / nS)
        self.line3.set_ydata(-self.M.g_neg[0] / nS)
        self.ax1.set_ylim(top=max(self.M.V[0] / mV) + 2, bottom=min(self.M.V[0] / mV) - 2)
        self.ax2.set_ylim(top=max(self.M.g_pos[0] / nS) + 2, bottom=min(-self.M.g_neg[0] / nS) - 2)
        draw()

    def _initial_slider_values(self):
        return {key: params[2] * params[-1] for key, params in self.slider_params.items()}

