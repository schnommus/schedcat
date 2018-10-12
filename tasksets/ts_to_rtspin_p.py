#!/bin/python3

import glob, os

for f in glob.glob("*.csv"):
    with open(f) as f_open:
        with open(f.replace('csv', 'sh'), "w") as w_open:
            cur_task = 0
            for l in f_open.readlines()[1:]:
                cur_task += 1
                b, p = l.strip().split(',')
                partition = cur_task / 
                w_open.write("rtspin -w {} {} $TEST_DURATION &\n".format(b, p))
