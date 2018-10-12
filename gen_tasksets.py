#!/bin/python2

import sys

import schedcat.generator.generator_emstada as generator
from schedcat.overheads.model import Overheads, CacheDelay
from schedcat.overheads.jlfp import charge_scheduling_overheads, \
                                    quantize_params
import schedcat.sched.edf as edf
from schedcat.util.math import const

import numpy as np

n_tasks = 16
n_cpus = int(sys.argv[1])

gen_utilisation = n_cpus / 2.0

ts = generator.gen_taskset('uni-short', 'unif', n_tasks, gen_utilisation)

print "budget (ms),period (ms)"

total_utilisation = 0.0

for t in ts:
    actual_cost = t.cost / 10
    actual_period = t.period / 10

    if actual_cost == 0 or actual_period == 0:
        print "Zero cost/period!!"

    print "{},{}".format(actual_cost, actual_period)

    total_utilisation += float(actual_cost) / float(actual_period)

print total_utilisation
