import pandas as pd
import numpy as np
import global_vars

def calc_census_marginal_totals(region_sel):

    age_df = pd.read_csv(global_vars.PROJ_PATH + "/data/housing/LSOA_age_HRP_2011_interpolated.csv").set_index('LSOACODE')
    region_age_df = age_df.loc[region_sel]

    hhsize_df = pd.read_csv(global_vars.PROJ_PATH + "/data/housing/LSOA_hhsize_2011.csv").set_index('LSOACODE')
    region_hhsize_df = hhsize_df.loc[region_sel]

    sex_df = pd.read_csv(global_vars.PROJ_PATH + "/data/housing/LSOA_sex2_2011.csv").set_index('LSOACODE')
    region_sex_df = sex_df.loc[region_sel]

    hhtype_df = pd.read_csv(global_vars.PROJ_PATH + "/data/housing/LSOA_hhtype_2011.csv").set_index('LSOACODE')
    region_hhtype_df = hhtype_df.loc[region_sel]

    dwtype_df = pd.read_csv(global_vars.PROJ_PATH + "/data/housing/LSOA_dwtype_2011.csv").set_index('LSOACODE')
    region_dwtype_df = dwtype_df.loc[region_sel]

    scale_factor = (region_dwtype_df.sum() / region_sex_df.sum())

    region_sex_df = (region_sex_df*scale_factor)

    sex_new_df = TRS(region_sex_df)

    marginals_df = pd.concat([pd.DataFrame(data={region_sel: region_dwtype_df.values}, index=region_dwtype_df.index), pd.DataFrame(data={region_sel: region_hhtype_df.values}, index=region_hhtype_df.index), pd.DataFrame(data={region_sel: region_hhsize_df.values}, index=region_hhsize_df.index), pd.DataFrame(data={region_sel: region_age_df.values}, index=region_age_df.index), sex_new_df])

    return marginals_df

def TRS(df):

    rd_df = df.apply(np.floor)
    dec_df = df - rd_df

    diff =  df.sum() - rd_df.sum()
    dec_df = dec_df.transpose()
    sampled = dec_df.sample(int(diff), weights=dec_df, random_state=1)

    sampled = sampled.transpose()
    sampled = np.ceil(sampled)

    new_df = pd.concat([rd_df, sampled], axis=1)
    new_df = new_df.groupby(new_df.columns, axis=1).sum()

    return new_df
