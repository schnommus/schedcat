#!/bin/python3

import glob, os

for f in glob.glob("*.csv"):
    with open(f) as f_open:
        with open(f.replace('csv', 'sh'), "w") as w_open:
            for l in f_open.readlines()[1:]:
                b, p = l.strip().split(',')
                w_open.write("rtspin -w {} {} $TEST_DURATION &\n".format(b, p))
