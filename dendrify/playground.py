from brian2 import Network, NeuronGroup, StateMonitor
from brian2.units import *
from matplotlib.pyplot import rcParams, show, style, subplots
from matplotlib.widgets import Button, Slider


class Playground:
    SIMULATION_PARAMS = {
        'idle_duration': 5 * ms,
        'stim_duration': 100 * ms,
        'post_stim_duration': 50 * ms
    }

    MODEL_PARAMS = {
        'threshold': -40. * mvolt,
        'g_rise': 20. * nS,
        'g_fall': 20. * nS,
        'EL': -70. * mvolt,
        'C': 80 * pF,
        'gL': 3 * nS,
        'E_pos': 70. * mV,
        'E_neg': -89. * mV,
        'refractory_pos': 5. * ms,
        'offset_neg': 1. * ms,
        'duration_pos': 2. * ms,
        'duration_neg': 3. * ms
    }

    SLIDER_PARAMS = {
        'current': [0, 200, 120, 5],
        'threshold': [-70, 0, -40, 0.5],
        'g_rise': [0, 40, 20, 0.5],
        'g_fall': [0, 40, 20, 0.5],
        'duration_rise': [0, 50, 2, 0.5],
        'duration_fall': [0, 50, 3, 0.5],
        'offset_fall': [0, 55, 1, 0.5],
        'refractory': [0, 100, 5, 0.5],
        'reversal_rise': [70, 136, 70, (70, 136)]
    }

    EQUATIONS = """
        dV/dt = (gL * (EL-V) + I) / C  :volt
        I = I_ext + I_pos + I_neg  :amp
        I_ext  :amp
        I_pos = g_pos * (E_pos-V)  :amp
        I_neg = g_neg * (E_neg-V)  :amp
        g_pos = g_rise * int(t <= spiketime + duration_pos) * check :siemens
        g_neg = g_fall * int(t <= spiketime + offset_neg + duration_neg) * int(t >= spiketime + offset_neg) * check   :siemens
        spiketime  :second
        check :1
    """

    EVENT = {'dspike': 'V >= threshold and t >= spiketime + refractory_pos * check'}

    def __init__(self):
        self.simulation_params = self.SIMULATION_PARAMS.copy()
        self.model_params = self.MODEL_PARAMS.copy()
        self.slider_params = self.SLIDER_PARAMS.copy()

    def set_simulation_params(self, user_sim_params: dict) -> None:
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
        neuron.run_on_event('dspike', 'spiketime = t; check = 1')
        neuron.V = self.model_params['EL']
        neuron.check = 0
        M = StateMonitor(neuron, ['V', 'g_pos', 'g_neg'], record=True)
        net = Network(neuron, M)
        return neuron, M, net

    def _run_simulation(self, net, neuron, current):
        net.run(self.simulation_params['idle_duration'])
        neuron.I_ext = current
        net.run(self.simulation_params['stim_duration'])
        neuron.I_ext = 0 * pA
        net.run(self.simulation_params['post_stim_duration'])

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

        units = {
            'current': 'pA',
            'threshold': 'mV',
            'g_rise': 'nS',
            'g_fall': 'nS',
            'duration_rise': 'ms',
            'duration_fall': 'ms',
            'offset_fall': 'ms',
            'refractory': 'ms',
            'reversal_rise': 'mV'
        }

        sliders = []
        for i, (label, params) in enumerate(self.slider_params.items()):
            valmin, valmax, valinit, valstep = params
            ax = fig.add_axes([0.8, 0.9 - i * 0.05, 0.15, 0.025])
            slider = Slider(
            ax, f'{label} ({units[label]}) ', valmin, valmax,
            valinit=valinit, valstep=valstep, track_color='0.92'
)
            sliders.append(slider)

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
            'duration_pos': sliders[4].val * ms,
            'duration_neg': sliders[5].val * ms,
            'offset_neg': sliders[6].val * ms,
            'refractory_pos': sliders[7].val * ms,
            'E_pos': sliders[8].val * mV})
        self._run_simulation(net, neuron, sliders[0].val * pA)
        line1.set_ydata(M.V[0] / mV)
        line2.set_ydata(M.g_pos[0] / nS)
        line3.set_ydata(-M.g_neg[0] / nS)
        ax1.set_ylim(top=max(M.V[0] / mV) + 2, bottom=min(M.V[0] / mV) - 2)
        ax2.set_ylim(top=max(M.g_pos[0] / nS) + 2, bottom=min(-M.g_neg[0] / nS) - 2)

    def main(self):
        neuron, M, net = self._create_brian_objects()
        net.store()
        fig, ax1, ax2, sliders, reset_button = self._setup_plot()
        self._run_simulation(net, neuron, self.slider_params['current'][2] * pA)
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


test = Playground()
# test.set_simulation_params({'idle_duration': 5 * ms, 'post_stim_duration': 590 * ms})
# test.set_model_params({'C': 180 * pF, 'gL': 3 * nS})
test.main()
