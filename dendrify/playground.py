from brian2 import Network, NeuronGroup, StateMonitor
from brian2.units import ms, mV, mvolt, nS, pA, pF
from matplotlib.pyplot import rcParams, show, subplots
from matplotlib.widgets import Button, Slider


class Playground:
    SIMULATION_PARAMS = {
        'current': 120*pA,
        'idle_duration': 5*ms,
        'stim_duration': 100*ms,
        'post_stim_duration': 50*ms
    }
    
    MODEL_PARAMS = {
        'Vth_pos': -40. * mvolt,
        'g_pos_max': 20. * nS,
        'g_neg_max': 20. * nS,
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
    
    EQUATIONS = """
        dV/dt = (gL * (EL-V) + I) / C  :volt
        I = I_ext + I_pos + I_neg  :amp
        I_ext  :amp
        I_pos = g_pos * (E_pos-V)  :amp
        I_neg = g_neg * (E_neg-V)  :amp
        g_pos = g_pos_max * int(t <= spiketime + duration_pos) * check :siemens
        g_neg = g_neg_max * int(t <= spiketime + offset_neg + duration_neg) * int(t >= spiketime + offset_neg) * check   :siemens
        spiketime  :second
        check :1
    """
    
    EVENT = {'dspike': 'V >= Vth_pos and t >= spiketime + refractory_pos * check'}

    def __init__(self, **kwargs):
        # Separate keyword arguments for each dictionary
        simulation_params_user = kwargs.get("simulation_params", {})
        model_params_user = kwargs.get("model_params", {})

        # Create instance attributes by merging class defaults with provided updates
        self.simulation_params = {**self.SIMULATION_PARAMS, **simulation_params_user}
        self.model_params = {**self.MODEL_PARAMS, **model_params_user}

    def create_brian_objects(self):
        neuron = NeuronGroup(1, model=self.EQUATIONS, method='euler',
                             events=self.EVENT, namespace=self.model_params)
        neuron.run_on_event('dspike', 'spiketime = t; check = 1')
        neuron.V = self.model_params['EL']
        neuron.check = 0
        M = StateMonitor(neuron, ['V', 'g_pos', 'g_neg'], record=True)
        net = Network(neuron, M)
        net.store()
        return neuron, M, net
    
    def run_simulation(self, net, neuron, current):
        net.run(self.simulation_params['idle_duration'])
        neuron.I_ext = current
        net.run(self.simulation_params['stim_duration'])
        neuron.I_ext = 0*pA
        net.run(self.simulation_params['post_stim_duration'])

    def setup_plot(self):
        rcParams.update({
            "font.family": "Arial",
            "legend.fontsize": 10,
            "legend.edgecolor": 'none',
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "xtick.color": 'none',
            "xtick.labelcolor": 'black',
            "xtick.labelsize": 10,
            "ytick.color": 'none',
            "ytick.labelcolor": 'black',
            "ytick.labelsize": 10,
            'grid.linestyle': ":",
            'grid.color': "#d3d3d3"
        })

        fig, axes = subplots(2, 1, figsize=[9.5, 7], sharex=True)
        ax1, ax2 = axes
        fig.canvas.manager.set_window_title('dSpike Playground')
        fig.subplots_adjust(top=0.95, bottom=0.07, left=0.09, right=0.65, hspace=0.12, wspace=0.2)
        ax1.set_ylabel('Voltage (mV)')
        ax2.set_ylabel('Conductance (nS)')
        ax2.set_xlabel('Time (ms)')
        ax1.grid(True)
        ax2.grid(True)
        ax1.set_title('Membrane', fontsize=11, fontweight='bold', loc='left')
        ax2.set_title('dSpike channels', fontsize=11, fontweight='bold', loc='left')
        fig.text(0.66, 0.962, "Parameters", fontsize=11, fontweight='bold')

        slider_params = [
            ('input current (pA)', 0, 200, 120, 10),
            ('threshold (mV)', -50, 0, -40, 1.0),
            ('g_rise (nS)', 0, 40, 20, 0.5),
            ('g_fall (nS)', 0, 40, 20, 0.5),
            ('duration_rise (ms)', 0, 50, 2, 0.5),
            ('duration_fall (ms)', 0, 50, 3, 0.5),
            ('offset_fall (ms)', 0, 55, 1, 0.5),
            ('refractory (ms)', 0, 100, 5, 0.5),
            ('reversal_rise (mV)', 70, 136, 70, (70, 136))
        ]

        sliders = []
        for i, (label, valmin, valmax, valinit, valstep) in enumerate(slider_params):
            ax = fig.add_axes([0.8, 0.9 - i * 0.05, 0.15, 0.025])
            slider = Slider(ax, label, valmin, valmax, valinit=valinit, valstep=valstep, track_color='0.9')
            sliders.append(slider)

        ax_reset = fig.add_axes([0.8, 0.45, 0.15, 0.025])
        reset_button = Button(ax_reset, 'Reset', color='0.9', hovercolor='0.8')

        return fig, ax1, ax2, sliders, reset_button



    def main(self):

        def reset(event):
            for slider in sliders:
                slider.reset()
    
        def update(val):
            net.restore()
            neuron.namespace.update({
                'Vth_pos': sliders[1].val * mV,
                'g_pos_max': sliders[2].val * nS,
                'g_neg_max': sliders[3].val * nS,
                'duration_pos': sliders[4].val * ms,
                'duration_neg': sliders[5].val * ms,
                'offset_neg': sliders[6].val * ms,
                'refractory_pos': sliders[7].val * ms,
                'E_pos': sliders[8].val * mV})
            self.run_simulation(net, neuron, sliders[0].val*pA)
            line1.set_ydata(M.V[0]/mV)
            line2.set_ydata(M.g_pos[0]/nS)
            line3.set_ydata(-M.g_neg[0]/nS)
            ax1.set_ylim(top=max(M.V[0]/mV)+2, bottom=min(M.V[0]/mV)-2)
            ax2.set_ylim(top=max(M.g_pos[0]/nS)+2, bottom=min(-M.g_neg[0]/nS)-2)
        
        neuron, M, net = self.create_brian_objects()
        fig, ax1, ax2, sliders, reset_button = self.setup_plot()
        self.run_simulation(net, neuron, self.SIMULATION_PARAMS['current'])
        line1, = ax1.plot(M.t/ms, M.V[0]/mV)
        line2, = ax2.plot(M.t/ms, M.g_pos[0]/nS, label='g_rise', c='black')
        line3, = ax2.plot(M.t/ms, -M.g_neg[0]/nS, label='-g_fall', c='gray')
        ax2.legend()

        for slider in sliders:
            slider.on_changed(update)
        reset_button.on_clicked(reset)
        show()




test = Playground()
test.main()
