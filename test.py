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

def get_overheads(n):
    oh = Overheads()
    oh.ctx_switch = const(n)
    return oh

n_tasks = 10
n_cpus = 2
dedicated_irq = True
utilisation_inc = 0.05
tests_per_utilisation = 10

all_overheads = {
        'ctx_switch=0': get_overheads(0),
        'ctx_switch=100': get_overheads(1000),
        }

fig, ax = plt.subplots()

for oh in all_overheads.keys():

    all_tests = [0.0 for _ in range(int(n_cpus / utilisation_inc))]
    gen_utilisation = 0.001
    for n, _ in enumerate(all_tests):

        for _ in range(tests_per_utilisation):

            ts = generator.gen_taskset('uni-moderate', 'unif', n_tasks, gen_utilisation)
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

