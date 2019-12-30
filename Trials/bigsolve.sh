# See readme for instructions


N=150              # batch size. recommended: 100-200
DIREC="triangle"   # directory for all outputs

NUM_TRIALS=$(python3 params.py $DIREC)
echo $NUM_TRIALS

for ((n = 1; n <= $NUM_TRIALS; n++)); do

  # format and solve trials, aggregate NEOS outputs in N-batches
  ((i=i%N)); ((i++==(N-1))) && wait && echo hello at $n &&
    python3 aggregate.py $n $N $NUM_TRIALS $DIREC 0 && wait

  python3 trial.py $n $NUM_TRIALS $DIREC &

done
wait
echo done with all

n=$((NUM_TRIALS+1))
python3 aggregate.py $n $N $NUM_TRIALS $DIREC 1
