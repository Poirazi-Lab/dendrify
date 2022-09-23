# A dictionary that contains templates of frequently used models or strings

library = {
    # Adaptive exponential integrate & fire:
    'adex': ('dV{0}/dt = (gL{0} * (EL{0}-V{0}) + gL{0}*DeltaT{0}*exp((V{0}-Vth{0})/DeltaT{0}) + I{0} - w{0}) / C{0}  :volt\n'
             'dw{0}/dt = (a{0} * (V{0}-EL{0}) -w{0}) / tauw{0}  :amp\n'
             'I{0} = I_ext{0}  :amp\n'
             'I_ext{0}  :amp'),

    # Leaky integrate and fire with adaptation:
    'adaptiveIF': ('dV{0}/dt = (gL{0} * (EL{0}-V{0}) + I{0} - w{0}) / C{0}  :volt\n'
                   'dw{0}/dt = (a{0} * (V{0}-EL{0}) - w{0}) / tauw{0}  :amp\n'
                   'I{0} = I_ext{0}  :amp\n'
                   'I_ext{0}  :amp'),

    # Leaky integrate and fire:
    'leakyIF': ('dV{0}/dt = (gL{0} * (EL{0}-V{0}) + I{0}) / C{0}  :volt\n'
                'I{0} = I_ext{0}  :amp\n'
                'I_ext{0}  :amp'),

    # Leaky membrane:
    'passive': ('dV{0}/dt = (gL{0} * (EL{0}-V{0}) + I{0}) / C{0}  :volt\n'
                'I{0} = I_ext{0}  :amp\n'
                'I_ext{0}  :amp'),

    # AMPA equations with instant rise (only decay kinetics):
    'AMPA': ('I_AMPA_{1}_{0} = g_AMPA_{1}_{0} * (E_AMPA-V_{0}) * s_AMPA_{1}_{0} * w_AMPA_{1}_{0}  :amp\n'
             'ds_AMPA_{1}_{0}/dt = -s_AMPA_{1}_{0} / t_AMPA_decay_{1}_{0}  :1'),

    # AMPA equations with rise and decay kinetics:
    'AMPA_rd': ('I_AMPA_{1}_{0} = g_AMPA_{1}_{0} * (E_AMPA-V_{0}) * x_AMPA_{1}_{0} * w_AMPA_{1}_{0}  :amp\n'
                'dx_AMPA_{1}_{0}/dt = (-x_AMPA_{1}_{0}/t_AMPA_decay_{1}_{0}) + s_AMPA_{1}_{0}/ms  :1\n'
                'ds_AMPA_{1}_{0}/dt = -s_AMPA_{1}_{0} / t_AMPA_rise_{1}_{0}  :1'),

    # GABA equations with instant rise (only decay kinetics):
    'GABA': ('I_GABA_{1}_{0} = g_GABA_{1}_{0} * (E_GABA-V_{0}) * s_GABA_{1}_{0} * w_GABA_{1}_{0}  :amp\n'
             'ds_GABA_{1}_{0}/dt = -s_GABA_{1}_{0} / t_GABA_decay_{1}_{0}  :1'),

    # GABA equations with rise and decay kinetics:
    'GABA_rd': ('I_GABA_{1}_{0} = g_GABA_{1}_{0} * (E_GABA-V_{0}) * x_GABA_{1}_{0} * w_GABA_{1}_{0}  :amp\n'
                'dx_GABA_{1}_{0}/dt = (-x_GABA_{1}_{0}/t_GABA_decay_{1}_{0}) + s_GABA_{1}_{0}/ms  :1\n'
                'ds_GABA_{1}_{0}/dt = -s_GABA_{1}_{0} / t_GABA_rise_{1}_{0}  :1'),

    # NMDA equations with rise and decay kinetics:
    'NMDA': ('I_NMDA_{1}_{0} = g_NMDA_{1}_{0} * (E_NMDA-V_{0}) * s_NMDA_{1}_{0} / (1 + Mg * exp(-alpha*(V_{0}/mV+gamma)) / beta) * w_NMDA_{1}_{0}  :amp\n'
             'ds_NMDA_{1}_{0}/dt = -s_NMDA_{1}_{0}/t_NMDA_decay_{1}_{0}  :1'),

    # NMDA equations with rise and decay kinetics:
    'NMDA_rd': ('I_NMDA_{1}_{0} = g_NMDA_{1}_{0} * (E_NMDA-V_{0}) * x_NMDA_{1}_{0} / (1 + Mg * exp(-alpha*(V_{0}/mV+gamma)) / beta) * w_NMDA_{1}_{0}  :amp\n'
                'dx_NMDA_{1}_{0}/dt = (-x_NMDA_{1}_{0}/t_NMDA_decay_{1}_{0}) + s_NMDA_{1}_{0}/ms  :1\n'
                'ds_NMDA_{1}_{0}/dt = -s_NMDA_{1}_{0} / t_NMDA_rise_{1}_{0}  :1'),

    # Random white noise equations:
    'noise': 'dI_noise_{0}/dt = (mean_noise_{0}-I_noise_{0}) / tau_noise_{0} + sigma_noise_{0} * (sqrt(2/(tau_noise_{0}*dt)) * randn()) :amp',

    'condition_I_Na': 'V_{0} > Vth_Na_{0} and allow_I_Na_{0} and t > timer_Na_{0} + refractory_Na',

    'condition_I_Kn': 't > (timer_Na_{0} + offset_Kn) and allow_I_Kn_{0}',

    'condition_I_Ca': 'V_{0} > Vth_Ca_{0} and allow_I_Ca_{0} and t > timer_Ca_{0} + refractory_Ca',

    'condition_I_Kc': 't > (timer_Ca_{0} + offset_Kc) and allow_I_Kc_{0}',

    'run_on_Na_spike': ("run_on_event('activate_I_Na_{0}', 'g_Na_{0} += g_Na_{0}_max; allow_I_Na_{0}=False; allow_I_Kn_{0}=True; timer_Na_{0} = t') \n"
                        "run_on_event('activate_I_Kn_{0}', 'g_Kn_{0} += g_Kn_{0}_max; allow_I_Kn_{0}=False; allow_I_Na_{0}=True')"),

    'run_on_Ca_spike': ("run_on_event('activate_I_Ca_{0}', 'g_Ca_{0} += g_Ca_{0}_max; allow_I_Ca_{0}=False; allow_I_Kc_{0}=True; timer_Ca_{0} = t') \n"
                        "run_on_event('activate_I_Kc_{0}', 'g_Kc_{0} += g_Kc_{0}_max; allow_I_Kc_{0}=False; allow_I_Ca_{0}=True')")
}
