from brian2 import Network, NeuronGroup, StateMonitor
from brian2.units import *
from matplotlib.pyplot import rcParams, show, subplots
from matplotlib.widgets import Button, Slider
from brian2 import prefs
import time

prefs.codegen.target = 'cython'

class Playground:
    SIMULATION_PARAMS = {
        'idle_duration': 5 * ms,
        'stim_duration': 100 * ms,
        'post_stim_duration': 50 * ms
    }

    MODEL_PARAMS = {
        'EL': -70. * mvolt,
        'C': 80 * pF,
        'gL': 3 * nS,
        'reversal_fall': -89 * mV
    }

    SLIDER_PARAMS = {
        'current': [0, 200, 120, 5, pA],
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
    
    def start(self, timeit=False) -> None:
        """
        Starts the simulation and sets up the interactive plot.

        Parameters
        ----------
        timeit : bool, optional
            If True, the simulation time will be measured and printed. Default is False.

        Returns
        -------
        None
        """
        fig, ax1, ax2, sliders, reset_button = self._setup_plot()
        neuron, M, net = self._create_brian_objects()
        net.store()
        self._run_simulation(net, neuron, self.slider_params['current'][2] * pA,
                             timeit=timeit)
        line1, = ax1.plot(M.t / ms, M.V[0] / mV)
        line2, = ax2.plot(M.t / ms, M.g_pos[0] / nS, label='g_rise', c='black')
        line3, = ax2.plot(M.t / ms, -M.g_neg[0] / nS, label='- g_fall', c='firebrick')
        ax2.legend()

        reset_button.on_clicked(lambda event: self._reset(event, sliders))
        for slider in sliders:
            slider.on_changed(
                lambda val: self._update(
                    val, net, neuron, M, sliders, ax1, ax2, line1, line2, line3
                )
            )
        show()

    def set_simulation_params(self, user_sim_params: dict) -> None:
        """
        Set simulation parameters.

        Parameters
        ----------
        user_sim_params : dict
            A dictionary containing user-defined simulation parameters. Valid
            keys are:
            - 'idle_duration': Duration of idle time in milliseconds (ms) before the stimulation starts.
            - 'stim_duration': Duration of the stimulation period in milliseconds (ms).
            - 'post_stim_duration': Duration of the time in milliseconds (ms) after the stimulation ends.

        Raises
        ------
        KeyError
            If invalid keys are provided.

        """
        invalid_keys = [key for key in user_sim_params if key not in self.simulation_params]
        if invalid_keys:
            raise KeyError(
                f"The keys {invalid_keys} are not valid for simulation parameters. "
                f"Valid keys are: {list(self.simulation_params.keys())}"
            )
        self.simulation_params.update(user_sim_params)

    def set_model_params(self, user_model_params: dict) -> None:
        invalid_keys = [key for key in user_model_params if key not in self.model_params]
        if invalid_keys:
            raise KeyError(
                f"The keys {invalid_keys} are not valid for model parameters. "
                f"Valid keys are: {list(self.model_params.keys())}"
            )
        self.model_params.update(user_model_params)

    def set_slider_params(self, user_slider_params: dict) -> None:
        invalid_keys = [key for key in user_slider_params if key not in self.slider_params]
        if invalid_keys:
            raise KeyError(
                f"The keys {invalid_keys} are not valid for slider parameters. "
                f"Valid keys are: {list(self.slider_params.keys())}"
            )
        self.slider_params.update(user_slider_params)

    def _create_brian_objects(self):
        neuron = NeuronGroup(1, model=self.EQUATIONS, method='euler',
                             events=self.EVENT, namespace=self.model_params)
        neuron.namespace.update(self._initial_slider_values())
        neuron.run_on_event('dspike', 'spiketime = t; check = 1')
        neuron.V = self.model_params['EL']
        neuron.check = 0
        M = StateMonitor(neuron, ['V', 'g_pos', 'g_neg'], record=True)
        net = Network(neuron, M)
        return neuron, M, net

    def _run_simulation(self, net, neuron, current, timeit=False):
        if timeit:
            t0 = time.time()
        net.run(self.simulation_params['idle_duration'])
        neuron.I_ext = current
        net.run(self.simulation_params['stim_duration'])
        neuron.I_ext = 0 * pA
        net.run(self.simulation_params['post_stim_duration'])
        if timeit:
            print(f"Simulation time: {time.time() - t0:.2f} s")

    def _setup_plot(self):
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

        fig, axes = subplots(2, 1, figsize=[9.5, 7], sharex=True)
        ax1, ax2 = axes
        fig.canvas.manager.set_window_title('dSpike Playground')
        fig.subplots_adjust(
            top=0.95, bottom=0.07, left=0.09, right=0.62, 
            hspace=0.15, wspace=0.2
        )
        ax1.set_ylabel('Voltage (mV)')
        ax2.set_ylabel('Conductance (nS)')
        ax2.set_xlabel('Time (ms)')
        ax1.grid(True)
        ax2.grid(True)
        ax1.set_title('Membrane', fontsize=11, fontweight='bold', loc='left')
        ax2.set_title('dSpike channels', fontsize=11, fontweight='bold', loc='left')
        fig.text(0.66, 0.962, "Parameters", fontsize=11, fontweight='bold')

        sliders = [
            Slider(
                fig.add_axes([0.8, 0.9 - i * 0.05, 0.15, 0.025]),
                f'{label} ({unit}) ', valmin, valmax,
                valinit=valinit, valstep=valstep, track_color='0.92'
            )
            for i, (label, (valmin, valmax, valinit, valstep, unit)) in enumerate(self.slider_params.items())
        ]

        ax_reset = fig.add_axes([0.8, 0.45, 0.15, 0.025])
        reset_button = Button(ax_reset, 'Reset', color='0.92', hovercolor='0.95')

        return fig, ax1, ax2, sliders, reset_button

    def _reset(self, event, sliders):
        for slider in sliders:
            slider.reset()

    def _update(self, val, net, neuron, M, sliders, ax1, ax2, line1, line2, line3):
        net.restore()
        neuron.namespace.update({
            'threshold': sliders[1].val * mV,
            'g_rise': sliders[2].val * nS,
            'g_fall': sliders[3].val * nS,
            'duration_rise': sliders[4].val * ms,
            'duration_fall': sliders[5].val * ms,
            'offset_fall': sliders[6].val * ms,
            'refractory': sliders[7].val * ms,
            'reversal_rise': sliders[8].val * mV
        })
        self._run_simulation(net, neuron, sliders[0].val * pA)
        line1.set_ydata(M.V[0] / mV)
        line2.set_ydata(M.g_pos[0] / nS)
        line3.set_ydata(-M.g_neg[0] / nS)
        ax1.set_ylim(top=max(M.V[0] / mV) + 2, bottom=min(M.V[0] / mV) - 2)
        ax2.set_ylim(top=max(M.g_pos[0] / nS) + 2, bottom=min(-M.g_neg[0] / nS) - 2)

    def _initial_slider_values(self):
        return {key: params[2] * params[-1] for key, params in self.slider_params.items()}


test = Playground()
test.start()
