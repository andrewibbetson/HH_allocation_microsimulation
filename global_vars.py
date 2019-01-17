'''
Created on Jan 6, 2016

@author: philip
'''
"""File containing global variables used throughout code"""

import os
import sys

if sys.platform=='darwin':
    print("Operating System: MAC OS")
#   PROJ_PATH = os.path.realpath("/Users/PhilSymonds/Documents/workspace/micro-simulation/")
    PROJ_PATH = os.path.expanduser("~/micro-simulation/")
elif sys.platform=='linux2' or sys.platform=='linux':
    ##For legion
    print("Operating System: linux")
    PROJ_PATH = os.path.realpath("/home/ucqbpsy/Scratch/Simulations/micro-simulation/")
elif sys.platform=='win32':
    ##For legion
    print("Operating System: windows")
    PROJ_PATH = os.path.realpath("H:/My Documents/micro-simulation_housing/")
else:
    print("rootdir not found")
#proj_path = os.path.realpath("/home/ucqbpsy/Scratch/Simulations/micro-sim-080217")
#for local

MAX_AGE = 100
MIGRANT_MAX_AGE = 70

##Pollution Consts
##UK values calculated using census and Ricardo data
##France value of 12.37 come from here: https://www.indexmundi.com/facts/france/indicator/EN.ATM.PM25.MC.M3

PM25_MEAN = {'England': 9.356, 'Wales':8.029, 'Scotland':6.084, 'NI':6.074, 'France':12.37, 'UK':9.2}  #2015)  ##12.12 (#2011)


##IMD death rate Hazard ratios by GOR
##For CVD (Table 2 of https://www.ons.gov.uk/ons/rel/hsq/health-statistics-quarterly/no--32--winter-2006/mortality-by-deprivation-and-cause-of-death-in-england-and-wales--1999-2003.pdf)  Wales, Scot, NI
##FRANCE values from here: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2637240/ - 35 is Rennes department
IMD_CVD_MALE   = {"E12000001": 2.3, "E12000002": 2.2,"C": 1.9,"E12000003": 2, "E12000004": 2, "E12000005": 2, "E12000006": 1.9, "E12000007": 2, "E12000008": 2.1, "E12000009": 2.1, "E12000010": 1.9, "E12000011": 2.3, "E12000012": 2.3,
                  35:1.496}
IMD_CVD_FEMALE = {"E12000001": 2.3, "E12000002": 2.4,"C": 2.3,"E12000003": 2.2, "E12000004": 2.1, "E12000005": 2.2, "E12000006": 2.1, "E12000007": 2.1, "E12000008": 2.1, "E12000009": 2.4, "E12000010": 2.3, "E12000011": 2.4, "E12000012": 2.4,
                  35:1.397}


##For All cause
##For France 29% higher in most than least deprived quintile: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2637240/ (see table 1)
IMD_HR_FRANCE=1.419
IMD_HR_M = 1.7
IMD_HR_F = 1.5


###France birth rates /100 females for metropolitan  areas from: https://www.insee.fr/fr/statistiques/1892259?sommaire=1912926&q=taux+g%C3%A9n%C3%A9ral+de+f%C3%A9condit%C3%A9
FERTILITY_FR = {'15-24':2.2, '25-29':11.0, '30-34':12.7, '35-39':6.8,  '40-50':0.8}
