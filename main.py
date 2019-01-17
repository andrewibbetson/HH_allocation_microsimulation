'''
Created on Jun 26, 2015

@author: philip
'''
import sys
import argparse
print(sys.version)
import population
import health as hlth

import outputs
import region

import global_vars
import numpy as np

import timeit
import shutil
import os

import pandas as pd
from global_vars import PROJ_PATH


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##Arguments
parser = argparse.ArgumentParser(description='Microsim aregs for LSOA start and stop.')

#input script file
parser.add_argument('-script', metavar='-i',default='England.txt',
                   help='Run name - input script name (default=test.txt)')

##Start files
parser.add_argument('-start', metavar='-s',default=0, type=int,
                   help='Set the start run (default=0)')
##End files
parser.add_argument('-end', metavar='-e',default=5, type=int,
                   help='Set the max number of runs (default=10)')

args = parser.parse_args()

##define start/end run
start_run=args.start
end_run=args.end

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~ Read                         input file
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##read the input script
with open(global_vars.PROJ_PATH+'/input_scripts/'+args.script) as f:
    content = f.readlines()

# you may also want to remove whitespace characters like `\n` at the end of each line
input_vars = {}
content = [x.strip() for x in content]

for c in content:
    if ('=' in c) and '#' not in c:
        # print(c)
        input_vars[c.split('=')[0]] = c.split('=')[1]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##define inputs to read from script file:
##Run name:
name='Test'
##Choose country (options: England, Wales, Scotland, NI, France)
country='England'

reg_file=''
male_file=''
female_file=''

##Run years:
start_year=2016
run_years=106

##Run type (options: Default, Impact, Burden)
run_type='basecase'
pollution_measure=0

validation=False
mortality_projections=False

##Layers:
#Birth rate -  (options: True is use regional data, 0.012 for births/population size, False - no births)
birth_rate=True
#Migration rate - #(options: True is (TODO:) use regional data , 0.012 for births/population size, False - no migration)
migration_rate=False

##PM2.5 - (options: True use regional in RR, False - don't, or specify PM2.5 value in ug/m3)
pollution_pm25=True

##IMD - (options True use regional in RR, False - don't, or specify imd decile)
imd=True

##DISMOD files:
male_pop_file='England_ihd_male_2010.csv'
female_pop_file='England_ihd_female_2010.csv'

##PM2.5 Relative risks
##IHD incidence: default = 1.09 (from meta-analysis), sense1 = 1.09, sense2=1
pm25_hr_inc=0
##IHD CF
pm25_hr_cf=0
##All-cause (Value from Miller et al. 2007)
pm25_hr_allcause=0

#Output directory
output_dir=None


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~ Re-Define input parameters ~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##TODO: option for lag in here?
for i, v in input_vars.items():

    if i=='Name':
        name=v
    elif i=='Birth_rate':
        if v == 'True':
            birth_rate=True
        elif v == 'False':
            birth_rate=False
        else:
            birth_rate=float(v)

    elif i=='Start_year':
        start_year=int(v)
    elif i=='Female_file':
        female_file=v
    elif i=='Male_file':
        male_file=v
    elif i=='Migration_rate':
        if v == 'True':
            migration_rate=True
        elif v == 'False':
            migration_rate=False
        else:
            migration_rate=float(v)

    elif i=='Validation':
        if v == 'True':
            validation=True
        elif v == 'False':
            validation=False
        else:
            validation=v
    elif i=='Mortality_projections':
        mortality_projections=bool(v)
        if v == 'True':
            mortality_projections=True
        elif v == 'False':
            mortality_projections=False
        else:
            mortality_projections=v

    elif i=='Run_years':
        run_years=int(v)
    elif i=='Pollution_pm25':
        if v == 'True':
            pollution_pm25=True
        elif v == 'False':
            pollution_pm25=False
        else:
            pollution_pm25=float(v)

    elif i=='Imd':
        if v == 'True':
            imd=True
        elif v == 'False':
            imd=False
        else:
            imd=v
    elif i=='Pollution_measure':
        pollution_meas=float(v)
    elif i=='PM25_HR_CF':
        pm25_hr_cf=float(v)
    elif i=='Type':
        run_type=v
    elif i=='PM25_HR_ALLCAUSE':
        pm25_hr_allcause=float(v)
    elif i=='PM25_HR_INC':
        pm25_hr_inc=float(v)
    elif i=='Country':
        country=v
    elif i=='Region_file':
        reg_file=v
    elif i=='Male_pop_file':
        male_pop_file=v
    elif i=='Female_pop_file':
        female_pop_file=v

    elif i=='Output_dir':
        output_dir=v
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)


#run name - used for output folder
run_name=country+"_"+run_type

# set output dir if not set in input input_script
if output_dir is None:
    cwd = os.getcwd()
    output_dir = cwd+"/"+run_name+"/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

print(output_dir)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


##Define the diseases of interest here. Only have two state at the moment: CVD and other causes
diseases = []

##Other diseases go here:
cvd = hlth.Disease("IHD",
                    male_file, #male and female dismod files
                    female_file,
                    country=country,
                    pm25_hr_cf=pm25_hr_cf,
                    pm25_hr_inc=pm25_hr_inc)
diseases.append(cvd)

#All cause here
all_cause = hlth.AllCause(projections = mortality_projections, pm25_hr_allcause=pm25_hr_allcause, country=country)
diseases.append(all_cause)

print("Reading regional census data...")
##Create population from census

print(country, reg_file)

if validation != True:
    region_sel = region.Region(country,
                               file=reg_file,
                               birth_rate = True) #, filter_gorcode=['E12000007']
else:
    ##Used for UK testing
    #TODO: may no not work
    region_sel = None
    pop_file = "UK-population-2002"
    #region_sel = region.Region("UK-valid")


if not os.path.exists(global_vars.PROJ_PATH+"/"+run_name):
    os.makedirs(global_vars.PROJ_PATH+"/"+run_name)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##Function called to simulate
def run_sim(lsoa, output):

    np.random.seed(0) # Set the random number generator to a fixed sequence.

    ##Will probs find another way to do this in future from real data (have done now)
    pop = population.Population(1,   ##population size to scale to (1 for census)
                        diseases,   ##defined above
                        start_year,  ##defined above
                        region = region_sel, #region_sel for census, use None for validation
                        lsoa = lsoa,
                        birth_rate = birth_rate,   #None for valid , 0.012
                        migrantion_rate = migration_rate, #None for valid , 0.004
                        male_pop_file = male_pop_file, #"UK-population-2002" for validation
                        female_pop_file=female_pop_file,
                        pollution_pm25 = pollution_pm25,
                        pollution_measure = pollution_meas, #, #-1 is reduce the pollution by 1ug/m3 , 'Burden' for non anth PM
                        imd = imd)

    print("Running Micro-simulation over ", run_years, " years...")
    ###Set up output file and print out initial population stuff

    output.print_pop(start_year, pop)

    ##Loop over years of interest
    for year in range(start_year, start_year+run_years):

        if validation == True:
            dismod_year = pop.find_nearest_year(year)
            print("reading: ", "cvd_male_"+str(dismod_year)+".csv")
            cvd.read_dismod(male_file = "cvd_male_"+str(dismod_year)+".csv", female_file = "cvd_female_"+str(dismod_year)+".csv")
            diseases[0] = cvd

        pop.calc_year(year+1, diseases)
        output.print_pop(year+1, pop)

    return pop.pop_df

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##Function to run for multiple LSOAs
def run_N_lsoas(lsoas):
    #Start of timer to calculate run time
    start = timeit.default_timer()

    for lsoa in lsoas:

        output = outputs.Outputs(lsoa, output_dir=output_dir)

        return_pop = run_sim(lsoa, output)

        output.write_file(return_pop)

        if sys.platform=='linux2' or sys.platform=='linux':
            ##move file to outputs
            shutil.move(output_dir+"/"+output.file_name, global_vars.PROJ_PATH+"/"+run_name+"/"+output.file_name)


            #shutil.rmtree(output_dir)

    end = timeit.default_timer()
    print("time", end-start)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##MAIN:
##For census analysis
#proj_path = os.path.realpath("H:/My Documents/micro-simulation/")
#lsoas_not_run = []
# ##check if file exists, continue if does
# for lsoa in list(region_sel.filtered_lsoas[start_run:end_run]):#[start_run:end_run]
#    if os.path.exists(proj_path+"/"+run_name+"/"+lsoa+".csv"):
#        continue
#    else:
#        lsoas_not_run.append(lsoa)

# run_N_lsoas(lsoas_not_run)

#find out fails
# lsoas_not_run = []
# #check if file exists, continue if does
# for lsoa in list(region_sel.filtered_lsoas):#[start_run:end_run]
#     if os.path.exists(proj_path+"/"+run_name+"/"+lsoa+".csv"):
#         continue
#     else:
#         lsoas_not_run.append(lsoa)
# print(proj_path+"/"+run_name)
# print(lsoas_not_run)
# print(len(lsoas_not_run))
# sys.exit(0)

##to finish off
# lsoas_not_run = ['E01003573', 'E010035734', 'E01003575']
# run_N_lsoas(lsoas_not_run)

##find out fails
# lsoas_not_run = []
# ##check if file exists, continue if does
# for lsoa in list(region_sel.filtered_lsoas):#[start_run:end_run]
#     if os.path.exists(proj_path+"/"+run_name+"/"+lsoa+".csv"):
#         continue
#     else:
#         lsoas_not_run.append(lsoa)
#
# print(proj_path+"/"+run_name)
# print(lsoas_not_run)


##for testing census analysis
# #Start of timer to calculate run time
start = timeit.default_timer()

LSOA_df = pd.read_csv(PROJ_PATH + "/data/camden_lsoa_list_2011.csv")
LSOA_list = LSOA_df['LSOACODE'].tolist()

lsoas = LSOA_list[start_run:end_run] #lsoa (e.g. E01000001) for census, use None for step0_validation_old

run_N_lsoas(lsoas)

#end = timeit.default_timer()
#print("time", end-start)

##For validation

# output = outputs.Outputs("UK-valid")
# valid_pop = run_sim("UK-valid", output)
# output.write_file(valid_pop)

##TODO: list
#TODO: Add regionally explicit migration
#TODO: commutes (data available) employment?
#TODO: houses (EPC data?)
#TODO: clean up options
#TODO: Consider doing CVD projection (same as all-cause?)
