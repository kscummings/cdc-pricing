"""
Parse optimal solutions from NEOS outputs
Write aggregated results
Remove temp files from output directory
"""

import numpy as np
import pandas as pd
import sys
import random
import math
import unicodedata
import fileinput
import time
import os
import re

#-----------------------A FUNCTION TO PARSE ONE NEOS TXT OUTPUT
def parse(trial_id, df):

    # if optimal solution was found, grab it
    neos_filename = DIREC + "/NEOS" + trial_id + ".txt"

    if "optimal" in open(neos_filename,'r').read():
        f = open(neos_filename,'r')
        first_line = f.readline()
        for line in f:
            if "price" in line:
                temp = next(f)
                d=re.search('\d',temp)   # grab first digit
                df.loc[trial_id]['m1_pub_price']=float(temp[d.start():])
                temp = next(f)
                d=re.search('\d',temp)
                df.loc[trial_id]['m2_pub_price']=float(temp[d.start():])
                temp = next(f)
                d=re.search('\d',temp)
                df.loc[trial_id]['m1_priv_price']=float(temp[d.start():])
                temp = next(f)
                d=re.search('\d',temp)
                df.loc[trial_id]['m2_priv_price']=float(temp[d.start():])
            if "quant" in line:
                temp = next(f)
                d=re.search('\d',temp)
                df.loc[trial_id]['m1_pub_quant']=float(temp[d.start():])
                temp = next(f)
                d=re.search('\d',temp)
                df.loc[trial_id]['m2_pub_quant']=float(temp[d.start():])
                temp = next(f)
                d=re.search('\d',temp)
                df.loc[trial_id]['m1_priv_quant']=float(temp[d.start():])
                temp = next(f)
                d=re.search('\d',temp)
                df.loc[trial_id]['m2_priv_quant']=float(temp[d.start():])

            if "governmentCost" in line:
                a=re.search('\d',line)
                df.loc[trial_id]['govt_cost']=float(line[a.start():])

        f.close()
    os.remove(neos_filename)
    return df


#-----------------------GET TRIALS [a,b) TO AGGREGATE
b = int(sys.argv[1])   # last trial, exclusive
N = int(sys.argv[2])   # batch size
T = int(sys.argv[3])   # number of trials

if b==1:        # there's only one trial
    a = 1
    b = 2
elif N > b:     # batch size exceeds number of trials, aggregate everything
    a = 1
else:           # compute first trial, inclusive
    a = b - (b%N)*(b>T) - N*(b<=T) + (b==N)

# trials we will aggregate
n_digits = int(np.ceil(np.log10(T)))
to_parse = [str(np.arange(a,b)[i]).zfill(n_digits) for i in range(b-a)]


#-----------------------CREATE RESULTS CSV OR READ IT IN
DIREC = sys.argv[4]  # directory containing results
filename = DIREC + "/" + DIREC + "_results"

if b<=N:
    # expand param grid pickle into results df
    df = pd.read_pickle(DIREC+"/param_grid.pkl")
    emptydf = pd.DataFrame(np.nan,index=df.index,columns=(
        'm1_pub_price','m2_pub_price','m1_priv_price','m2_priv_price',
        'm1_pub_quant','m2_pub_quant','m1_priv_quant','m2_priv_quant',
        'govt_cost'))
    df = pd.concat([df,emptydf],axis=1)
else:
    # read in results
    df = pd.read_pickle(filename+".pkl")


#-----------------------PARSE AND WRITE

for trial_id in to_parse:
    df = parse(trial_id, df)

if int(sys.argv[5])==1:
    df.to_csv(filename+".csv",index=False)
    os.remove(DIREC+"/param_grid.pkl")
    try:
        os.remove(filename+".pkl")
    except OSError:     # only aggregated once
        pass
else:
    df.to_pickle(filename+".pkl")
