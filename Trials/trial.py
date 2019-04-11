"""
Format trial in DAT and XML files
Send XML file to NEOS
Delete XML file
Write output to txt file
"""
import numpy as np
import pandas as pd
import sys
import random
import math
import unicodedata
import fileinput
import xmlrpc.client as xmlrpclib
import time
import os

#------------------------------CONSTANTS

DIREC = sys.argv[3]
MODEL_FILE = "../model/model.mod"
COMMAND_FILE = "../model/commands.txt"
NEOS_HOST="neos-server.org"
NEOS_PORT=3333



#------------------------------GET TRIAL
TRIAL_NUM = sys.argv[1]
NUM_TRIALS = int(sys.argv[2])
NUM_DIGITS = int(np.ceil(np.log10(NUM_TRIALS)))
trial_id = TRIAL_NUM.zfill(NUM_DIGITS)

df = pd.read_pickle(DIREC+"/param_grid.pkl")
trial = df.loc[trial_id].apply(str)       # convert to strings


#------------------------------FORMAT DAT FILE THAT IS EMBEDDED IN XML FILE

"""
Start output string
"""

all_text=[]

all_text.append("set Manufacturers := x y; \n")               # sets
all_text.append("set Sectors := public private; \n")
                                                                # manufacturer params
all_text.append("param: profit := \n x "+trial['m1_prof']+"\n y "+trial['m2_prof']+"; \n")
all_text.append("param: capacity := \n x "+trial['m1_cap']+"\n y "+trial['m2_cap']+"; \n")
all_text.append("param demand := "+trial['dem']+"; \n")         # market params
all_text.append("param gamma := "+trial['prod_sim']+"; \n")
all_text.append("param objCost = "+trial['obj_govt']+"; \n")    # objective function weight
all_text.append("param inflationPrice := x "+trial['m1_infl']+"\n y "+trial['m2_infl']+"; \n")

gamma = float(trial['prod_sim'])                                # linear demand curves
a = [2219700+1102300/(1+gamma), 1674500+2246600/(1+gamma)]      # pub, priv (HEPB)
#a = [1396000+1526143/(1+gamma), 1053000+2361286/(1+gamma)]      # pub, priv (DTAP)
b = [100000/((1+gamma)*(1-gamma)), 100000/((1+gamma)*(1-gamma))]
c = [gamma*b[0], gamma*b[1]]
all_text.append("param: a := \n public "+str(a[0])+"\n private "+str(a[1])+";\n")
all_text.append("param: b := \n public "+str(b[0])+"\n private "+str(b[1])+"; \n")
all_text.append("param: c := \n public "+str(c[0])+"\n private "+str(c[1])+"; \n")


#------------------------------FORMAT XML FILE

mod = open(MODEL_FILE)   # model
model = mod.read()
mod.close()
run = open(COMMAND_FILE) # commands
commands = run.read()
run.close()

xml_text = []

xml_text.append("<document> \n")
xml_text.append("<category>minco</category> \n")
xml_text.append("<solver>BARON</solver> \n")
xml_text.append("<inputMethod>AMPL</inputMethod> \n")
xml_text.append("<model><![CDATA[ \n")
xml_text.append( model  + "\n")
xml_text.append("]]></model> \n")
xml_text.append("<data><![CDATA[ \n")
for i in range(len(all_text)):
    xml_text.append('\n'+all_text[i])
xml_text.append("]]></data> \n")
xml_text.append("<commands><![CDATA[ \n")
xml_text.append( commands + "\n")
xml_text.append("]]></commands> \n")
xml_text.append("</document>")


"""
Uncomment to write/read XML file
"""
# f = open(DIREC+"/XML"+trial_id+".xml", 'w')        # open new file to send to NEOS
#
# for i in range(len(xml_text)):                     # create file
#     f.write('\n'+xml_text[i])
#
# f.close()
#
# #Read XML file
# xml_file = open(DIREC+"/XML"+trial_id+".xml","r")
#
# xml=""
# buffer=1
# while buffer:
#     buffer =  xml_file.read()
#     xml+= buffer
# xml_file.close()
# os.remove(DIREC+"/XML"+trial_id+".xml")


#------------------------------SEND TO NEOS AND RETRIEVE RESULTS


neos=xmlrpclib.Server("https://%s:%d" % (NEOS_HOST, NEOS_PORT))


xml = ''.join(xml_text)             # convert from list to string
(jobNumber,password) = neos.submitJob(xml)

#uncomment to print out partial job while running
#sys.stdout.write("JobNumber = %d " % jobNumber)

offset=0
status=""
while status != "Done":
    (msg,offset) = neos.getIntermediateResults(jobNumber,password,offset)
    #sys.stdout.write(msg.data.decode())
    status = neos.getJobStatus(jobNumber, password)


#------------------------------WRITE RESULTS

msg = neos.getFinalResults(jobNumber, password).data
buf = open(DIREC+"/NEOS"+trial_id+".txt", 'w')
buf.write(msg.decode())
buf.close()

#print("Done with trial "+trial_id)
