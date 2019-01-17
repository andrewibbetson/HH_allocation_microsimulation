# HH_allocation_microsimulation
A household allocation algorithm for microsimulation.

This is a household allocation package for a UK microsimulation model (on bitbucket: https://bitbucket.org/psymo87/micro-simulation). 

The allocation process can be run using the 'run_HH_allocation' function in 'h_main.py'.

It requires Gurobi optimisation software.

The process of household allocation consists of two main steps:

i. An iterative proportional fit to reweight English Housing Survey data to LSOA level aggregates

ii. Filling the generated households with individuals from census population data at the LSOA level. Initially, the generated households 
    do not match census population data. To solve this we can write a mixed integer problem and, using the optimisation software Gurobi, 
    we can solve this problem in an optimal fashion, so that the generated households match the census population totals.  

For a full explanation of the household allocation method, see Husby, Ivanova and Thissen (2018) https://www.microsimulation.org/IJM/V11_2/IJM_11_2_5.pdf 

