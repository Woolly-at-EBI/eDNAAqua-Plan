#!/usr/bin/env python3
"""Script of get_environmental_info.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2024-05-09
__docformat___ = 'reStructuredText'
chmod a+x get_taxononomy_scientific_name.py
"""

import requests
import xml.etree.ElementTree as ET

from icecream import ic
import os
import argparse
import sys
import json
import pickle
import time
import pandas as pd

def get_query_params():
    my_params = {
        "srv": "https://www.ebi.ac.uk/ena/portal/api/search",
        "query": '(environmental_sample%3Dtrue%20OR%20(CHECKLIST%3D%22ERC000012%22%20OR%20CHECKLIST%3D%22ERC000020%22%20OR%20CHECKLIST%3D%22ERC000021%22%20OR%20CHECKLIST%3D%22ERC000022%22%20OR%20CHECKLIST%3D%22ERC000023%22%20OR%20CHECKLIST%3D%22ERC000024%22%20OR%20CHECKLIST%3D%22ERC000025%22%20OR%20CHECKLIST%3D%22ERC000027%22%20OR%20CHECKLIST%3D%22ERC000055%22%20OR%20CHECKLIST%3D%22ERC000030%22%20OR%20CHECKLIST%3D%22ERC000031%22%20OR%20CHECKLIST%3D%22ERC000036%22))%20AND%20not_tax_tree(9606)'
    }
    return my_params

def run_webservice(url):
    r = requests.get(url)

    if r.status_code == 200:
        return r.text
    else:
        ic.enable()
        ic(r.status_code)
        ic(f"for url={r.url}")
        ic("retrying in 5 seconds, once")
        time.sleep(5)
        if r.status_code == 200:
            ic.disable()
            return r.text
        else:
            ic(f"Still {r.status_code} so exiting")
        ic.disable()
        sys.exit(1)


def extract_record_ids_from_json(id_field_name, json_blob):
    # print(json.dumps(json_blob, indent=4))
    record_list = []
    for record in json_blob:
        # ic(record)
        record_list.append(record[id_field_name])
    return record_list

def pickle_data_structure(data_structure, filename):
    try:
        with open(filename, "wb") as f:
            pickle.dump(data_structure, f, protocol = pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)

def unpickle_data_structure(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)

def get_env_readrun_ids():
    env_read_run_id_file = "read_run.pickle"
    if os.path.exists(env_read_run_id_file):
        ic("env_read_run_id_file exists, so can unpickle it")
        return unpickle_data_structure(env_read_run_id_file)

    query_params_json = get_query_params()
    srv = query_params_json['srv']
    params = "result=read_run&query=" + query_params_json['query'] + "&format=json"
    limit = '&limit=5'
    url = srv + '?' + params + limit
    ic(url)
    output = json.loads(run_webservice(url))
    ic(output)
    record_list = extract_record_ids_from_json('run_accession', output)
    ic(len(record_list))
    pickle_data_structure(record_list, env_read_run_id_file)
    return record_list

def get_env_readrun_detail():
    env_read_run_detail_file = "read_run_detail.pickle"
    if os.path.exists(env_read_run_detail_file):
        ic(f"{env_read_run_detail_file} exists, so can unpickle it")
        return unpickle_data_structure(env_read_run_detail_file)

    fields = "sample_accession%2Crun_accession%2Clibrary_strategy%2Clibrary_source%2Clat%2Clon%2Ccountry%2Cbroad_scale_environmental_context%2Ctax_id%2Cchecklist%2Ccollection_date%2Ctarget_gene"

    query_params_json = get_query_params()
    srv = query_params_json['srv']
    params = "result=read_run&query=" + query_params_json['query'] + "&fields=" + fields + "&format=json"
    limit = '&limit=0'
    url = srv + '?' + params + limit
    ic(url)

    output = json.loads(run_webservice(url))
    # sys.exit()
    # ic(output)
    # record_list = extract_record_ids_from_json('run_accession', output)
    # ic(len(record_list))
    ic(len(output))
    pickle_data_structure(output, env_read_run_detail_file)
    return output


def get_env_sample_ids():
    env_sample_id_file = "env_sample_id_file.pickle"
    if os.path.exists(env_sample_id_file):
        ic("env_sample_id_file exists, so can unpickle it")
        return unpickle_data_structure(env_sample_id_file)

    query_params_json = get_query_params()
    srv = query_params_json['srv']
    params = "result=sample&query=" + query_params_json['query'] + "&format=json"
    limit = '&limit=5'
    url = srv + '?' + params + limit
    ic(url)
    output = json.loads(run_webservice(url))
    ic(output)
    record_list = extract_record_ids_from_json('sample_accession', output)
    ic(record_list)
    pickle_data_structure(record_list, env_sample_id_file)
    return record_list

def analyse_readrun_detail(env_readrun_detail):
    ic(len(env_readrun_detail))
    # count = 0
    # for record in env_readrun_detail:
    #
    #     ic(record)
    #     count = count + 1
    #     if count > 3:
    #         break

    df = pd.DataFrame.from_records(env_readrun_detail)
    ic(df.dtypes)
    df['lat'] = pd.to_numeric(df['lat'], errors = 'coerce')

    # df[['lat', 'lon']] = df[['lat', 'lon']].apply(pd.to_numeric, errors='ignore')

    ic(df.dtypes)

    ic(df['lat'])
    # sys.exit()
    null_rows = df.query('lat != lat')
    df['has_geographical_coordinates'] = True
    df['has_geographical_coordinates'] = df['has_geographical_coordinates'].mask(df['lat'].isna(), False)
    df['has_geographical_coordinates'] = df['has_geographical_coordinates'].mask(df['lon'].isna(), False)
    ic(df['has_geographical_coordinates'].value_counts())
    df['has_broad_scale_environmental_context'] = True
    df['has_broad_scale_environmental_context'] = df['has_broad_scale_environmental_context'].mask(df['broad_scale_environmental_context'] == '', False)
    print(df.info())
    ic(df.head())
    ic(df['has_broad_scale_environmental_context'])
    ic(df['has_broad_scale_environmental_context'].value_counts())
    ic(df['broad_scale_environmental_context'].value_counts())


def main(args):
    sample_ids = get_env_sample_ids()
    ic(len(sample_ids))
    readrun_ids = get_env_readrun_ids()
    ic(len(readrun_ids))
    env_readrun_detail = get_env_readrun_detail()
    analyse_readrun_detail(env_readrun_detail)


if __name__ == '__main__':
    # Read arguments from command line
    prog_des = "Script to "

    parser = argparse.ArgumentParser(description = prog_des)

    # Adding optional argument, n.b. in debugging mode in IDE, had to turn required to false.
    parser.add_argument("-d", "--debug_status",
                        help = "Debug status i.e.True if selected, is verbose",
                        required = False, action = "store_true")

    parser.parse_args()
    args = parser.parse_args()

    if args.debug_status:
        ic.enable()
    else:
        ic.disable()
    ic(prog_des)

    main(args)
