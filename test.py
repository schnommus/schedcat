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
    oh.ctx_switch = const(3000*SCALE)
    oh.schedule = const(5500*SCALE)
    oh.release = const(12000*SCALE)
    oh.ipi_latency = const(10000*SCALE)
    oh.release_latency = const(10000*SCALE)
    return oh

def get_oh_us():
    oh = Overheads()
    oh.ctx_switch = const(2800*SCALE)
    oh.schedule = const(3275*SCALE)
    oh.release = const(8829*SCALE)
    oh.ipi_latency = const(2372*SCALE)
    oh.release_latency = const(5000*SCALE)
    return oh

n_tasks = 10
n_cpus = 4
dedicated_irq = True
utilisation_inc = 0.05
tests_per_utilisation = 100

all_overheads = {
        'LITMUS (4-GEDF)': get_oh_litmus(),
        'Us (4-GEDF)': get_oh_us(),
        'Ideal (4-GEDF)': get_oh_ideal(),
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

    ax.plot(np.arange(0.0, n_cpus, utilisation_inc), all_tests, label=oh)

ax.grid()
ax.set(xlabel='Utilisation Cap', ylabel='% of task sets schedulable',
       title='G-EDF Schedulable Task Sets [ncpus={}]'.format(n_cpus))
ax.legend()
plt.show()

