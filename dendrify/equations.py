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

    # Condactance-based integrate and fire with adaptation:
    'cadIF': ('dV{0}/dt =  (gL{0}*(EL{0}-V{0}) + I{0} - w{0}) / C{0} :volt \n'
              'w{0} = gA * (V{0}-EA) :amp \n'
              'dgA/dt = (gAmax * (abs(V{0}-EA)) / mV - gA) / tauA :siemens \n'
              'I{0} = I_ext{0}  :amp \n'
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
    'NMDA': ('I_NMDA_{1}_{0} = g_NMDA_{1}_{0} * (E_NMDA-V_{0}) * s_NMDA_{1}_{0} / (1 + Mg_con * exp(-Alpha_NMDA*(V_{0}/mV+Gamma_NMDA)) / Beta_NMDA) * w_NMDA_{1}_{0}  :amp\n'
             'ds_NMDA_{1}_{0}/dt = -s_NMDA_{1}_{0}/t_NMDA_decay_{1}_{0}  :1'),

    # NMDA equations with rise and decay kinetics:
    'NMDA_rd': ('I_NMDA_{1}_{0} = g_NMDA_{1}_{0} * (E_NMDA-V_{0}) * x_NMDA_{1}_{0} / (1 + Mg_con * exp(-Alpha_NMDA*(V_{0}/mV+Gamma_NMDA)) / Beta_NMDA) * w_NMDA_{1}_{0}  :amp\n'
                'dx_NMDA_{1}_{0}/dt = (-x_NMDA_{1}_{0}/t_NMDA_decay_{1}_{0}) + s_NMDA_{1}_{0}/ms  :1\n'
                'ds_NMDA_{1}_{0}/dt = -s_NMDA_{1}_{0} / t_NMDA_rise_{1}_{0}  :1'),

    # Random white noise equations:
    'noise': 'dI_noise_{0}/dt = (mean_noise_{0}-I_noise_{0}) / tau_noise_{0} + sigma_noise_{0} * (sqrt(2/(tau_noise_{0}*dt)) * randn()) :amp'
}

library_point = {
    # Adaptive exponential integrate & fire:
    'adex': ('dV/dt = (gL * (EL-V) + gL*DeltaT*exp((V-Vth)/DeltaT) + I - w) / C  :volt\n'
             'dw/dt = (a * (V-EL) -w) / tauw  :amp\n'
             'I = I_ext  :amp\n'
             'I_ext  :amp'),

    # Leaky integrate and fire with adaptation:
    'adaptiveIF': ('dV/dt = (gL * (EL-V) + I - w) / C  :volt\n'
                   'dw/dt = (a * (V-EL) - w) / tauw  :amp\n'
                   'I = I_ext  :amp\n'
                   'I_ext  :amp'),

    # Condactance-based integrate and fire with adaptation:
    'cadIF': ('dV/dt =  (gL*(EL-V) + I - w) / C :volt \n'
              'w = gA * (V-EA) :amp \n'
              'dgA/dt = (gAmax * (abs(V-EA)) / mV - gA) / tauA :siemens \n'
              'I = I_ext  :amp \n'
              'I_ext  :amp'),

    # Leaky integrate and fire:
    'leakyIF': ('dV/dt = (gL * (EL-V) + I) / C  :volt\n'
                'I = I_ext  :amp\n'
                'I_ext  :amp'),

    # Leaky membrane:
    'passive': ('dV/dt = (gL * (EL-V) + I) / C  :volt\n'
                'I = I_ext  :amp\n'
                'I_ext  :amp'),

    # AMPA equations with instant rise (only decay kinetics):
    'AMPA': ('I_AMPA_{0} = g_AMPA_{0} * (E_AMPA-V) * s_AMPA_{0} * w_AMPA_{0}  :amp\n'
             'ds_AMPA_{0}/dt = -s_AMPA_{0} / t_AMPA_decay_{0}  :1'),

    # AMPA equations with rise and decay kinetics:
    'AMPA_rd': ('I_AMPA_{0} = g_AMPA_{0} * (E_AMPA-V) * x_AMPA_{0} * w_AMPA_{0}  :amp\n'
                'dx_AMPA_{0}/dt = (-x_AMPA_{0}/t_AMPA_decay_{0}) + s_AMPA_{0}/ms  :1\n'
                'ds_AMPA_{0}/dt = -s_AMPA_{0} / t_AMPA_rise_{0}  :1'),

    # GABA equations with instant rise (only decay kinetics):
    'GABA': ('I_GABA_{0} = g_GABA_{0} * (E_GABA-V) * s_GABA_{0} * w_GABA_{0}  :amp\n'
             'ds_GABA_{0}/dt = -s_GABA_{0} / t_GABA_decay_{0}  :1'),

    # GABA equations with rise and decay kinetics:
    'GABA_rd': ('I_GABA_{0} = g_GABA_{0} * (E_GABA-V) * x_GABA_{0} * w_GABA_{0}  :amp\n'
                'dx_GABA_{0}/dt = (-x_GABA_{0}/t_GABA_decay_{0}) + s_GABA_{0}/ms  :1\n'
                'ds_GABA_{0}/dt = -s_GABA_{0} / t_GABA_rise_{0}  :1'),

    # NMDA equations with rise and decay kinetics:
    'NMDA': ('I_NMDA_{0} = g_NMDA_{0} * (E_NMDA-V) * s_NMDA_{0} / (1 + Mg_con * exp(-Alpha_NMDA*(V/mV+Gamma_NMDA)) / Beta_NMDA) * w_NMDA_{0}  :amp\n'
             'ds_NMDA_{0}/dt = -s_NMDA_{0}/t_NMDA_decay_{0}  :1'),

    # NMDA equations with rise and decay kinetics:
    'NMDA_rd': ('I_NMDA_{0} = g_NMDA_{0} * (E_NMDA-V) * x_NMDA_{0} / (1 + Mg_con * exp(-Alpha_NMDA*(V/mV+Gamma_NMDA)) / Beta_NMDA) * w_NMDA_{0}  :amp\n'
                'dx_NMDA_{0}/dt = (-x_NMDA_{0}/t_NMDA_decay_{0}) + s_NMDA_{0}/ms  :1\n'
                'ds_NMDA_{0}/dt = -s_NMDA_{0} / t_NMDA_rise_{0}  :1'),

    # Random white noise equations:
    'noise': 'dI_noise/dt = (mean_noise-I_noise) / tau_noise + sigma_noise * (sqrt(2/(tau_noise*dt)) * randn()) :amp'
}
