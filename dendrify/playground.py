from brian2 import Network, NeuronGroup, StateMonitor
from brian2.units import *
from matplotlib.pyplot import rcParams, show, subplots, draw
from matplotlib.widgets import Button, Slider, TextBox
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
    
    def start(self, timeit=True) -> None:
        fig, ax1, ax2, sliders, reset_button, text_boxes = self._setup_plot()
        neuron, M, net = self._create_brian_objects()
        net.store()
        self._run_simulation(net, neuron, self.slider_params['current'][2] * pA, timeit=timeit)
        line1, = ax1.plot(M.t / ms, M.V[0] / mV)
        line2, = ax2.plot(M.t / ms, M.g_pos[0] / nS, label='g_rise', c='black')
        line3, = ax2.plot(M.t / ms, -M.g_neg[0] / nS, label='- g_fall', c='firebrick')
        ax2.legend()

        reset_button.on_clicked(lambda event: self._reset(sliders, text_boxes))
        for slider in sliders:
            slider.on_changed(lambda val: self._update(val, net, neuron, M, sliders, ax1, ax2, line1, line2, line3))
        for text_box in text_boxes:
            text_box.on_submit(lambda expr: self._update_model_params(expr, net, neuron, M, text_boxes, ax1, ax2, line1, line2, line3))
        show()

    def set_simulation_params(self, user_sim_params: dict) -> None:
        self._update_params(self.simulation_params, user_sim_params)

    def set_model_params(self, user_model_params: dict) -> None:
        self._update_params(self.model_params, user_model_params)

    def set_slider_params(self, user_slider_params: dict) -> None:
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
        self._configure_plot()
        fig, axes = subplots(2, 1, figsize=[9.5, 7], sharex=True)
        ax1, ax2 = axes
        fig.canvas.manager.set_window_title('dSpike Playground')
        fig.subplots_adjust(top=0.95, bottom=0.07, left=0.09, right=0.62, hspace=0.15, wspace=0.2)
        ax1.set_ylabel('Voltage (mV)')
        ax2.set_ylabel('Conductance (nS)')
        ax2.set_xlabel('Time (ms)')
        ax1.grid(True)
        ax2.grid(True)
        ax1.set_title('Membrane response', fontsize=11, fontweight='bold', loc='left')
        ax2.set_title('dSpike channels', fontsize=11, fontweight='bold', loc='left')
        fig.text(0.66, 0.962, "Parameters", fontsize=11, fontweight='bold')
        fig.text(0.66, 0.25, "Membrane properties", fontsize=11, fontweight='bold')

        sliders = self._create_sliders(fig)
        reset_button = self._create_reset_button(fig)
        text_boxes = self._create_text_boxes(fig)

        return fig, ax1, ax2, sliders, reset_button, text_boxes

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
        return [
            Slider(
                fig.add_axes([0.8, 0.9 - i * 0.05, 0.15, 0.025]),
                f'{label} ({unit})  ', valmin, valmax,
                valinit=valinit, valstep=valstep, track_color='0.92'
            )
            for i, (label, (valmin, valmax, valinit, valstep, unit)) in enumerate(self.slider_params.items())
        ]

    def _create_reset_button(self, fig):
        ax_reset = fig.add_axes([0.8, 0.45, 0.15, 0.025])
        return Button(ax_reset, 'Reset', color='0.92', hovercolor='0.95')

    def _create_text_boxes(self, fig):
        text_boxes = {
            'C (pF)  ': (self.model_params["C"] / pF),
            'gL (nS)  ': (self.model_params["gL"] / nS),
            'EL (mV)  ': (self.model_params["EL"] / mV)
        }
        text_box_axes = [fig.add_axes([0.8, 0.17 - i * 0.05, 0.15, 0.03]) for i in range(len(text_boxes))]
        return [
            TextBox(ax, label, initial=f'{value:.1f}', textalignment='center')
            for ax, (label, value) in zip(text_box_axes, text_boxes.items())
        ]

    def _reset(self, sliders, text_boxes):
        for slider in sliders:
            slider.reset()
        for text_box in text_boxes:
            text_box.set_val(str(text_box.initial))
        
    def _update(self, val, net, neuron, M, sliders, ax1, ax2, line1, line2, line3):
        start_time = time.time()
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
        self._update_plot(M, ax1, ax2, line1, line2, line3)
        print(f"Update time: {time.time() - start_time:.2f} s")

    def _update_model_params(self, expr, net, neuron, M, text_boxes, ax1, ax2, line1, line2, line3):
        start_time = time.time()
        net.restore()
        neuron.namespace.update({
            'C': float(text_boxes[0].text) * pF,
            'gL': float(text_boxes[1].text) * nS,
            'EL': float(text_boxes[2].text) * mV
        })
        self._run_simulation(net, neuron, self.slider_params['current'][2] * pA)
        self._update_plot(M, ax1, ax2, line1, line2, line3)
        print(f"Update time: {time.time() - start_time:.2f} s")

    def _update_plot(self, M, ax1, ax2, line1, line2, line3):
        line1.set_ydata(M.V[0] / mV)
        line2.set_ydata(M.g_pos[0] / nS)
        line3.set_ydata(-M.g_neg[0] / nS)
        ax1.set_ylim(top=max(M.V[0] / mV) + 2, bottom=min(M.V[0] / mV) - 2)
        ax2.set_ylim(top=max(M.g_pos[0] / nS) + 2, bottom=min(-M.g_neg[0] / nS) - 2)
        draw()

    def _initial_slider_values(self):
        return {key: params[2] * params[-1] for key, params in self.slider_params.items()}

if __name__ == "__main__":
    test = Playground()
    test.start()
