#!/usr/bin/env python3
"""Script of get_environmental_info.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2024-05-09
__docformat___ = 'reStructuredText'
chmod a+x get_taxononomy_scientific_name.py
"""

import json
import pickle
import re
import sys
import time

import pandas as pd
import requests

from geography import Geography
from taxonomy import *


pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)


def get_query_params():
    my_params = {
        "srv": "https://www.ebi.ac.uk/ena/portal/api/search",
        "query": '(environmental_sample%3Dtrue%20OR%20(CHECKLIST%3D%22ERC000012%22%20OR%20CHECKLIST%3D%22ERC000020%22'
                 '%20OR%20CHECKLIST%3D%22ERC000021%22%20OR%20CHECKLIST%3D%22ERC000022%22%20OR%20CHECKLIST%3D'
                 '%22ERC000023%22%20OR%20CHECKLIST%3D%22ERC000024%22%20OR%20CHECKLIST%3D%22ERC000025%22%20OR'
                 '%20CHECKLIST%3D%22ERC000027%22%20OR%20CHECKLIST%3D%22ERC000055%22%20OR%20CHECKLIST%3D%22ERC000030'
                 '%22%20OR%20CHECKLIST%3D%22ERC000031%22%20OR%20CHECKLIST%3D%22ERC000036%22))%20AND%20not_tax_tree('
                 '9606)'
    }
    return my_params


def run_webservice(url):
    """

    :param url:
    :return:
    """
    r = requests.get(url)
    ic(r.url)

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

    fields = ("sample_accession%2Crun_accession%2Clibrary_strategy%2Clibrary_source%2Clat%2Clon%2Ccountry"
              "%2Cbroad_scale_environmental_context%2Ctax_id%2Cchecklist%2Ccollection_date%2Ctarget_gene%2Ctag")

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


def select_first_part(value):
    """
    select just the first part of value before the :
    :param value:
    :return:
    """

    my_list = value.split(":")
    if len(my_list[0]) > 0:
        return my_list[0]
    else:
        return "missing"

    # #ic(value[:value.find(":")])
    # if value.find(":") >= 0:
    #     return value[:value.find(":")+1]
    # else:
    #     return value

def print_value_count_table(df_var):
    counts = df_var.value_counts()
    percs = df_var.value_counts(normalize = True)
    tmp_df = pd.concat([counts, percs], axis = 1, keys = ['count', 'percentage'])
    tmp_df['percentage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in tmp_df['percentage']], index = tmp_df.index)
    print(tmp_df)


def do_geographical(df):
    df['has_geographical_coordinates'] = True
    df['has_geographical_coordinates'] = df['has_geographical_coordinates'].mask(df['lat'].isna(), False)
    print_value_count_table(df.has_geographical_coordinates)

    df['has_broad_scale_environmental_context'] = True
    df['has_broad_scale_environmental_context'] = df['has_broad_scale_environmental_context'].mask(
        df['broad_scale_environmental_context'] == '', False)

    print_value_count_table(df.has_broad_scale_environmental_context)
    print_value_count_table(df.broad_scale_environmental_context)

    df['country_clean'] = df['country'].apply(select_first_part)
    print_value_count_table(df.country_clean)
    ic(df['country'].value_counts())
    ic("About to call geographical")
    geography_obj = Geography()
    df['continent'] = df['country_clean'].apply(geography_obj.get_continent)
    print_value_count_table(df.continent)

    df['ocean'] = df['country_clean'].apply(geography_obj.get_ocean)
    tmp_df = df[df['ocean'] != 'not ocean']
    print_value_count_table(tmp_df.ocean)
    return df


def collection_date_year(value):
    if value == "":
        return ""
    elif re.search("^missing|^not", value):
        return ""
    elif re.search("^[0-9]{4}$", value):
        return value
    elif re.search("^[0-9]{4}[-/]", value):
        return value[0:4]
    elif re.search("^[0-9]{2}/[0-9]{2}/[0-9]{4}", value):
        return value.split("/")[2]
    elif re.search("[0-9]{4}$", value):
        return value[:-4]
    elif re.search("^[0-9]{4}$", value):
        return re.findall("^[0-9]{4}", value)[0]
    elif re.search("[0-2][0-9]$", value):
        extract_value = int(value[-2:])
        if extract_value > 50:
            return '19' + str(extract_value)
        else:
            return '20' + str(extract_value)
    else:
        ic(f"no year match for {value}")
        return ""

def create_year_bins(value):
    """
    trying to bin years in 5 year
    :param value:
    :return:
    """
    min=1950
    max=2025
    if isinstance(value, int):
        if value <= min:
            return str(min) + "-pre"
        for x in range(min, max, 5):
            # 2023 far more likely than min so could try reversing the order
            # ic(value)
            if value <= x:
               return f"{str(x)}-{str(x+5)}"
    return None




def experimental_analysis_inc_filtering(df):
    ic(df.columns)

    ic("before filtering")
    print_value_count_table(df.library_source)
    print_value_count_table(df.library_strategy)

    strategy_list_to_keep = ['AMPLICON', 'WGS', 'RNA-Seq', 'WGA', 'Targeted-Capture', 'ssRNA-seq', 'miRNA-Seq']
    ic(strategy_list_to_keep)
    df = df.loc[df['library_strategy'].isin(strategy_list_to_keep)]
    ic("after filtering")

    print_value_count_table(df.library_source)
    print_value_count_table(df.library_strategy)

    ic(df['library_strategy'].value_counts())
    print_value_count_table(df.library_source)
    ic(df.groupby(['library_source', 'library_strategy']).size())
    ic(df.groupby(['library_source', 'library_strategy']).size().reset_index())
    print(df.groupby(['library_source', 'library_strategy']).size().reset_index().to_string(index=False))
    ic(df.columns)

    return df


def target_gene_analysis(df):
    ic(df['target_gene'].value_counts().head())


def analyse_environment(df):
    """
    needs to be called after taxonomic_analysis
    :param df:
    :return:
    """
    def process_env_tags(value):
        my_tag_list = value.split(';')

        my_env_tags = [s for s in my_tag_list if "env_" in s]

        return my_env_tags
    print_value_count_table(df.tag)
    ic(df.tag.head(50))
    #df['env_tax'] = df['tag'].str.extract("(env_tax:[^;]*)")[0]
    df['env_tag'] = df['tag'].apply(process_env_tags)
    df['env_tags'] = df['env_tag'].apply(lambda x: ';'.join(x))
    ic(df['env_tag'].value_counts().head(5))
    tmp_df = df[df.env_tag.str.len() > 0]
    # print_value_count_table(tmp_df.env_tag)

    ic(tmp_df['env_tag'].value_counts().head(5))
    ic(tmp_df['env_tag'].explode().unique())


    tmp_df['env_tag_string'] = tmp_df['env_tag'].str.join(';')
    ic(tmp_df['env_tag_string'].unique())
    # ic(my_env_lists['env_tag'])
    #  for tag in tmp_df['env_tag'].unique():
    #      ic(tag)

    tag_string_assignment = {}
    # f = tmp_df['env_tag_string'].str.contains("env_geo",na=False)
    # sys.exit()

    not_assigned = []
    for tags in tmp_df['env_tag_string'].unique():
        tag_list = tags.split(';')
        # ic(tags)
        # ic(tag_list)

        if 'env_geo' in tags:
            # ic(f"----------------------{tags}")
            matches = re.findall(r'env_geo[^;]*', tags)
            # ic(matches)
            if len(matches) > 1:
                ic(f"matches={matches}, tags={tags}")
                # sys.exit()
            else:
                if matches[0] == 'env_geo:marine' and 'env_tax:marine' in tags:
                    tag_string_assignment[tags] = "marine"
                elif matches[0] == 'env_geo:freshwater' and 'env_geo:freshwater' in tags:
                    tag_string_assignment[tags] = "freshwater"
                elif matches[0] == 'env_geo:coastal' and 'env_geo:coastal' in tags:
                    tag_string_assignment[tags] = "coastal"
                elif matches[0] == 'env_geo:brackish' and 'env_geo:brackish' in tags:
                    tag_string_assignment[tags] = "brackish"
                elif matches[0] == 'env_geo:terrestrial' and 'env_geo:terrestrial' in tags:
                    tag_string_assignment[tags] = "terrestrial"
                else:
                    #ic(f"Not assigned: {tags}")
                    not_assigned.append(tags)

            if 'env_tax:marine' in tag_list and 'env_geo:marine' in tag_list:
                tag_string_assignment[tags] = "marine"
    ic(tag_string_assignment)
    ic(not_assigned)

    ic('env_tax:freshwater;env_tax:terrestrial;env_geo:marine')
    tmp_df = df[df['env_tags'].str.contains('env_tax:freshwater;env_tax:terrestrial;env_geo:marine')]
    ic(tmp_df['sample_accession'].unique())

    ic(('env_tax:freshwater;env_geo:marine'))
    tmp_df = df.query('env_tags == "env_tax:freshwater;env_geo:marine"')
    ic(len(tmp_df['sample_accession'].unique()))
    ic(tmp_df['sample_accession'].unique())
    ic(tmp_df['tax_id'].unique())
    ic(tmp_df['scientific_name'].unique())


def taxonomic_analysis(df):

    tax_id_list = df['tax_id'].unique()
    def lineage_lookup(value):
        # ic(taxonomy_hash_by_tax_id[value])
        return taxonomy_hash_by_tax_id[value]['lineage']

    def tax_lineage_lookup(value):
        # ic(taxonomy_hash_by_tax_id[value])
        return taxonomy_hash_by_tax_id[value]['tax_lineage']

    def scientific_name_lookup(value):
        # ic(taxonomy_hash_by_tax_id[value])
        return taxonomy_hash_by_tax_id[value]['scientific_name']





    taxonomy_hash_by_tax_id = create_taxonomy_hash_by_tax_id(tax_id_list)



    # ic(taxonomy_hash_by_tax_id)


    print_value_count_table(df)

    df['scientific_name'] = df['tax_id'].apply(scientific_name_lookup)
    print_value_count_table(df.scientific_name)

    df['lineage'] = df['tax_id'].apply(lineage_lookup)
    # ic(df['lineage'].value_counts())
    print_value_count_table(df.lineage)
    df['tax_lineage'] = df['tax_id'].apply(tax_lineage_lookup)

    df['lineage_3'] = df['lineage'].str.extract("^[^;]*;([^;]*);")[0]
    ic(df['lineage_3'].value_counts())
    print_value_count_table(df.lineage_3)
    df['lineage_minus2'] = df['lineage'].str.extract("([^;]*);[^;]*$")[0]
    print_value_count_table(df.lineage_minus2)

    ic(df['tax_id'].value_counts())
    tax_id_list = df['tax_id'].unique()
    ic(len(tax_id_list))

    analyse_environment(df)

    sys.exit()

    return df

def clean_dates_in_df(df):
    df['collection_year'] = df['collection_date'].apply(collection_date_year)
    df['collection_year'] = pd.to_numeric(df['collection_year'], errors = 'coerce').astype('Int64')
    df = df.sort_values(by = ['collection_date'])
    df['collection_year_bin'] = df['collection_year'].apply(create_year_bins)

    return df



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
    df = clean_dates_in_df(df)

    df['lat'] = pd.to_numeric(df['lat'], errors = 'coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors = 'coerce')



    df = experimental_analysis_inc_filtering(df)
    print_value_count_table(df.collection_year)
    print_value_count_table(df.collection_year_bin)

    df = do_geographical(df)



    df = taxonomic_analysis(df)
    ic(df)
    ic(df.dtypes)


def main():
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

    main()
