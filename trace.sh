#!/bin/bash

N_CPUS=$1
SCHEDULER_NAME=$2
TEST_DURATION=5
TRACE_NAME=$SCHEDULER_NAME-trace-${1}cpus

LAST_CPU=7

for i in `seq 0 $(($N_CPUS - 1))`; do
    CMD="echo 1 > /sys/devices/system/cpu/cpu${i}/online"
    echo $CMD
    eval $CMD
done

for i in `seq $N_CPUS $LAST_CPU`; do
    CMD="echo 0 > /sys/devices/system/cpu/cpu${i}/online"
    echo $CMD
    eval $CMD
done

export PATH=/home/qcsim/litmus/feather-trace-tools/:$PATH
export PATH=/home/qcsim/litmus/liblitmus/:$PATH

setsched Linux

setsched $SCHEDULER_NAME

ft-trace-overheads -s $TRACE_NAME &

sleep 5

# Run the specified taskset
TASKSET=../tasksets/ts_${1}cpu.sh
echo $TASKSET
eval $TASKSET

release_ts

sleep $TEST_DURATION

killall -s SIGUSR1 ft-trace-overheads
killall rtspin

ft-sort-traces *$TRACE_NAME*.bin 2>&1 | tee -a overhead-processing.log

ft-extract-samples *$TRACE_NAME*.bin 2>&1 | tee -a overhead-processing.log

ft-compute-stats *$TRACE_NAME*.float32 > $TRACE_NAME.csv
