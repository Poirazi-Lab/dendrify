from brian2 import Network, NeuronGroup, StateMonitor
from brian2.units import ms, mV, mvolt, nS, pA, pF
from matplotlib.pyplot import rcParams, show, subplots
from matplotlib.widgets import Button, Slider


def main(
        idle_duration=5,
        stim_duration=100,
        post_stim_duration=50,
        neuron_params={},
        dspike_params={}
        ):
    # from brian2 import Network, NeuronGroup, StateMonitor
    # from brian2.units import ms, mV, mvolt, nS, pA, pF
    # from matplotlib.pyplot import rcParams, show, subplots
    # from matplotlib.widgets import Button, Slider

    def run_simulation(current):
        net.run(idle_duration*ms)
        neuron.I_ext = current*pA
        net.run(stim_duration*ms)
        neuron.I_ext = 0*pA
        net.run(post_stim_duration*ms)

    def update(val):
        net.restore()
        neuron.namespace.update({
            'Vth_pos': vth_slider.val * mV,
            'g_pos_max': g_pos_slider.val * nS,
            'g_neg_max': g_neg_slider.val * nS,
            'duration_pos': pos_dur_slider.val * ms,
            'duration_neg': neg_dur_slider.val * ms,
            'offset_neg': neg_offset_slider.val * ms,
            'refractory_pos': refractory_slider.val * ms,
            'E_pos': ion_slider.val * mV})
        run_simulation(current_slider.val)
        line1.set_ydata(M.V[0]/mV)
        line2.set_ydata(M.g_pos[0]/nS)
        line3.set_ydata(-M.g_neg[0]/nS)
        ax1.set_ylim(top=max(M.V[0]/mV)+2, bottom=min(M.V[0]/mV)-2)
        ax2.set_ylim(top=max(M.g_pos[0]/nS)+2, bottom=min(-M.g_neg[0]/nS)-2)

    def reset(event):
        current_slider.reset()
        vth_slider.reset()
        g_pos_slider.reset()
        g_neg_slider.reset()
        pos_dur_slider.reset()
        neg_dur_slider.reset()
        neg_offset_slider.reset()
        refractory_slider.reset()
        ion_slider.reset()

    rcParams.update({
        "font.family": "Arial",
        "legend.fontsize": 10,
        "legend.edgecolor": 'none',
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "xtick.color": 'none',
        "xtick.labelcolor": 'black',
        "xtick.labelsize": 10,
        "ytick.color": 'none',
        "ytick.labelcolor": 'black',
        "ytick.labelsize": 10,
        'grid.linestyle': ":",
        'grid.color': "#d3d3d3"})

    eqs = """
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

    default_params = {
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
        'duration_neg': 3. * ms}

    event = {'dspike': 'V >= Vth_pos and t >= spiketime + refractory_pos * check'}


    # Create neurongroup and run first simulation
    neuron = NeuronGroup(1, model=eqs, method='euler', events=event, namespace=default_params)
    neuron.run_on_event('dspike', 'spiketime = t; check = 1')
    neuron.V = default_params['EL']
    neuron.check = 0
    vars_to_record = ['V', 'g_pos', 'g_neg']
    M = StateMonitor(neuron, vars_to_record, record=True)
    net = Network(neuron, M)
    net.store()
    run_simulation(120)

    # Plotting setup
    fig, axes = subplots(2, 1, figsize=[9.5, 7], sharex=True)
    fig.canvas.manager.set_window_title('dSpike Playground')
    fig.subplots_adjust(top=0.95, bottom=0.07, left=0.09, right=0.65, hspace=0.12, wspace=0.2)

    slider_height = 0.025
    ax_current = fig.add_axes([0.8, 0.9, 0.15, slider_height])
    ax_vth = fig.add_axes([0.8, 0.85, 0.15, slider_height])
    ax_g_pos = fig.add_axes([0.8, 0.8, 0.15, slider_height])
    ax_g_neg = fig.add_axes([0.8, 0.75, 0.15, slider_height])
    ax_pos_dur = fig.add_axes([0.8, 0.7, 0.15, slider_height])
    ax_neg_dur = fig.add_axes([0.8, 0.65, 0.15, slider_height])
    ax_neg_offset = fig.add_axes([0.8, 0.6, 0.15, slider_height])
    ax_refractory = fig.add_axes([0.8, 0.55, 0.15, slider_height])
    ax_reversal = fig.add_axes([0.8, 0.50, 0.15, slider_height])
    ax_reset = fig.add_axes([0.8, 0.45, 0.15, slider_height])

    ax1, ax2 = axes
    line1, = ax1.plot(M.t/ms, M.V[0]/mV)
    line2, = ax2.plot(M.t/ms, M.g_pos[0]/nS, label='g_rise', c='black')
    line3, = ax2.plot(M.t/ms, -M.g_neg[0]/nS, label='-g_fall', c='gray')
    ax1.set_ylabel('Voltage (mV)')
    ax2.set_ylabel('Conductance (nS)')
    ax2.set_xlabel('Time (ms)')
    ax2.legend()
    ax1.grid(True)
    ax2.grid(True)
    ax1.set_title('Membrane', fontsize=11, fontweight='bold', loc='left')
    ax2.set_title('dSpike channels', fontsize=11, fontweight='bold', loc='left')
    fig.text(0.66, 0.962, "Parameters", fontsize=11, fontweight='bold')


    # Create sliders and buttons
    current_slider = Slider(ax_current, 'input current (pA) ', 0, 200, valinit=120, valstep=10, track_color='0.9')
    vth_slider = Slider(ax_vth, 'threshold (mV) ', -50, 0, valinit=-40, valstep=1.0, track_color='0.9')
    g_pos_slider = Slider(ax_g_pos, 'g_rise (nS) ', 0, 40, valinit=20, valstep=0.5, track_color='0.9')
    g_neg_slider = Slider(ax_g_neg, 'g_fall (nS) ', 0, 40, valinit=20, valstep=0.5, track_color='0.9')
    pos_dur_slider = Slider(ax_pos_dur, 'duration_rise (ms) ', 0, 50, valinit=2, valstep=0.5, track_color='0.9')
    neg_dur_slider = Slider(ax_neg_dur, 'duration_fall (ms) ', 0, 50, valinit=3, valstep=0.5, track_color='0.9')
    neg_offset_slider = Slider(ax_neg_offset, 'offset_fall (ms) ', 0, 55, valinit=1, valstep=0.5, track_color='0.9')
    refractory_slider = Slider(ax_refractory, 'refractory (ms) ', 0, 100, valinit=5, valstep=0.5, track_color='0.9')
    ion_slider = Slider(ax_reversal, 'reversal_rise (mV) ', 70, 136, valinit=70, valstep=(70, 136), track_color='0.9')
    reset_button = Button(ax_reset, 'Reset', color='0.9', hovercolor='0.8')

    # Connect sliders to update function
    sliders = [current_slider, vth_slider, g_pos_slider, g_neg_slider,
            pos_dur_slider, neg_dur_slider, neg_offset_slider,
            refractory_slider, ion_slider]
    for slider in sliders:
        slider.on_changed(update)
    reset_button.on_clicked(reset)

    show()

main(stim_duration=100)
