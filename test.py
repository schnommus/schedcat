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

import collections

Measurement = collections.namedtuple('Measurement', ['mean', 'stddev', 'worst'])

# Cycles to microseconds
SCALE = 3 * (1 / (3e9 * 1e-6))

all_rasp_gedf = collections.OrderedDict([('CXS', Measurement(mean=854.7309874523942, stddev=0.0, worst=4832.4740200780925)), ('SCHED', Measurement(mean=1508.9943455863336, stddev=0.0, worst=29995.70076006712)), ('RELEASE', Measurement(mean=32386.57546289018, stddev=0.0, worst=48793.80652778625)), ('RELEASE\nLATENCY', Measurement(mean=479075, stddev=0.0, worst=2000000)), ('SEND\nRESCHED', Measurement(mean=248618.86333812933, stddev=0.0, worst=561791.4676129273))])

all_litmus_gedf = collections.OrderedDict([('CXS', Measurement(mean=3026.752625, stddev=1770.8703025, worst=8586.5)), ('SCHED', Measurement(mean=5376.7659475, stddev=2219.1700725, worst=15581.0)), ('RELEASE', Measurement(mean=11324.346925, stddev=8295.9173625, worst=29242.0)), ('RELEASE\nLATENCY', Measurement(mean=40977.097499999996, stddev=34981.053, worst=105081.25)), ('SEND\nRESCHED', Measurement(mean=9261.9990225, stddev=9118.231565, worst=91255.0))])

all_litmus_pedf = collections.OrderedDict([('CXS', Measurement(mean=2641.5759275, stddev=1494.4631675, worst=6683.5)), ('SCHED', Measurement(mean=3927.9633625, stddev=1429.9445500000002, worst=8029.0)), ('RELEASE', Measurement(mean=3384.8741449999998, stddev=2179.0025625, worst=12344.5)), ('RELEASE\nLATENCY', Measurement(mean=36180.4455, stddev=28935.113499999996, worst=121135.2))])

all_us_gedf = collections.OrderedDict([('CXS', Measurement(mean=8829.648745519713, stddev=1598.8343800494706, worst=10508)), ('SCHED', Measurement(mean=6075.776550203673, stddev=2334.04179791727, worst=7729)), ('RELEASE', Measurement(mean=173.19600725952813, stddev=38.979235740375394, worst=429)), ('RELEASE\nLATENCY', Measurement(mean=15472.463768115942, stddev=2232.124963471352, worst=20400.0)), ('SEND\nRESCHED', Measurement(mean=2372.8, stddev=158.02328942279362, worst=2537))])

all_us_pedf = collections.OrderedDict([('CXS', Measurement(mean=5103.0344827586205, stddev=410.62846113105485, worst=10716)), ('SCHED', Measurement(mean=4409.361695585329, stddev=2207.929010693271, worst=7133)), ('RELEASE', Measurement(mean=173.19600725952813, stddev=38.979235740375394, worst=429)), ('RELEASE\nLATENCY', Measurement(mean=15472.463768115942, stddev=2232.124963471352, worst=20400.0))])

def get_oh_ideal():
    oh = Overheads()
    oh.ctx_switch = const(0)
    return oh

oh_map = {
            'CXS': 'ctxt_switch',
            'RELEASE': 'release',
            'SEND\nRESCHED': 'ipi_latency',
            'RELEASE\nLATENCY': 'release_latency',
            'SCHED': 'schedule',
    }

def get_mean_oh_from_dict(d):
    oh = Overheads()
    for e in d.keys():
        setattr(oh, oh_map[e], const(d[e].mean * SCALE))
    return oh

def get_worst_oh_from_dict(d):
    oh = Overheads()
    for e in d.keys():
        setattr(oh, oh_map[e], const(d[e].worst * SCALE))
    return oh

n_tasks = 10
dedicated_irq = True
utilisation_inc = 0.02
tests_per_utilisation = 300

# n_cpus = 4
#   all_overheads = {
#           'Ideal (4-GEDF)': get_oh_ideal(),
#           'LITMUS (4-GEDF)': get_worst_oh_from_dict(all_litmus_gedf),
#           'RASP (4-GEDF)': get_worst_oh_from_dict(all_rasp_gedf),
#           'Our approach (4-GEDF)': get_worst_oh_from_dict(all_us_gedf),
#           }

n_cpus = 1
all_overheads = {
          'Ideal (4-PEDF)': get_oh_ideal(),
          'LITMUS (4-PEDF)': get_mean_oh_from_dict(all_litmus_pedf),
          'Our approach (4-PEDF)': get_mean_oh_from_dict(all_us_pedf),
          }

fig, ax = plt.subplots()

for oh in all_overheads.keys():

    all_tests = [0.0 for _ in range(int(n_cpus / utilisation_inc))]
    gen_utilisation = 0.01
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

    ax.plot(np.arange(0.0, n_cpus, utilisation_inc), all_tests, label=oh, linewidth=3)

ax.grid()
ax.set(xlabel='Utilisation Cap', ylabel='% of task sets schedulable')
ax.legend()

fig.set_size_inches(7, 2.5)
plt.tight_layout()
fig.savefig('cdf_out.png', dpi=200) 
plt.show()
