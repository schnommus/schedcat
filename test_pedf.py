#!/bin/python2

import schedcat.generator.generator_emstada as generator
from schedcat.overheads.model import Overheads, CacheDelay
from schedcat.overheads.jlfp import charge_scheduling_overheads, \
                                    quantize_params
import schedcat.sched.edf as edf
from schedcat.util.math import const

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Linux Libertine']

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Cycles to microseconds
SCALE = 30 * (1 / (3e9 * 1e-6))

def get_oh_ideal():
    oh = Overheads()
    oh.ctx_switch = const(0)
    return oh

def get_oh_litmus():
    oh = Overheads()
    oh.ctx_switch = const(2500*SCALE)
    oh.schedule = const(4000*SCALE)
    oh.release = const(3500*SCALE)
    oh.release_latency = const(37000*SCALE)
    return oh

def get_oh_us():
    oh = Overheads()
    oh.ctx_switch = const(5000*SCALE)
    oh.schedule = const(1700*SCALE)
    oh.release = const(2000*SCALE)
    oh.release_latency = const(17000*SCALE)
    return oh

n_tasks = 10
n_cpus = 1
dedicated_irq = True
utilisation_inc = 0.005
tests_per_utilisation = 400

all_overheads = {
        'Ideal (4-PEDF)': get_oh_ideal(),
        'LITMUS (4-PEDF)': get_oh_litmus(),
        'Our approach (4-PEDF)': get_oh_us(),
        }

fig, ax = plt.subplots()

for oh in all_overheads.keys():

    all_tests = [0.0 for _ in range(int(n_cpus / utilisation_inc))]
    gen_utilisation = 0.001
    for n, _ in enumerate(all_tests):

        for _ in range(tests_per_utilisation):

            ts = generator.gen_taskset('uni-short', 'unif', n_tasks, gen_utilisation)
            for t in ts:
                t.wss = 0

            success = charge_scheduling_overheads(all_overheads[oh], n_cpus, dedicated_irq, ts)
            if not success:
                continue

            quantize_params(ts)

            set_schedulable = edf.is_schedulable(n_cpus, ts)

            if set_schedulable:
                all_tests[n] += 100.0 / tests_per_utilisation

        print all_tests[n]

        gen_utilisation += utilisation_inc

    ax.plot(np.arange(0.0, n_cpus, utilisation_inc), all_tests, label=oh, linewidth=4)

ax.grid()
ax.set(xlabel='Utilisation Cap (per core)', ylabel='% of task sets schedulable')
ax.legend()

plt.tight_layout()
fig.savefig('cdf_out.png', dpi=200) 
plt.show()
