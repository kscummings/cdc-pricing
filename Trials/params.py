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
HMIL = 10**5
DEC = 10**-1
OBJ = 10**-4


#---------------------------- GET OUTPUT DIRECTORY
DIREC = sys.argv[1]
try:
    os.mkdir(DIREC)
except OSError:     # directory exists
    pass

#---------------------------- GLOBAL TRIAL INPUTS (maxes are inclusive)

# DEM = [4 *MIL , 8 *MIL]                # total annual US demand
# DEM_INT = 0.5 *MIL                     # demand interval
#
# GAM = [1 *DEC, 5 *DEC]                 # product similarity in [0,1], where 1=identical
# GAM_INT = 0.5 *DEC
#
# CAP = [3 *MIL , 6 *MIL]                # production capacity min, max
# CAP_INT = 1 * MIL                      # production capacity interval
#
# PROF = [30 *MIL , 50 *MIL]             # target profit min, max
# PROF_INT = 5 *MIL                      # target profit interval
#
# OBJ_GOVT = [OBJ, OBJ]                  # objective function weight for gov't cost
# OBJ_GOVT_INT = OBJ                     # gov't cost weight interval
#
# M1_INFLATION = [17.25]                # inflation price upper bound
# M2_INFLATION = [17.13] # DAPTACEL

DEM = [4 *MIL , 5 *MIL]                # total annual US demand
DEM_INT = 1 *MIL                     # demand interval

GAM = [1 *DEC, 3 *DEC]                 # product similarity in [0,1], where 1=identical
GAM_INT = 0.2 *DEC

CAP = [3 *MIL , 4 *MIL]                # production capacity min, max
CAP_INT = 1 * MIL                      # production capacity interval

PROF = [30 *MIL , 40 *MIL]             # target profit min, max
PROF_INT = 10 *MIL                      # target profit interval

OBJ_GOVT = [OBJ, OBJ]                  # objective function weight for gov't cost
OBJ_GOVT_INT = OBJ                     # gov't cost weight interval

M1_INFLATION = [17.25]                # inflation price upper bound
M2_INFLATION = [17.13] # DAPTACEL

#---------------------------- CREATE PARAMETER GRID

# generate unique pairs of manufacturers
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
