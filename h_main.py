from LSOA_agg import calc_census_marginal_totals, TRS
from microdata import microdata, EHS, scatter_plot
import my_ipfn as ipfn

import pandas as pd
import numpy as np
import HH
import cvxpy as cp
import os
import outputs
import sys


def generate_HHs(lsoa):

    marginals = calc_census_marginal_totals(lsoa)

    region_df = EHS(lsoa)

    original_df = region_df.copy()

    aggregates, dimensions = microdata(marginals, region_df)

    IPF = ipfn.ipfn(region_df, aggregates, dimensions)
    region_df, df_list = IPF.iteration()

    cwd = os.getcwd()
    output_dir = cwd+"/housing_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df_list.insert(0, original_df)
    IPF_df = pd.concat(df_list)

    IPF_name = lsoa + "_IPF"
    IPF_output = outputs.Outputs(IPF_name, output_dir=output_dir)
    IPF_output.write_file(IPF_df)

    region_df['total'] = TRS(region_df['total'])

    region_df = region_df[region_df.total != 0]
    region_df = region_df.astype(int)

    region_df.to_csv(output_dir + "/" + lsoa + "_IPF_post_integerisation.csv")

    IPF_posti_name = lsoa + "_IPF_post_integerisation"
    IPF_posti_output = outputs.Outputs(IPF_posti_name, output_dir=output_dir)
    IPF_posti_output.write_file(region_df)

    HH_list = []
    for index, row in region_df.iterrows():
        for n in range(row['total']):

            household = HH.HH(row['hhsizex'], row['sexhrp'], row['agehrp6x'], row['dwtypenx'], row['hhtype7'])
            HH_list.append(household)

    unadj_HH_list = []
    for house in HH_list:
        unadj_HH_list.append([house.id, house.agehrp, house.sexhrp, house.dwtype, house.hhtype, house.hhsize, house.mip])

    unadj_HH_df = pd.DataFrame(unadj_HH_list, columns=['HH_id', 'agehrp', 'sexhrp', 'dwtype', 'hhtype', 'hhsize', 'mip'])

    unadj_HH_name = lsoa + "_unadjusted_HHs"
    unadj_HH_output = outputs.Outputs(unadj_HH_name, output_dir=output_dir)
    unadj_HH_output.write_file(unadj_HH_df)

    if sys.platform=='linux2' or sys.platform=='linux':
        shutil.move(output_dir+"/"+unadj_HH_output.file_name, global_vars.PROJ_PATH+"/"+run_name+"/"+unadj_HH_output.file_name)
        shutil.move(output_dir+"/"+IPF_posti_output.file_name, global_vars.PROJ_PATH+"/"+run_name+"/"+IPF_posti_output.file_name)
        shutil.move(output_dir+"/"+IPF_output.file_name, global_vars.PROJ_PATH+"/"+run_name+"/"+IPF_output.file_name)

    return HH_list

def assign_HRP(pop_list, HH_list):

    HH_with_head = []
    assigned_persons = []
    for person in pop_list:
        for HH in HH_list:

            if len(HH.occupants) == 0:

                if HH.sexhrp == person.sex and HH.agehrp == person.age_cat:
                    HH.occupants.append(person)
                    person.HHid = HH.id

                    assigned_persons.append(person)
                    HH_with_head.append(HH)

                    break

                else:

                    continue

            else:

                continue

    unassigned_persons = list(set(pop_list) - set(assigned_persons))
    HH_no_head = list(set(HH_list) - set(HH_with_head))


    if len(HH_no_head) > 0:

        print('HRP constraints relaxed: 1')

        for person in unassigned_persons:
            for HH in HH_no_head:

                if len(HH.occupants) == 0:

                    if HH.agehrp == person.age_cat:
                        HH.occupants.append(person)
                        person.HHid = HH.id

                        assigned_persons.append(person)
                        HH_with_head.append(HH)

                        break

                    else:

                        continue

                else:

                    continue

    unassigned_persons = list(set(pop_list) - set(assigned_persons))
    HH_no_head = list(set(HH_list) - set(HH_with_head))

    if len(HH_no_head) > 0:

        print('HRP constraints relaxed: 2')

        for person in unassigned_persons:
            for HH in HH_no_head:

                if len(HH.occupants) == 0:

                    if (HH.agehrp - person.age_cat) < 2:
                        HH.occupants.append(person)
                        person.HHid = HH.id

                        assigned_persons.append(person)
                        HH_with_head.append(HH)

                        break

                    else:

                        continue

                else:

                    continue

    unassigned_persons = list(set(pop_list) - set(assigned_persons))
    HH_no_head = list(set(HH_list) - set(HH_with_head))

    if len(HH_no_head) > 0:

        print('HRP constraints relaxed: 3')

        for person in unassigned_persons:
            for HH in HH_no_head:

                if len(HH.occupants) == 0:

                    if (HH.agehrp - person.age_cat) < 3:
                        HH.occupants.append(person)
                        person.HHid = HH.id

                        assigned_persons.append(person)
                        HH_with_head.append(HH)

                        break

                    else:

                        continue

                else:

                    continue

    unassigned_persons = list(set(pop_list) - set(assigned_persons))
    HH_no_head = list(set(HH_list) - set(HH_with_head))

    return HH_with_head, unassigned_persons


def mip_solve(HH_matrix, Ind_matrix):


    HH_hd = np.array(HH_matrix)
    HHs = list(range(len(HH_hd)))
    characteristics = list(range(len(HH_hd[0])))

    I_id_list = Ind_matrix

    hh_slots = cp.Variable(shape=(len(HHs), len(characteristics)), integer=True)


    obj = cp.Minimize(cp.sum_squares(hh_slots))

    # correct function - but too slow for testing on normal pc
    #obj = 0
    #for HH in HHs:
        #obj += cp.Minimize(cp.sum([hh_slots[HH][char]**2 for char in characteristics])**2)

    constraints = []
    for HH in HHs:
        for char in characteristics:
            constraints += [(HH_hd[HH][char] + hh_slots[HH][char]) >= 0]

    #for HH in HHs:
    #    constraints += [sum([hh_slots[HH][char]**2 for char in characteristics]) <= 1]

    constraints += [sum(hh_slots) + sum(HH_hd) == I_id_list]

    prob = cp.Problem(obj, constraints)

    print(prob.solve(solver=cp.GUROBI, verbose=True, timelimit=20))

    print("status:", prob.status)

    solution_list = []
    for v in prob.variables():
        solution_list.append(np.rint(v.value).astype(int))

    solution = solution_list[0]

    return solution


def assign_rem_individuals(HHs_with_head, unassigned_persons):

    filled_HHs = []
    unfilled_HHs = []
    for HH in HHs_with_head:

        if sum(HH.mip) == 0:
            filled_HHs.append(HH)

        else:
            unfilled_HHs.append(HH)

    for person in unassigned_persons:
        for HH in unfilled_HHs:

            if HH.mip[person.age_sex_cat] >= 1:

                HH.occupants.append(person)
                person.HHid = HH.id

                HH.mip[person.age_sex_cat] -= 1

                if sum(HH.mip) == 0:
                    filled_HHs.append(HH)

                    break

                break

            else:

                continue

    return filled_HHs

def run_HH_allocation(lsoa, pop_list):

    HH_list = generate_HHs(lsoa)

    unassigned_persons_and_HHs_with_head = assign_HRP(pop_list, HH_list)

    HHs_with_head = unassigned_persons_and_HHs_with_head[0]
    unassigned_persons = unassigned_persons_and_HHs_with_head[1]

    individual_age_sex_totals = [0]*14
    for person in unassigned_persons:

        if person.sex == 0:
            individual_age_sex_totals[person.age_cat] += 1
        else:
            individual_age_sex_totals[person.age_cat + 7] += 1

    HH_matrix = []
    for HH in HHs_with_head:
        HH_matrix.append(HH.mip.copy())

    mip_solution = mip_solve(HH_matrix, individual_age_sex_totals)

    for index, HH in enumerate(HHs_with_head):
        HH.mip = [sum(x) for x in zip(HH.mip, mip_solution[index])]

    cwd = os.getcwd()
    output_dir = cwd+"/housing_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    adj_HH_list = []
    for house in HHs_with_head:
        adj_HH_list.append([house.id, house.mip, lsoa])

    adj_HH_df = pd.DataFrame(adj_HH_list, columns=['HH_id', 'mip', 'LSOACODE'])
    adj_HH_name = lsoa + "_adjusted_HHs"
    adj_HH_output = outputs.Outputs(adj_HH_name, output_dir=output_dir)
    adj_HH_output.write_file(adj_HH_df)

    lsoa_tag = [lsoa]*len(individual_age_sex_totals)
    individuals_df = pd.DataFrame({'mip': individual_age_sex_totals, 'LSOACODE': lsoa_tag})

    individuals_name = lsoa + "_individuals_mip"
    ind_output = outputs.Outputs(individuals_name, output_dir=output_dir)
    ind_output.write_file(individuals_df)

    if sys.platform=='linux2' or sys.platform=='linux':
        shutil.move(output_dir+"/"+ind_output.file_name, global_vars.PROJ_PATH+"/"+run_name+"/"+ind_output.file_name)
        shutil.move(output_dir+"/"+adj_HH_output.file_name, global_vars.PROJ_PATH+"/"+run_name+"/"+adj_HH_output.file_name)

    filled_HHs = assign_rem_individuals(HHs_with_head, unassigned_persons)
