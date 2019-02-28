#!/bin/bash


N=100               # batch size. recommended: 100-300
DIREC="temp_test"   # directory for all outputs

#export PATH="/opt/local/bin":$PATH
#export PATH="/Library/Frameworks/Python.framework/Versions/3.7/bin:${PATH}"
#export PYTHONPATH="/Library/Frameworks/Python.framework/Versions/3.7/bin:${PYTHONPATH}"


##############################################


NUM_TRIALS=$(python3 hope.py $DIREC)

for ((n = 1; n <= $NUM_TRIALS; n++)); do

  # format and solve trials, aggregate NEOS outputs in N-batches
  ((i=i%N)); ((i++==(N-1))) && wait && echo hello at $n &&
    python3 hope_aggregate.py $n $N $NUM_TRIALS $DIREC 0 && wait

  python3 hope_trial.py $n $NUM_TRIALS $DIREC &

done
wait
echo done with all

n=$((NUM_TRIALS+1))
python3 hope_aggregate.py $n $N $NUM_TRIALS $DIREC 1
