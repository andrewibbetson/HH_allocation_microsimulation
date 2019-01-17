# -*- coding: utf-8 -*-
import pandas as pd
import re
#import matplotlib.pyplot as plt
import numpy as np
import global_vars

def EHS(lsoa):

    lsoa_region_lookup_df = pd.read_csv(global_vars.PROJ_PATH + r'/data/housing/LSOA_GOR_lookup_2016.csv')
    GOR = lsoa_region_lookup_df.loc[lsoa_region_lookup_df['LSOACODE'] == lsoa, 'REGION_CODE'].iloc[0]
    GOR = int(GOR[-1:])

    if GOR >=3:
        GOR += 1
    else:
        GOR = GOR

    general_df = pd.read_csv(global_vars.PROJ_PATH + r'data/housing/EHS_general_2011.csv')
    general_df = general_df.filter(regex='gorEHS|serialanon')

    interview_vars = 'hhsizex|hhtype7|agehrp6x|sexhrp'
    interview_df = pd.read_csv(global_vars.PROJ_PATH + r'data/housing/EHS_interview_2011.csv')
    interview_df = interview_df.filter(regex= interview_vars + '|serialanon')
    # merge one male / one female / one person (unknown sex)
    interview_df['hhtype7'].replace([7,6], 5,inplace=True)
    # cap hhsize @ 5
    # interview_df['hhsizex'].replace([6, 7, 8], 5, inplace=True)


    # get dwelling type for each house
    # -8 “unknown” / 1 “end terrace” / 2 “mid terrace” / 3 “semi detached” / 4 “detached” / 5 “bungalow” / 6 “converted flat” / 7 “purpose built flat, low rise” / 8 “purpose built flat, high rise”

    physical_var = 'dwtypenx'
    physical_df = pd.read_csv(global_vars.PROJ_PATH + r'data/housing/EHS_physical_2011.csv')
    physical_df = physical_df.filter(regex= physical_var + '|serialanon')

    # merge dwtypes
    # 1 "terrace" / 2 "detached" / 3 "semi" / 4 "flat"
    physical_df['dwtypenx'].replace([1, 2], 1, inplace=True)
    physical_df['dwtypenx'].replace([4, 5], 2, inplace=True)
    physical_df['dwtypenx'].replace([6, 7, 8], 4, inplace=True)

    full_df = pd.merge(general_df, physical_df, on = 'serialanon')
    full_df = pd.merge(full_df, interview_df, on = 'serialanon')

    full_df = full_df.sort_values(by=['gorEHS'])

    full_df = full_df.drop(['serialanon'], axis=1)

    full_df = full_df[full_df > 0].dropna()
    full_df = pd.DataFrame({'total' : full_df.groupby(['gorEHS', physical_var, 'hhsizex', 'hhtype7', 'agehrp6x', 'sexhrp']).size()}).reset_index()

    GOR_df = full_df[full_df['gorEHS'] == GOR]
    GOR_df = GOR_df.drop(['gorEHS'], axis=1)

    return GOR_df


def microdata(marginals, GOR_df):

    #MARGINAL TOTALS

    xipppp = GOR_df.groupby('dwtypenx')['total'].sum()
    xpjppp = GOR_df.groupby('hhsizex')['total'].sum()
    xppkpp = GOR_df.groupby('hhtype7')['total'].sum()
    xppplp = GOR_df.groupby('agehrp6x')['total'].sum()
    xppppm = GOR_df.groupby('sexhrp')['total'].sum()
    # xijppp = GOR7_df.groupby(['dwtypenx', 'hhsizex'])['total'].sum()
    # xipkpp = GOR7_df.groupby(['dwtypenx', 'hhtype7'])['total'].sum()
    # xipplp = GOR7_df.groupby(['dwtypenx', 'agehrp6x'])['total'].sum()
    # xipppm = GOR7_df.groupby(['dwtypenx', 'sexhrp'])['total'].sum()
    # xpjkpp = GOR7_df.groupby(['hhsizex', 'hhtype7'])['total'].sum()
    # xpjplp = GOR7_df.groupby(['hhsizex', 'agehrp6x'])['total'].sum()
    # xpjppm = GOR7_df.groupby(['hhsizex', 'sexhrp'])['total'].sum()
    # xppklp = GOR7_df.groupby(['hhtype7', 'agehrp6x'])['total'].sum()
    # xppkpm = GOR7_df.groupby(['hhtype7', 'sexhrp'])['total'].sum()
    # xppplm = GOR7_df.groupby(['agehrp6x', 'sexhrp'])['total'].sum()
    # xijkpp = GOR7_df.groupby(['dwtypenx', 'hhsizex', 'hhtype7'])['total'].sum()
    # xipklp = GOR7_df.groupby(['dwtypenx', 'hhtype7', 'agehrp6x'])['total'].sum()
    # xipplm = GOR7_df.groupby(['dwtypenx', 'agehrp6x', 'sexhrp'])['total'].sum()
    # xpjklp = GOR7_df.groupby(['hhsizex', 'hhtype7', 'agehrp6x'])['total'].sum()
    # xpjplm = GOR7_df.groupby(['hhsizex', 'agehrp6x', 'sexhrp'])['total'].sum()
    # xppklm = GOR7_df.groupby(['hhtype7', 'agehrp6x', 'sexhrp'])['total'].sum()
    # xijklp = GOR7_df.groupby(['dwtypenx', 'hhsizex', 'hhtype7', 'agehrp6x'])['total'].sum()
    # xipklm = GOR7_df.groupby(['dwtypenx', 'hhtype7', 'agehrp6x', 'sexhrp'])['total'].sum()
    # xijplm = GOR7_df.groupby(['dwtypenx', 'hhsizex', 'agehrp6x', 'sexhrp'])['total'].sum()
    # xijkpm = GOR7_df.groupby(['dwtypenx', 'hhsizex', 'hhtype7', 'sexhrp'])['total'].sum()
    # xpjklm = GOR7_df.groupby(['hhsizex', 'hhtype7', 'agehrp6x', 'sexhrp'])['total'].sum()

    # marginals = [xipppp, xpjppp, xppkpp, xppplp, xppppm, xijppp, xipkpp, xipplp, xipppm, xpjkpp, xpjplp, xpjppm, xppklp,
    #     xppkpm, xppplm, xijkpp, xipklp, xipplm, xpjklp, xpjplm, xppklm, xijklp, xipklm, xijplm, xijkpm, xpjklm]

    xipppp.loc[1] = int(marginals.loc['dwtype_1'].values[0])
    xipppp.loc[2] = int(marginals.loc['dwtype_2'].values[0])
    xipppp.loc[3] = int(marginals.loc['dwtype_3'].values[0])
    xipppp.loc[4] = int(marginals.loc['dwtype_4'].values[0])

    xpjppp.loc[1] = int(marginals.loc['hhsize_1'].values[0])
    xpjppp.loc[2] = int(marginals.loc['hhsize_2'].values[0])
    xpjppp.loc[3] = int(marginals.loc['hhsize_3'].values[0])
    xpjppp.loc[4] = int(marginals.loc['hhsize_4'].values[0])
    xpjppp.loc[5] = int(marginals.loc['hhsize_5'].values[0])
    xpjppp.loc[6] = int(marginals.loc['hhsize_6'].values[0])
    xpjppp.loc[7] = int(marginals.loc['hhsize_7'].values[0])
    xpjppp.loc[8] = int(marginals.loc['hhsize_8'].values[0])

    xppkpp.loc[1] = int(marginals.loc['hhtype_1'].values[0])
    xppkpp.loc[2] = int(marginals.loc['hhtype_2'].values[0])
    xppkpp.loc[3] = int(marginals.loc['hhtype_3'].values[0])
    xppkpp.loc[4] = int(marginals.loc['hhtype_4'].values[0])
    xppkpp.loc[5] = int(marginals.loc['hhtype_5'].values[0])

    xppplp.loc[1] = int(marginals.loc['16-24'].values[0])
    xppplp.loc[2] = int(marginals.loc['25-34'].values[0])
    xppplp.loc[3] = int(marginals.loc['35-44'].values[0])
    xppplp.loc[4] = int(marginals.loc['45-54'].values[0])
    xppplp.loc[5] = int(marginals.loc['55-64'].values[0])
    xppplp.loc[6] = int(marginals.loc['65+'].values[0])

    xppppm.loc[1] = int(marginals.loc['m'].values[0])
    xppppm.loc[2] = int(marginals.loc['f'].values[0])


    aggregates = [xipppp, xpjppp, xppkpp, xppplp, xppppm]
    dimensions = [['dwtypenx'], ['hhsizex'], ['hhtype7'], ['agehrp6x'], ['sexhrp']]

    return aggregates, dimensions


def scatter_plot(original_df, df_list, aggregates):

    df_list.insert(0, original_df)

    o_xipppp_values = []
    o_xpjppp_values = []
    o_xppkpp_values = []
    o_xppplp_values = []
    o_xppppm_values = []
    for df in df_list:

        o_xipppp = df.groupby('dwtypenx')['total'].sum()
        o_xpjppp = df.groupby('hhsizex')['total'].sum()
        o_xppkpp = df.groupby('hhtype7')['total'].sum()
        o_xppplp = df.groupby('agehrp6x')['total'].sum()
        o_xppppm = df.groupby('sexhrp')['total'].sum()

        o_xipppp_values.append(list(o_xipppp.values))
        o_xpjppp_values.append(list(o_xpjppp.values))
        o_xppkpp_values.append(list(o_xppkpp.values))
        o_xppplp_values.append(list(o_xppplp.values))
        o_xppppm_values.append(list(o_xppppm.values))

    zipped_list_i = []
    for lst in o_xipppp_values:
        zipped_xipppp = list(zip(lst, aggregates[0]))
        zipped_list_i.append(zipped_xipppp)

    zipped_list_j = []
    for lst in o_xpjppp_values:
        zipped_xpjppp = list(zip(lst, aggregates[1]))
        zipped_list_j.append(zipped_xpjppp)

    zipped_list_k = []
    for lst in o_xppkpp_values:
        zipped_xppkpp = list(zip(lst, aggregates[2]))
        zipped_list_k.append(zipped_xppkpp)

    zipped_list_l = []
    for lst in o_xppplp_values:
        zipped_xppplp = list(zip(lst, aggregates[3]))
        zipped_list_l.append(zipped_xppplp)

    zipped_list_m = []
    for lst in o_xppppm_values:
        zipped_xppppm = list(zip(lst, aggregates[4]))
        zipped_list_m.append(zipped_xppppm)

    i = []
    j = []
    k = []
    l = []
    m = []

    for iteration in range(len(zipped_list_i)):
        no_iterations_i = zipped_list_i[iteration]
        no_iterations_j = zipped_list_j[iteration]
        no_iterations_k = zipped_list_k[iteration]
        no_iterations_l = zipped_list_l[iteration]
        no_iterations_m = zipped_list_m[iteration]

        xi, yi = zip(*no_iterations_i)
        xj, yj = zip(*no_iterations_j)
        xk, yk = zip(*no_iterations_k)
        xl, yl = zip(*no_iterations_l)
        xm, ym = zip(*no_iterations_m)

        i.append([xi, yi])
        j.append([xj, yj])
        k.append([xk, yk])
        l.append([xl, yl])
        m.append([xm, ym])

    return i, j, k, l, m
