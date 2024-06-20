#!/usr/bin/env python3
"""Script of mine_bioinfomatics_eval.py is to mine the bioinfomatics evaluation spreadsheet file

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2024-06-18
__docformat___ = 'reStructuredText'

"""


import pandas as pd
import sys
import logging
from collections import Counter
from eDNA_utilities import logger,  my_coloredFormatter, coloredlogs

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



def get_dataframe():
    ss_url = r'https://docs.google.com/spreadsheets/d/1bll3zzMJHv0gbe2xH4h7a9wTCMy3INtV/edit?usp=sharing&ouid=112917721394157806879&rtpof=true&sd=true'
    sheet_id = '1bll3zzMJHv0gbe2xH4h7a9wTCMy3INtV'
    ss_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv'
    ss_url = 'eDNA_Survey-Data.xlsx'
    logger.info(f'Mined questionnaire evaluation spreadsheet: {ss_url}')
    # df = pd.read_csv(ss_url)
    df = pd.read_excel(ss_url)

    col_list = list(df.columns)
    logger.info(f"\n{col_list}")

    def filter_not_raw(value):

        if value.startswith("Raw") or value == "NoRaw":
            return False
        else:
            return True

    logger.info("-------------------------------------------")
    logger.info(f"len of col_list={len(col_list)}")
    not_raw_list = list(filter(filter_not_raw, col_list))
    logger.info(f"\n{not_raw_list}")
    df = df[not_raw_list]

    return df

def un_split_list(list):

    clean_list = []
    for item in list:
        if item != item:
            continue
        item = item.strip().replace('[', '').replace(']', '')
        local_list = item.split(';')
        clean_list.extend(local_list)
    return clean_list

def get_duplicates_in_list(mylist):
    newlist = []  # empty list to hold unique elements from the list
    duplist = []  # empty list to hold the duplicate elements from the list
    for i in mylist:
        if i not in newlist:
            newlist.append(i)
        else:
            duplist.append(i)
    return sorted(set(duplist))


def get_lists_from_df_column(df, col):
    my_list = df[col].to_list()
    # logger.info(f"\n{my_list}")
    my_list = un_split_list(my_list)
    # logger.info(f"\n{my_list}")
    print(f"Total of {len(my_list)} in col={col} , unique count= {len(set(my_list))}")
    duplist = get_duplicates_in_list(my_list)
    print(f"\nDuplicated {col} list:  {duplist}")
    print(Counter(my_list))
    return my_list

def analyse_projects(df):
    project_list = get_lists_from_df_column(df,'Project')
    print(Counter(project_list))

def analyse_location(df):
    location_list = get_lists_from_df_column(df, 'Location')

def analyse_europe(df):
    location_list = get_lists_from_df_column(df, 'Europe')


def mine_questionnaire_eval():
    """"""
    df = get_dataframe()
    row_vals_2_drop = ['[NO ANSWER]']
    df = df[~df.Project.isin(row_vals_2_drop)]
    logger.info(f"\n{list(df.columns)}")
    proj_list = df['Project'].to_list()
    proj_list = un_split_list(proj_list)
    print(f"This many questionnaire evaluations were done: {len(df)} covering {len(proj_list)} projects")
    # analyse_projects(df)
    # analyse_location(df)
    analyse_europe(df)






def main():
    print("FFS")
    mine_questionnaire_eval()

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)

    coloredlogs.install(logger = logger)
    logger.propagate = False
    ch = logging.StreamHandler(stream = sys.stdout)
    ch.setFormatter(fmt = my_coloredFormatter)
    logger.addHandler(hdlr = ch)
    logger.setLevel(level = logging.INFO)


    main()
