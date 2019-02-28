# Vaccine market analysis
___

**Work in progress!**

 This code is for the paper, "CDC as a Strategic Agent in the Pediatric Vaccine Market:
 An Analytical Approach," joint with B. Behzad and S. Martonosi.

### Inputs

* Specify parameter ranges and intervals in `params.py`.
* Specify batch size *N* and output directory name in `bigsolve.sh`.

### Run the code

1. Navigate to working directory and give permission to execute (`chmod`).
2. Use the command `./bigsolve.sh` to execute, which will:
   * Run `params.py` to expand the parameter grid and enumerate each trial;
   * Run `trial.py` in parallel *N*-batches, to build the model, format the jobs, and send them to NEOS;
   * Run `aggregate.py` after every *N* trials to compile the outputs into one CSV containing the optimal solutions.
