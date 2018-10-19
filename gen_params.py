#!/bin/python2

import sys

import schedcat.generator.generator_emstada as generator
from schedcat.overheads.model import Overheads, CacheDelay
from schedcat.overheads.jlfp import charge_scheduling_overheads, \
                                    quantize_params
import schedcat.sched.edf as edf
from schedcat.util.math import const

import numpy as np

n_tasks_max = 256
n_sets = 4

gen_utilisation = 0.7

for n_tasks in range(1,n_tasks_max+1):
    print(' '*4 + '/* {} tasks */'.format(n_tasks))
    print(' '*4 + '{')
    for set_id in range(n_sets):

        ts = generator.gen_taskset('uni-broad', 'unif', n_tasks, gen_utilisation)

        for t in ts:
            actual_cost = t.cost*100
            actual_period = t.period*100

            if actual_cost == 0 or actual_period == 0:
                print "Zero cost/period!!"

            print(' '*8 + "{{{}, {}}},".format(actual_cost, actual_period))

        print

    print(' '*4 + '},')
