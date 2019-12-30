"""
Create parameter grid and identify each trial uniquely

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xmlrpc.client as xmlrpclib  # for NEOS server
import argparse
import os
import re
import time
import sys
import scipy.io
import random
import math
import unicodedata
import fileinput
import itertools



MIL = 10**6
TH = 10**3
DEC = 10**-1
OBJ = 10**-4

#---------------------------- TOGGLE TRIAL TYPE

STANDARD = 0
UNIQUE_MANUF = 0
DEM_CAP = 0
DEM_PROF = 0
CAP_PROF = 0
TRIANGULAR = 1

NUM_SAMPLES = 10000

#---------------------------- GET OUTPUT DIRECTORY
DIREC = sys.argv[1]
try:
    os.mkdir(DIREC)
except OSError:     # directory exists
    pass

#---------------------------- GLOBAL TRIAL INPUTS (maxes are inclusive)

DEM = [4 *MIL , 4 *MIL]                # total annual US demand
DEM_INT = MIL                                # demand interval

GAM = [0.25,0.25]                               # product similarity in [0,1], where 1=identical
GAM_INT = 1

OBJ_GOVT = [OBJ, OBJ]                  # objective function weight for gov't cost
OBJ_GOVT_INT = 5                     # gov't cost weight interval

M1_INFLATION = [18.62] #inf                   # inflation price upper bound
M2_INFLATION = [18.02] #dap


#---------------------------- CREATE PARAMETER GRID

if STANDARD==1:

    M1_CAP = [4.034 *MIL, 4.034 *MIL] #inf              # production capacity min, max
    M1_CAP_INT = 33260                                 # production capacity interval
    M2_CAP = [4.034 *MIL, 4.034 *MIL] #dap
    M2_CAP_INT = 33260

    M1_PROF = [26.5 *MIL, 26.5 *MIL] #inf              # target profit min, max
    M1_PROF_INT = 2.65 *MIL#530 *TH                              # target profit interval
    M2_PROF = [26.5 *MIL, 26.5 *MIL] #dap
    M2_PROF_INT = 2.65 *MIL#530 *TH

    # populate grid with distinct manufacturers
    grid=np.array([(K1,K2,P1,P2,D,G,OG,I1,I2)
           for K1 in np.arange(M1_CAP[0],M1_CAP[1]+M1_CAP_INT,M1_CAP_INT)
           for K2 in np.arange(M2_CAP[0],M2_CAP[1]+M2_CAP_INT,M2_CAP_INT)
           for P1 in np.arange(M1_PROF[0],M1_PROF[1]+M1_PROF_INT,M1_PROF_INT)
           for P2 in np.arange(M2_PROF[0],M2_PROF[1]+M2_PROF_INT,M2_PROF_INT)
           for D in np.arange(DEM[0],DEM[1]+DEM_INT,DEM_INT)
           for G in np.arange(GAM[0],GAM[1]+GAM_INT,GAM_INT)
           for OG in np.arange(OBJ_GOVT[0],OBJ_GOVT[1]+OBJ_GOVT_INT,OBJ_GOVT_INT)
           for I1 in M1_INFLATION
           for I2 in M2_INFLATION
        ])


########## generate unique pairs of manufacturers
# doesnt think about inflation bounds
if UNIQUE_MANUF==1:

    CAP = [4.034 *MIL , 4.034 *MIL]                # production capacity min, max
    CAP_INT = 100 *MIL                      # production capacity interval

    PROF = [26.5 *MIL , 53 *MIL]             # target profit min, max
    PROF_INT = 530 *TH                      # target profit interval

    manuf=[(K,P) for K in np.arange(CAP[0],CAP[1]+CAP_INT,CAP_INT)
              for P in np.arange(PROF[0],PROF[1]+PROF_INT,PROF_INT)]
    valid_trials=[(i,j) for i in np.arange(len(manuf))
                        for j in np.arange(i+1)]
    x=[(manuf[id[0]],manuf[id[1]]) for id in valid_trials]
    x=np.array([list(itertools.chain(*x[i])) for i in np.arange(len(x))]) #squash

    # populate rest of grid
    grid=np.array([(x[M,0],x[M,2],x[M,1],x[M,3],D,G,OG,P1,P2)
           for M in np.arange(len(x))
           for D in np.arange(DEM[0],DEM[1]+DEM_INT,DEM_INT)
           for G in np.arange(GAM[0],GAM[1]+GAM_INT,GAM_INT)
           for OG in np.arange(OBJ_GOVT[0],OBJ_GOVT[1]+OBJ_GOVT_INT,OBJ_GOVT_INT)
           for P1 in M1_INFLATION
           for P2 in M2_INFLATION
        ])

# run capacity difference trials
if DEM_CAP==1:

    TOTAL_CAP = 4.034*2 *MIL
    CAP = [2.534 *MIL, 4.034 *MIL]
    CAP_INT = 250000

    M1_PROF = [42.45 *MIL, 42.45 *MIL] #rec              # target profit min, max
    M1_PROF_INT = 530 *TH                              # target profit interval
    M2_PROF = [42.45 *MIL, 42.45 *MIL] #eng
    M2_PROF_INT = 530 *TH


    grid=np.array([(K,TOTAL_CAP-K,P1,P2,D,G,OG,I1,I2)
           for K in np.arange(CAP[0],CAP[1]+CAP_INT,CAP_INT)
           for P1 in np.arange(M1_PROF[0],M1_PROF[1]+M1_PROF_INT,M1_PROF_INT)
           for P2 in np.arange(M2_PROF[0],M2_PROF[1]+M2_PROF_INT,M2_PROF_INT)
           for D in np.arange(DEM[0],DEM[1]+DEM_INT,DEM_INT)
           for G in np.arange(GAM[0],GAM[1]+GAM_INT,GAM_INT)
           for OG in np.arange(OBJ_GOVT[0],OBJ_GOVT[1]+OBJ_GOVT_INT,OBJ_GOVT_INT)
           for I1 in M1_INFLATION
           for I2 in M2_INFLATION
        ])

# run profit difference trials
if DEM_PROF==1:

    M1_CAP = [4.034 *MIL, 4.034 *MIL] #rec              # production capacity min, max
    M1_CAP_INT = 23480                                 # production capacity interval
    M2_CAP = [4.034 *MIL, 4.034 *MIL] #eng
    M2_CAP_INT = 23480

    TOTAL_PROF = 84.9 *MIL
    PROF = [28.45 *MIL, 42.45 *MIL]
    PROF_INT = 2*MIL

    grid=np.array([(K1,K2,P,TOTAL_PROF - P,D,G,OG,I1,I2)
           for K1 in np.arange(M1_CAP[0],M1_CAP[1]+M1_CAP_INT,M1_CAP_INT)
           for K2 in np.arange(M2_CAP[0],M2_CAP[1]+M2_CAP_INT,M2_CAP_INT)
           for P in np.arange(PROF[0],PROF[1]+PROF_INT,PROF_INT)
           for D in np.arange(DEM[0],DEM[1]+DEM_INT,DEM_INT)
           for G in np.arange(GAM[0],GAM[1]+GAM_INT,GAM_INT)
           for OG in np.arange(OBJ_GOVT[0],OBJ_GOVT[1]+OBJ_GOVT_INT,OBJ_GOVT_INT)
           for I1 in M1_INFLATION
           for I2 in M2_INFLATION
        ])

# run capacity profit difference trials
if CAP_PROF==1:

    TOTAL_PROF = 84.9 *MIL
    PROF = [32.5 *MIL, 52.4 *MIL]
    PROF_INT = 398*TH
    TOTAL_CAP = 4.034*2 *MIL
    CAP = [2.034 *MIL, 4.034 *MIL]
    CAP_INT = 40 *TH

    grid=np.array([(K,TOTAL_CAP-K,P,TOTAL_PROF - P,D,G,OG,I1,I2)
           for K in np.arange(CAP[0],CAP[1]+CAP_INT,CAP_INT)
           for P in np.arange(PROF[0],PROF[1]+PROF_INT,PROF_INT)
           for D in np.arange(DEM[0],DEM[1]+DEM_INT,DEM_INT)
           for G in np.arange(GAM[0],GAM[1]+GAM_INT,GAM_INT)
           for OG in np.arange(OBJ_GOVT[0],OBJ_GOVT[1]+OBJ_GOVT_INT,OBJ_GOVT_INT)
           for I1 in M1_INFLATION
           for I2 in M2_INFLATION
        ])

# draw samples from triangular distributions
if TRIANGULAR==1:
    K_inf = np.random.triangular(2.837 *MIL, 4.034 *MIL, 4.034 *MIL, NUM_SAMPLES)
    K_dap = np.random.triangular(2.837 *MIL, 4.034 *MIL, 4.034 *MIL, NUM_SAMPLES)
    P_inf = np.random.triangular(26.5 *MIL, 39.8 *MIL, 53 *MIL, NUM_SAMPLES)
    P_dap = np.random.triangular(26.5 *MIL, 45.1 *MIL, 53 *MIL, NUM_SAMPLES)
    D = np.random.triangular(4 *MIL, 4.034 *MIL, 7.832 *MIL, NUM_SAMPLES)
    G = np.random.triangular(0.01, 0.25, 0.5, NUM_SAMPLES)
    O = np.repeat(OBJ_GOVT[0], NUM_SAMPLES)
    R_inf = np.repeat(M1_INFLATION[0], NUM_SAMPLES)
    R_dap = np.repeat(M2_INFLATION[0], NUM_SAMPLES)
    grid = np.array((K_inf, K_dap, P_inf, P_dap, D, G, O, R_inf, R_dap)).T

# convert to data frame
df = pd.DataFrame(grid)
df.columns = ("m1_cap","m2_cap","m1_prof","m2_prof","dem","prod_sim",
                "obj_govt","m1_infl","m2_infl")

# create trial id and fill with leading zeros
id = np.arange(1,len(grid)+1)
n_digits = np.ceil(np.log10(len(id))).astype(np.int64)  # max number of digits
df.index = [str(id[i]).zfill(n_digits) for i in range(len(id))]

# write to pickle
df.to_pickle(DIREC+"/param_grid.pkl")

#---------------------------- CAPTURE SIZE OF PARAM GRID IN BASH SCRIPT

print(len(id))
