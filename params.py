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

MIL = 10**6
HMIL = 10**5
DEC = 10**-1


#---------------------------- GET OUTPUT DIRECTORY
DIREC = sys.argv[1]
try:
    os.mkdir(DIREC)
except OSError:     # directory exists
    pass

#---------------------------- GLOBAL TRIAL INPUTS (maxes are inclusive)

DEM = [4 *MIL , 8 *MIL]                # total annual US demand
DEM_INT = 0.5 *MIL                     # demand interval

GAM = [1 *DEC, 5 *DEC]                 # product similarity in [0,1], where 1=identical
GAM_INT = 0.5 *DEC

CAP = [3 *MIL , 6 *MIL]                # production capacity min, max
CAP_INT = 1 * MIL                      # production capacity interval

PROF = [30 *MIL , 50 *MIL]             # target profit min, max
PROF_INT = 5 *MIL                      # target profit interval

OBJ_GOVT = [5 *(1/MIL), 5 *(1/MIL)]    # objective function weight for gov't cost
OBJ_GOVT_INT = 1 *(1/MIL)              # gov't cost weight interval


#---------------------------- CREATE PARAMETER GRID

# populate
grid = np.array(
    [(K1,K2,P1,P2,D,G,OG)
       for K1 in np.arange(CAP[0],CAP[1]+CAP_INT,CAP_INT)
       for K2 in np.arange(CAP[0],K1+CAP_INT,CAP_INT)         # lower triangle
       for P1 in np.arange(PROF[0],PROF[1]+PROF_INT,PROF_INT)
       for P2 in np.arange(PROF[0],P1+PROF_INT,PROF_INT)      # lower triangle
       for D in np.arange(DEM[0],DEM[1]+DEM_INT,DEM_INT)
       for G in np.arange(GAM[0],GAM[1]+GAM_INT,GAM_INT)
       for OG in np.arange(OBJ_GOVT[0],OBJ_GOVT[1]+OBJ_GOVT_INT,OBJ_GOVT_INT)
    ])


# convert to data frame
df = pd.DataFrame(grid)
df.columns = ("m1_cap","m2_cap","m1_prof","m2_prof","dem","prod_sim","obj_govt")

# create trial id and fill with leading zeros
id = np.arange(1,len(grid)+1)
n_digits = np.ceil(np.log10(len(id))).astype(np.int64)  # max number of digits
df.index = [str(id[i]).zfill(n_digits) for i in range(len(id))]

# write to pickle
df.to_pickle(DIREC+"/param_grid.pkl")

#---------------------------- CAPTURE SIZE OF PARAM GRID IN BASH SCRIPT

print(len(id))
