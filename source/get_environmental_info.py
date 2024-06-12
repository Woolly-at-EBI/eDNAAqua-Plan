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
import plotly.express as px
import plotly.graph_objects as go
import logging
import coloredlogs

from collections import Counter

from geography import Geography
from taxonomy import *


pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)


my_coloredFormatter = coloredlogs.ColoredFormatter(
    fmt='[%(name)s] %(asctime)s %(funcName)s %(lineno)-3d  %(message)s',
    level_styles=dict(
        debug=dict(color='white'),
        info=dict(color='green'),
        warning=dict(color='yellow', bright=True),
        error=dict(color='red', bold=True, bright=True),
        critical=dict(color='black', bold=True, background='red'),
    ),
    field_styles=dict(
        name=dict(color='white'),
        asctime=dict(color='white'),
        funcName=dict(color='white'),
        lineno=dict(color='white'),
    )
)


def get_query_params(checklist_type):
    my_params = {
        "srv": "https://www.ebi.ac.uk/ena/portal/api/search",
        "query": ""
    }


    # see  https://www.ebi.ac.uk/ena/browser/checklists

    if checklist_type == "environmental_checklists":
        my_params['query'] = """(environmental_sample%3Dtrue%20OR%20(CHECKLIST%3D%22ERC000012%22%20OR%20CHECKLIST%3D%22ERC000020%22\
                 %20OR%20CHECKLIST%3D%22ERC000021%22%20OR%20CHECKLIST%3D%22ERC000022%22%20OR%20CHECKLIST%3D\
                 %22ERC000023%22%20OR%20CHECKLIST%3D%22ERC000024%22%20OR%20CHECKLIST%3D%22ERC000025%22%20OR\
                 %20CHECKLIST%3D%22ERC000027%22%20OR%20CHECKLIST%3D%22ERC000055%22%20OR%20CHECKLIST%3D%22ERC000030\
                 %22%20OR%20CHECKLIST%3D%22ERC000031%22%20OR%20CHECKLIST%3D%22ERC000036%22)%20OR\
                 (ncbi_reporting_standard%3D%22*ENV*%22%20ORncbi_reporting_standard%3D%22*WATER*%22\
                 %20ORncbi_reporting_standard%3D%22*SOIL*%22%20ORncbi_reporting_standard%3D%22*AIR*%22\
                 %20ORncbi_reporting_standard%3D%22*SEDIMENT*%22%20ORncbi_reporting_standard%3D%22*BUILT%22%20))\
                 AND%20not_tax_tree(9606)"""
    elif checklist_type == "default_checklists":

        # 'result=read_experiment&query=not_tax_eq(9606)%20AND%20(ncbi_reporting_standard%3D%22generic%22%20OR%20(%20checklist%3D%22erc000011%22%20OR%20ncbi_reporting_standard%3D%22generic%22%20))&fields=experiment_accession%2Cexperiment_title%2Ctax_id%2Cncbi_reporting_standard&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search"
        my_params['query'] = """not_tax_eq(9606)%20AND%20(ncbi_reporting_standard%3D%22generic%22%20OR%20(%20checklist%3D%22\
                 erc000011%22%20OR%20ncbi_reporting_standard%3D%22generic%22%20))"""
    else:
        logger.error(f"unknown {checklist_type}")
        sys.exit(-1)


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

    query_params_json = get_query_params("environmental_checklists")
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
    """
curl -X 'POST' \
  'https://www.ebi.ac.uk/ena/portal/api/search' \
  -H 'accept: */*' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'excludeAccessionType=&download=false&query=(environmental_sample%253Dtrue%2520OR%2520(CHECKLIST%253D%2522ERC000012%2522%2520OR%2520CHECKLIST%253D%2522ERC000020%2522%2520OR%2520CHECKLIST%253D%2522ERC000021%2522%2520OR%2520CHECKLIST%253D%2522ERC000022%2522%2520OR%2520CHECKLIST%253D%2522ERC000023%2522%2520OR%2520CHECKLIST%253D%2522ERC000024%2522%2520OR%2520CHECKLIST%253D%2522ERC000025%2522%2520OR%2520CHECKLIST%253D%2522ERC000027%2522%2520OR%2520CHECKLIST%253D%2522ERC000055%2522%2520OR%2520CHECKLIST%253D%2522ERC000030%2522%2520OR%2520CHECKLIST%253D%2522ERC000031%2522%2520OR%2520CHECKLIST%253D%2522ERC000036%2522)%2520OR(ncbi_reporting_standard%253D%2522*ENV*%2522%2520ORncbi_reporting_standard%253D%2522*WATER*%2522%2520ORncbi_reporting_standard%253D%2522*SOIL*%2522%2520ORncbi_reporting_standard%253D%2522*AIR*%2522%2520ORncbi_reporting_standard%253D%2522*SEDIMENT*%2522%2520ORncbi_reporting_standard%253D%2522*BUILT%2522%2520))AND%2520not_tax_tree(9606)&excludeAccessions=&includeMetagenomes=false&dataPortal=&includeAccessionType=&includeAccessions=&format=json&fields=sample_accession%252Crun_accession%252Clibrary_strategy%252Clibrary_source%252Cinstrument_platform%252Clat%252Clon%252Ccountry%252Cbroad_scale_environmental_context%252Ctax_id%252Cchecklist%252Ccollection_date%252Cncbi_reporting_standard%252Ctarget_gene%252Ctag%252Cstudy_accession%252Cstudy_title&dccDataOnly=false&&rule=&result=read_run&limit=0' > all.json
    :return: records list

    # This is for the default_checklist
    ## curl 'https://www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=not_tax_eq(9606)%20AND%20(ncbi_reporting_standard%3D%22generic%22%20OR%20(%20checklist%3D%22erc000011%22%20OR%20ncbi_reporting_standard%3D%22generic%22%20))&fields=sample_accession%2Crun_accession%2Clibrary_strategy%2Clibrary_source%2Cinstrument_platform%2Clat%2Clon%2Ccountry%2Cbroad_scale_environmental_context%2Ctax_id%2Cchecklist%2Ccollection_date%2Cncbi_reporting_standard%2Ctarget_gene%2Ctag%2Cstudy_accession%2Cstudy_title&format=json&limit=0' > default.json
    """
    logger.info("get_env_readrun_detail")


    def setup_run_api_call(query_params_json):
        out_fields = (
            "sample_accession%2Crun_accession%2Clibrary_strategy%2Clibrary_source%2Cinstrument_platform%2Clat%2Clon%2Ccountry"
            "%2Cbroad_scale_environmental_context%2Ctax_id%2Cchecklist%2Ccollection_date%2Cncbi_reporting_standard%2Ctarget_gene%2Ctag%2Cstudy_accession%2Cstudy_title")


        srv = query_params_json['srv']
        params = "result=read_run&query=" + query_params_json['query'] + "&fields=" + out_fields + "&format=json"
        limit = '&limit=5'
        url = srv + '?' + params + limit
        logger.info(url)

        output = json.loads(run_webservice(url))
        # sys.exit()
        # ic(output)
        # record_list = extract_record_ids_from_json('run_accession', output)
        # ic(len(record_list))
        logger.info(len(output))
        return output

    checklist_types = ["environmental_checklists", "default_checklists"]
    checklist_types = ["default_checklists"]
    #checklist_types = ["environmental_checklists"]
    for checklist_type in checklist_types:
        logger.info(f"Doing the main search of environmental data via {checklist_type}")
        if checklist_type == "default_checklists":
            env_read_run_detail_file = "read_run_allinsdc_defaultgeneric.json.pickle"
            env_read_run_detail_jsonfile = "read_run_allinsdc_defaultgeneric.json"
        else:
            env_read_run_detail_file = "read_run_ena_detail.pickle"
            env_read_run_detail_file = "read_run_allinsdc_detail.pickle"
            env_read_run_detail_jsonfile = "read_run_allinsdc_detail.json"


        if os.path.exists(env_read_run_detail_file):
             logger.info(f"{env_read_run_detail_file} exists, so can unpickle it")
             return unpickle_data_structure(env_read_run_detail_file)
        elif os.path.exists(env_read_run_detail_jsonfile):
             logger.info(f"{env_read_run_detail_jsonfile} exists, so using that")
             with open(env_read_run_detail_jsonfile, "r") as f:
                 record_list = json.load(f)
                 length = len(record_list)
                 for i in range(length):
                     # record = record_list[i]
                     record_list[i]["query_type"] = checklist_type
                 pickle_data_structure(record_list, env_read_run_detail_file)
                 # sys.exit()
                 return record_list
        else:
            query_params_json = get_query_params(checklist_type)
            logger.info(f"Doing the main search of environmental data via {checklist_type}, \n  query: {query_params_json}")
            record_list = setup_run_api_call(query_params_json)
            logger.info(f"Finished running {checklist_type}")

            logger.info(f"got {len(record_list)} records")
            # record_list = record_list[0:5]
            length = len(record_list)
            for i in range(length):
                # record = record_list[i]
                record_list[i]["query_type"] = checklist_type
            logger.info(f"Writing records to {env_read_run_detail_file}")
            pickle_data_structure(record_list, env_read_run_detail_file)

    #logger.info(record_list)

    # sys.exit()
    return record_list

def get_all_study_details():
    study_details_file = "study_details.pickle"
    if os.path.exists(study_details_file):
        ic("env_sample_id_file exists, so can unpickle it")
        record_list = unpickle_data_structure(study_details_file)
        return pd.DataFrame.from_records(record_list)

    #'result=study&fields=study_accession%2Cstudy_title%2Cstudy_description&format=tsv'
    query_params_json = get_query_params("environmental_checklists")
    srv = query_params_json['srv']
    fields = "study_accession%2Cstudy_title%2Cstudy_description"
    params = "result=study" + "&fields=" + fields + "&format=json"
    limit = '&limit=0'
    url = srv + '?' + params + limit
    ic(url)
    record_list = json.loads(run_webservice(url))
    #ic(record_list)

    pickle_data_structure(record_list, study_details_file)
    return pd.DataFrame.from_records(record_list)

def get_env_sample_ids():
    env_sample_id_file = "env_sample_id_file.pickle9"

    if os.path.exists(env_sample_id_file):
        ic("env_sample_id_file exists, so can unpickle it")
        return unpickle_data_structure(env_sample_id_file)

    query_params_json = get_query_params("environmental_checklists")
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

def get_presence_or_absence_col(df, col_name):
    # col with and without values
    # FFS isnull etc. did not work
    col_list = df[col_name].to_list()
    absent_count = 0
    present_count = 0
    for val in col_list:
        if val == None:
            absent_count += 1
        else:
            present_count += 1
    return present_count, absent_count


def print_value_count_table(df_var):
    counts = df_var.value_counts()
    percs = df_var.value_counts(normalize = True)
    tmp_df = pd.concat([counts, percs], axis = 1, keys = ['count', 'percentage'])
    tmp_df['percentage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in tmp_df['percentage']], index = tmp_df.index)
    logger.info(tmp_df)


def process_geographical_data(old_df):
    df = old_df.copy()
    if 'country_clean'  in df.columns:
        logger.info("geographical data already processed")
        return df

    df['has_geographical_coordinates'] = True
    df['has_geographical_coordinates'] = df['has_geographical_coordinates'].mask(df['lat'].isna(), False)
    print_value_count_table(df.has_geographical_coordinates)

    df['has_broad_scale_environmental_context'] = True
    df['has_broad_scale_environmental_context'] = df['has_broad_scale_environmental_context'].mask(
        df['broad_scale_environmental_context'] == '', False)

    #print_value_count_table(df.has_broad_scale_environmental_context)
    #print_value_count_table(df.broad_scale_environmental_context)

    df['country_clean'] = df['country'].apply(select_first_part)
    ic("About to call geographical")
    geography_obj = Geography()
    df['continent'] = df['country_clean'].apply(geography_obj.get_continent)
    df['ocean'] = df['country_clean'].apply(geography_obj.get_ocean)

    return df



def do_geographical(df):
    """

    :param df:
    :return:
    """
    df = process_geographical_data(df)
    print_value_count_table(df.country_clean)
    print_value_count_table(df.continent)

    tmp_df = df[df['ocean'] != 'not ocean']
    print_value_count_table(tmp_df.ocean)

    path_list = ['continent', 'country_clean']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plotfile = "../images/geography_sunburst.png"
    plot_sunburst(plot_df, 'Figure: ENA "Environmental" readrun records, by country', path_list,
                  'record_count', plotfile)

    path_list = ['ocean']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plot_df = plot_df[plot_df['ocean'] != 'not ocean']
    plotfile = "../images/ocean_sunburst.png"
    plot_sunburst(plot_df, 'Figure: ENA "Environmental" readrun records, by ocean', path_list,
                  'record_count', plotfile)

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
        #ic(f"no year match for {value}")  # e,g,  f"no year match for {value}": 'no year match for restricted access'
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

def generate_sankey_chart_data(df, columns: list, sankey_link_weight: str):

    column_values = [df[col] for col in columns]
    ic(column_values)

    # this generates the labels for the sankey by taking all the unique values
    labels = sum([list(node_values.unique()) for node_values in column_values], [])
    ic(labels)

    # initializes a dict of dicts (one dict per tier)
    link_mappings = {col: {} for col in columns}

    # each dict maps a node to unique number value (same node in different tiers
    # will have different number values
    i = 0
    for col, nodes in zip(columns, column_values):
        for node in nodes.unique():
            link_mappings[col][node] = i
            i = i + 1

    # specifying which columns are serving as sources and which as sources
    # ie: given 3 df columns (col1 is a source to col2, col2 is target to col1 and
    # a source to col 3 and col3 is a target to col2
    source_nodes = column_values[: len(columns) - 1]
    target_nodes = column_values[1:]
    source_cols = columns[: len(columns) - 1]
    target_cols = columns[1:]
    links = []

    # loop to create a list of links in the format [((src,tgt),wt),(),()...]
    for source, target, source_col, target_col in zip(source_nodes, target_nodes, source_cols, target_cols):
        for val1, val2, link_weight in zip(source, target, df[sankey_link_weight]):
            links.append(
                (
                    (
                        link_mappings[source_col][val1],
                        link_mappings[target_col][val2]
                    ),
                    link_weight,
                )
            )

    # creating a dataframe with 2 columns: for the links (src, tgt) and weights
    df_links = pd.DataFrame(links, columns = ["link", "weight"])

    # aggregating the same links into a single link (by weight)
    df_links = df_links.groupby(by = ["link"], as_index = False).agg({"weight": sum})

    # generating three lists needed for the sankey visual
    sources = [val[0] for val in df_links["link"]]
    targets = [val[1] for val in df_links["link"]]
    weights = df_links["weight"]

    ic(labels, sources, targets, weights)
    return labels, sources, targets, weights
def plot_sankey(df, sankey_link_weight, columns, title, plotfile):

    # list of list: each list are the set of nodes in each tier/column

    (labels, sources, targets, weights) = generate_sankey_chart_data(df, columns, sankey_link_weight)

    color_link = ['#000000', '#FFFF00', '#1CE6FF', '#FF34FF', '#FF4A46',
                  '#008941', '#006FA6', '#A30059', '#FFDBE5', '#7A4900',
                  '#0000A6', '#63FFAC', '#B79762', '#004D43', '#8FB0FF',
                  '#997D87', '#5A0007', '#809693', '#FEFFE6', '#1B4400',
                  '#4FC601', '#3B5DFF', '#4A3B53', '#FF2F80', '#61615A',
                  '#BA0900', '#6B7900', '#00C2A0', '#FFAA92', '#FF90C9',
                  '#B903AA', '#D16100', '#DDEFFF', '#000035', '#7B4F4B',
                  '#A1C299', '#300018', '#0AA6D8', '#013349', '#00846F',
                  '#372101', '#FFB500', '#C2FFED', '#A079BF', '#CC0744',
                  '#C0B9B2', '#C2FF99', '#001E09', '#00489C', '#6F0062',
                  '#0CBD66', '#EEC3FF', '#456D75', '#B77B68', '#7A87A1',
                  '#788D66', '#885578', '#FAD09F', '#FF8A9A', '#D157A0',
                  '#BEC459', '#456648', '#0086ED', '#886F4C', '#34362D',
                  '#B4A8BD', '#00A6AA', '#452C2C', '#636375', '#A3C8C9',
                  '#FF913F', '#938A81', '#575329', '#00FECF', '#B05B6F',
                  '#8CD0FF', '#3B9700', '#04F757', '#C8A1A1', '#1E6E00',
                  '#7900D7', '#A77500', '#6367A9', '#A05837', '#6B002C',
                  '#772600', '#D790FF', '#9B9700', '#549E79', '#FFF69F',
                  '#201625', '#72418F', '#BC23FF', '#99ADC0', '#3A2465',
                  '#922329', '#5B4534', '#FDE8DC', '#404E55', '#0089A3',
                  '#CB7E98', '#A4E804', '#324E72', '#6A3A4C'
                  ]

    ic(df.head(10))
    #---------------------------------
    fig = go.Figure(data = [go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            #label = ["A1", "A2", "B1", "B2", "C1", "C2"],
            label = labels,
            color = "blue"
        ),
        link = dict(
            # source = [0, 1, 0, 2, 3, 3],  # indices correspond to labels, eg A1, A2, A1, B1, ...
            # target = [2, 3, 3, 4, 4, 5],
            # value = [8, 4, 2, 8, 4, 2]
            source = sources,
            target = targets,
            value = weights,
            color=color_link
        ))])


    fig.update_layout(title_text = title, font_size = 10)
    if plotfile == "plot":
            fig.show()
    else:
            ic(f"Sankey plot to {plotfile}")
            fig.write_image(plotfile)


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

    print(df.groupby(['library_source', 'library_strategy']).size().reset_index().to_string(index=False))
    ic(df.columns)
    path_list = ['library_source', 'library_strategy', 'instrument_platform', 'collection_year_bin']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plotfile = "../images/experimental_analysis_strategy.png"
    sankey_link_weight = 'record_count'

    plot_sankey(plot_df, sankey_link_weight, path_list, 'Figure ENA "Environmental" readrun record count: library_source, library_strategy, platform, collection_date', plotfile)

    return df


def target_gene_analysis(df):
    """
    for the target genes as a checklist field
    :param df:
    :return:
    """
    logger.info("for the target genes as a checklist field")
    logger.debug(df['target_gene'].value_counts().head())
    # print_value_count_table(df['target_gene'])
    total = len(df)
    tmp_df = df[df['target_gene'] != ""]
    # print_value_count_table(tmp_df['target_gene'])
    total_w_tgs = len(tmp_df)
    logger.info(f"total target_gene count = {total_w_tgs} / {total} = {round((100 * total_w_tgs/ total),2)}%")



def plot_sunburst(df, title, path_list, value_field, plotfile):
    """

    :param df:
    :param title:
    :param path_list:
    :param value_field:
    :param plotfile:
    :return:
    """
    fig = px.sunburst(
            df,
            path = path_list,
            values = value_field,
            title = title,
        )
    if plotfile == "plot":
            fig.show()
    else:
            logger.info(f"Sunburst plot to {plotfile}")
            fig.write_image(plotfile)

def analyse_environment(df):
    """
    uses the tags to predict the environment, is rather rough and ready
    assuming is all terrestrial with a low confidence
    :param df:
    :return: df        with the addition of ['env_prediction']  ['env_prediction_hl']  ['env_confidence']
    """
    ic(len(df))
    def process_env_tags(value):
        my_tag_list = value.split(';')
        my_env_tags = [s for s in my_tag_list if "env_" in s]
        return my_env_tags

    print_value_count_table(df.tag)
    # ic(df.tag.head(50))
    df['env_tag'] = df['tag'].apply(process_env_tags)
    df['env_tag_string'] = df['env_tag'].apply(lambda x: ';'.join(x))
    # ic(df['env_tag'].value_counts().head(5))
    cp_df = df.copy()
    def is_w_env_tags(value_list):
        if len(value_list) == 0:
            return False
        return True

    # tmp_df = cp_df[len(cp_df.env_tag)> 0]
    df['is_env_tags'] = df['env_tag'].apply(is_w_env_tags)
    logger.debug(f"{df['env_tag'].value_counts().head()}")
    logger.info(f"{df.columns}")
    tmp_df = df[df['is_env_tags'] == True]
    # print_value_count_table(tmp_df.env_tag)
    logger.debug(tmp_df['env_tag'].value_counts().head(5))
    logger.debug(tmp_df['env_tag'].explode().unique())
    # tmp_df['env_tag_string'] = tmp_df['env_tag'].apply(lambda x: ';'.join(x))
    # tmp_df['env_tag_string'] = tmp_df['env_tag'].str.join(';')
    # ic(tmp_df['env_tag_string'].unique())
    # ic(my_env_lists['env_tag'])
    #  for tag in tmp_df['env_tag'].unique():
    #      ic(tag)
    logger.info(f"starting len={len(df)} filtered len={len(tmp_df)}")

    tag_string_assignment = {}
    # f = tmp_df['env_tag_string'].str.contains("env_geo",na=False)
    # sys.exit()

    logger.info("++++++++++++++++++++++++++++++++++++++++++++++++")
    not_assigned = []
    multiples = []
    aquatic_tag_set = ['env_geo:marine', 'env_geo:freshwater', 'env_geo:brackish', 'env_geo:coastal', 'env_tax:marine',
                        'env_tax:freshwater', 'env_tax:brackish', 'env_tax:coastal']
    terrestrial_tag_set = ['env_geo:terrestrial', 'env_tax:terrestrial']
    for tags in tmp_df['env_tag_string'].unique():
        logger.debug(tags)
        tag_list = tags.split(';')

        if 'env_geo' in tags:
            # ic(f"----------------------{tags}")
            matches = re.findall(r'env_geo[^;]*', tags)
            # ic(matches)
            if len(matches) > 1:
                msg = f"WARNING, multiple GEO matches={matches}, tags={tags} THAT IS NOT YET HANDLED"
                if 'env_geo:coastal' in matches and 'env_geo:marine' in matches:
                    if len(tag_list) == 2:
                        tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'medium'}
                    elif ('env_tax:marine' in tags or 'env_tax:coastal' or 'env_tax:brackish' in tags):
                        tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'high'}
                    else:
                        logger.debug(msg)
                        multiples.append(msg)
                elif 'env_geo:terrestrial' in tags:
                    if 'env_geo:freshwater' in tags:
                        tag_string_assignment[tags] = {'prediction': 'freshwater', 'confidence': 'low'}
                    elif 'env_geo:coastal' in tags:
                        tag_string_assignment[tags] = {'prediction': 'terrestrial', 'confidence': 'medium'}
                    else:
                        multiples.append(msg)
                elif 'env_geo:marine' in tags:
                        if 'env_tax:marine' in tags:
                            tag_string_assignment[tags] = {'prediction': 'marine', 'confidence': 'medium'}
                        elif 'env_geo:freshwater' in tags and 'env_tax:freshwater' in tags:
                            tag_string_assignment[tags] = {'prediction': 'freshwater', 'confidence': 'medium'}
                        elif 'env_geo:freshwater' in tags:
                            tag_string_assignment[tags] = {'prediction': 'brackish', 'confidence': 'low'}
                        else:
                            multiples.append(msg)
                else:
                    logger.debug(matches)
                    multiples.append(msg)
            else:  # ie. one match
                if matches[0] == 'env_geo:marine' and 'env_tax:marine' in tags:
                    tag_string_assignment[tags] = {'prediction': 'marine', 'confidence': 'high'}
                elif matches[0] == 'env_geo:freshwater' and 'env_geo:freshwater' in tags:
                    tag_string_assignment[tags] = {'prediction': 'freshwater', 'confidence': 'high'}
                elif matches[0] == 'env_geo:coastal' and 'env_geo:coastal' in tags:
                    tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'high'}
                elif matches[0] == 'env_geo:brackish' and 'env_geo:brackish' in tags:
                    tag_string_assignment[tags] = {'prediction': 'brackish', 'confidence': 'high'}
                elif matches[0] == 'env_geo:terrestrial' and 'env_geo:terrestrial' in tags:
                    tag_string_assignment[tags] = {'prediction': 'terrestrial', 'confidence': 'high'}
                elif len(tag_list) == 2 and 'env_geo:terrestrial' not in tags:
                    if tag_list[0] in aquatic_tag_set and tag_list[1] in aquatic_tag_set:
                        tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'medium'}
                    elif (tag_list[0] in terrestrial_tag_set and tag_list[1] in aquatic_tag_set) or (tag_list[1] in terrestrial_tag_set and tag_list[0] in aquatic_tag_set):
                            tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
                elif len(tag_list) == 3 and 'env_geo:terrestrial' not in tags:
                    if tag_list[0] in aquatic_tag_set and (tag_list[1] in aquatic_tag_set or tag_list[2] in aquatic_tag_set):
                        tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'medium'}
                    else:
                        tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
                else:
                    logger.debug("________________________________________________________")
                    logger.debug(matches[0])
                    if len(tag_list) == 1:
                        value = re.findall(r'env_geo:(.*)', matches[0])[0]
                        tag_string_assignment[tags] = {'prediction': value, 'confidence': 'medium'}
                    elif matches[0] == 'env_geo:coastal' and "brackish" in tags:
                        tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'medium'}
                    elif matches[0] == 'env_geo:marine' and ("brackish" in tags or "coastal" in tags):
                        tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'medium'}
                    elif matches[0] == 'env_geo:marine' and ("terrestrial" in tags):
                        tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
                    else:
                        if re.match(r'^(env_tax:freshwater;env_geo:marine|env_tax:freshwater;env_tax:terrestrial;env_geo:marine)$',tags):
                            not_assigned.append(tags)
                        else:
                            logger.error(f"Not assigned--->{tags} len_tags={len(tag_list)}")
                            sys.exit()

        # the following are where there are no env_geo: tgs
        elif len(tag_list) == 1:
            value = re.findall(r'env_tax:(.*)', tag_list[0])[0]
            tag_string_assignment[tags] = {'prediction': value, 'confidence': 'medium'}
        elif len(tag_list) == 2:
            if tag_list[0] in aquatic_tag_set and tag_list[1] in aquatic_tag_set:
                tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'medium'}
            elif tag_list[0] in aquatic_tag_set and tag_list[1] in aquatic_tag_set:
                tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
            elif tag_list[0] in aquatic_tag_set and tag_list[1] in terrestrial_tag_set:
                tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
            elif ((tag_list[0] in terrestrial_tag_set and tag_list[1] in aquatic_tag_set) or
                  (tag_list[1] in terrestrial_tag_set and tag_list[0] in aquatic_tag_set)):
                tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
            else:
                not_assigned.append(tags)
        elif len(tag_list) == 3:
                if tag_list[0] in aquatic_tag_set and (
                        tag_list[1] in aquatic_tag_set or tag_list[2] in aquatic_tag_set):
                    tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'low'}
                elif tag_list[1] in aquatic_tag_set and (
                        tag_list[2] in aquatic_tag_set):
                    tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'low'}
                elif tag_list[0] in terrestrial_tag_set and (
                            tag_list[1] in aquatic_tag_set and tag_list[2] in aquatic_tag_set):
                    tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
                else:
                    not_assigned.append(tags)
        elif len(tag_list) == 4:
                if (tag_list[0] in aquatic_tag_set or tag_list[1] in aquatic_tag_set) and (
                        tag_list[2] in aquatic_tag_set or tag_list[3] in aquatic_tag_set):
                    tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'low'}
                else:
                    not_assigned.append(tags)
        else:
            not_assigned.append(tags)
            logger.debug(f"Not assigned--->{tags} len_tags={len(tag_list)}")
    # END OF FOR
    logger.info("finished big for loop")

    # ic(tag_string_assignment)
    if len(multiples) > 0:
        logger.error("Apologies: you need to address these cases before proceeding")
        logger.error(f"multiples:{multiples}")
        logger.error(f"not_assigned: {not_assigned}")
        sys.exit()
    elif len(not_assigned) > 0:
        logger.error("Apologies: you need to address these cases before proceeding")
        logger.error(f"not_assigned: {not_assigned}")
        sys.exit()

    # ic('env_tax:freshwater;env_tax:terrestrial;env_geo:marine')
    # tmp_df = df[df['env_tags'].str.contains('env_tax:freshwater;env_tax:terrestrial;env_geo:marine')]
    # ic(tmp_df['sample_accession'].unique())
    logger.info("about to do a bunch of assignments")

    def actually_assign_env_info_pred(value):
        # ic(value)
        if len(value) > 1:
            # return tag_string_assignment[value]['prediction'], tag_string_assignment[value]['confidence']
            return tag_string_assignment[value]['prediction']
        return "terrestrial_assumed"

    def actually_assign_env_info_conf(value):
        # ic(value)
        if len(value) > 1:
            # return tag_string_assignment[value]['prediction'], tag_string_assignment[value]['confidence']
            return tag_string_assignment[value]['confidence']
        return "low"

    aquatic_set = ('marine', 'brackish', 'coastal', 'freshwater', 'mixed_aquatic')
    logger.info(f"aquatic_set: {aquatic_set}")

    def actually_assign_env_info_pred_hl(value):
        # ic(value)
        if value != "terrestrial_assumed" and value != None:
            if value == "terrestrial":
                   return value
            elif value in aquatic_set:
                    return "aquatic"
            else:
                   return "mixed"
            return "terrestrial_assumed"
        return "terrestrial_assumed"

        #, tag_string_assignment[value]['confidence']
    ic(len(df))

    df['env_prediction'] = df['env_tags'].apply(actually_assign_env_info_pred)
    df['env_confidence'] = df['env_tags'].apply(actually_assign_env_info_conf)

    df['env_prediction_hl'] = df['env_prediction'].apply(actually_assign_env_info_pred_hl)
    print_value_count_table(df['env_prediction'])
    print_value_count_table(df['env_confidence'])
    print()
    logger.info("\n" + df.groupby(['env_prediction', 'env_confidence']).size().to_frame().to_string())
    print_value_count_table(df['env_prediction_hl'])


    path = ['env_prediction_hl', 'env_prediction', 'env_confidence','continent']
    value_field = 'record_count'
    plot_df = df.groupby(path).size().to_frame('record_count').reset_index()
    plotfile = "../images/env_predictions.png"
    plot_sunburst(plot_df, "Figure: ENA readrun environmental predictions using species and lat/lons (Sunburst Plot)", path, value_field, plotfile)

    logger.info("finished All the analysis for the environmental predictions<-------------------")
    return df


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

    analyse_environment(df)

    taxonomy_hash_by_tax_id = create_taxonomy_hash_by_tax_id(tax_id_list)


    df['scientific_name'] = df['tax_id'].apply(scientific_name_lookup)
    # print_value_count_table(df.scientific_name)

    df['lineage'] = df['tax_id'].apply(lineage_lookup)
    # print_value_count_table(df.lineage)
    df['tax_lineage'] = df['tax_id'].apply(tax_lineage_lookup)
    df['lineage_2'] = df['lineage'].str.extract("^([^;]*);")[0]
    df['lineage_3'] = df['lineage'].str.extract("^[^;]*;([^;]*);")[0]
    # print_value_count_table(df.lineage_3)
    df['lineage_minus2'] = df['lineage'].str.extract("([^;]*);[^;]*$")[0]
    df['lineage_minus3'] = df['lineage'].str.extract("([^;]*);[^;]*;[^;]*$")[0]
    print_value_count_table(df.lineage_minus2)
    tax_id_list = df['tax_id'].unique()
    ic(len(tax_id_list))

    path_list = ['lineage_2', 'lineage_minus2', 'scientific_name']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plotfile = "../images/taxonomic_analysis_sunburst.png"
    plot_sunburst(plot_df, 'Figure: ENA "Environmental" readrun records, tax lineage(select)', path_list, 'record_count', plotfile)

    path_list = ['lineage_2', 'lineage_minus3', 'lineage_minus2', 'scientific_name', 'lineage']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plot_df = plot_df[plot_df['lineage_2'] == 'Eukaryota']
    path_list = ['lineage_minus3', 'lineage_minus2', 'scientific_name']
    plotfile = "../images/taxonomic_analysis_euk_sunburst.png"
    plot_sunburst(plot_df, 'Figure: ENA "Environmental" readrun records, tax lineage(Euk)', path_list,
                  'record_count', plotfile)


    path_list = ['lineage_2', 'lineage_minus3', 'lineage_minus2', 'scientific_name', 'lineage']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plot_df = plot_df[plot_df['lineage'].str.contains('Vertebrata')]
    path_list = ['lineage_minus3', 'lineage_minus2', 'scientific_name']
    plotfile = "../images/taxonomic_analysis_euk_sunburst.png"
    plot_sunburst(plot_df, 'Figure: ENA "Environmental" readrun records, Vertebrata', path_list,
              'record_count', plotfile)


    path_list = ['library_source', 'library_strategy', 'lineage_2']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plotfile = "../images/experimental_analysis_strategy_tax.png"
    sankey_link_weight = 'record_count'
    plot_sankey(plot_df, sankey_link_weight, path_list, 'Figure ENA "Environmental" readrun record count: library_source, library_strategy & tax', plotfile)


    return df

def clean_dates_in_df(df):
    df['collection_year'] = df['collection_date'].apply(collection_date_year)
    df['collection_year'] = pd.to_numeric(df['collection_year'], errors = 'coerce').astype('Int64')
    df = df.sort_values(by = ['collection_date'])
    df['collection_year_bin'] = df['collection_year'].apply(create_year_bins)

    return df

def add_insdc_member_receiver(df):
    ic()
    #df = df.sample(n=100)
    ic(df.dtypes)
    def get_insdc_member_receiver(value):
        if value.startswith('SAMN'):
            return 'NCBI'
        elif value.startswith('SAME'):
            return 'ENA'
        elif value.startswith('SAMD'):
            return 'DDBJ'
        else:
            return None

    df['insdc_member_receiver'] = df['sample_accession'].apply(get_insdc_member_receiver)
    ic()
    return df


def analyse_readrun_detail(df):
    logger.info("in analyse_readrun_detail")
    # count = 0
    # for record in env_readrun_detail:
    #
    #     ic(record)
    #     count = count + 1
    #     if count > 3:
    #         break


    # ['sample_accession', 'run_accession', 'library_strategy',
    #                        'library_source', 'instrument_platform', 'lat', 'lon', 'country',
    #                        'broad_scale_environmental_context', 'tax_id', 'checklist',
    #                        'collection_date', 'ncbi_reporting_standard', 'target_gene', 'tag']
    # dtype = 'object')

    # df = df.sample(n=100000)
    # df['sample_accession'] = df['sample_accession'].to_string()
    ic(df['sample_accession'])
    df = add_insdc_member_receiver(df)
    print_value_count_table(df.insdc_member_receiver)

    # outfile = all_sample_accessions.tsv"
    # ic(outfile)
    # df.sample_accession.to_csv(outfile)
    target_gene_analysis(df)

    print('NCBI "checklists":')
    print_value_count_table(df.ncbi_reporting_standard)
    print('ENA "checklists":')
    print_value_count_table(df.checklist)

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

def delist_col(my_list):
    """
    deconvolute a list of list
    :param my_list:
    :return: list
    """
    gene_list = []
    for gene_row_list in my_list:
        for gene in gene_row_list:
             gene_list.append(gene)
    return gene_list

def get_percentage_list(gene_list):
    """
    Takes
    :param gene_list:
    :return:
    """
    # ic(Counter(gene_list))
    c = Counter(gene_list)
    out = sorted([(i, c[i], str(round(c[i] / len(gene_list) * 100.0, 2)) + "%") for i in c])
    ic(out)
    return out


def analyse_all_study_details(df):
    """
    Generates a subset of the df, indexed from sample_accession
    Plus annotates two columns using
    barcoding_df['barcoding_genes_from_study'] = list of genes
    barcoding_df['is_barcoding_experiment_probable'] = True

    :param df:
    :return: barcoding_df
    """
    logger.info("in analyse_all_study_details---------------------------")
    ic(len(df))
    barcoding_pattern = '16S|18S|ITS|26S|5.8S|RBCL|rbcL|matK|MATK|COX1|CO1|mtCO|barcod'
    barcoding_title_df = df[df.study_title.str.contains(barcoding_pattern, regex= True, na=False)]
    ic(f"'study_title' with barcoding genes total={len(barcoding_title_df)}")
    ic(barcoding_title_df['study_title'].sample(n=10))

    barcoding_description_df = df[df.study_description.str.contains(barcoding_pattern, regex= True, na=False)]
    ic(f"'study_description' with barcoding genes total={len(barcoding_description_df)}")
    ic(barcoding_description_df['study_description'].sample(n=5))

    barcoding_df = pd.concat([barcoding_title_df, barcoding_description_df]).drop_duplicates().reset_index(drop=True)
    ic(f"barcoding total = {len(barcoding_df)}")
    barcoding_df['combined_tit_des'] = barcoding_df['study_title'] + barcoding_df['study_description']
    barcoding_df['is_barcoding_experiment_probable'] = True

    def get_barcoding_genes(value):

        sgenes_pattern = re.compile(r'^([1-9]{2}|5\.8)([sS])[ ]?(r)?([RD]NA)?', flags=0)
        sgenes_pattern = re.compile(r'^([1-9]{2}|5\.8)([sS])[ ]?r?(RNA|DNA|ribo)?', flags=0)
        rbcl_pattern = re.compile(r'^(RBCL)', re.IGNORECASE)
        its_pattern = re.compile(r'^(ITS)([1-2])?')
        matk_pattern = re.compile(r'^(matk)', re.IGNORECASE)
        COX1_pattern = re.compile('^COX1|CO1|COI|mtCO|Cytochrome c oxidase|cytochrome oxidase', re.IGNORECASE)
        def clean_name(my_list):
            """
             a clean harmonised list of barcoding gene names
            :param  list of gene names:
            :return: harmonised list.
            """
            clean_list = []
            #ic("-----------------------------------------------------------")
            for my_gene in my_list:
                #ic(my_gene)

                match = re.search(rbcl_pattern, my_gene)
                if match:
                    # ic(f"----------clean=rbcL")
                    clean_list.append("rbcL")
                    continue
                match = re.search(its_pattern, my_gene)
                if match:
                    if match.group(2):
                        # ic(f"----------clean=ITS{match.group(2)}")
                        clean_list.append("ITS" + match.group(2))
                    else:
                        # ic(f"----------clean=ITS")
                        clean_list.append("ITS")
                    continue
                match = re.search(matk_pattern, my_gene)
                if match:
                        # ic("----------clean=matK")
                        clean_list.append("matK")
                        continue
                match = re.search(COX1_pattern, my_gene)
                if match:
                        # ic("----------clean=COX1")
                        clean_list.append("COX1")
                        continue

                match = re.search(sgenes_pattern, my_gene)
                if match:
                    # ic(match.group(1))
                    # ic(match.group(2))
                    clean_gene_name = match.group(1) + "S"
                    if match.group(3):
                        # ic(f"---------------{match.group(3)}")
                        clean_gene_name += " r" + match.group(3)
                    clean_list.append(clean_gene_name)
                    # ic(clean_gene_name)
                    continue

                ic(f"remaining gene: -->{my_gene}<--")
                sys.exit()


            return clean_list
        barcode_genes_pattern = re.compile('16[sS][ ]?r?[RD]NA|16[sS][ ]?ribo|18S|ITS[12]?|26[Ss]|5\.8[Ss]|rbcL|rbcl|RBCL|matK|MATK|cox1|co1|COX1|CO1|COI|mtCO|cytochrome c oxidase|cytochrome oxidase')
        genes = list(set(re.findall(barcode_genes_pattern, value)))
        if len(genes) > 0:
            # ic(genes)
            return clean_name(genes)
        else:
            genes = list(set(re.findall(r'16[Ss]', value)))
            if len(genes) > 0:
                return clean_name(genes)
            return None
    barcoding_df['barcoding_genes_from_study'] = barcoding_df.combined_tit_des.apply(get_barcoding_genes)
    ic(barcoding_df['barcoding_genes_from_study'].value_counts())
    print_value_count_table(barcoding_df['barcoding_genes_from_study'])

    gene_list = delist_col(barcoding_df[barcoding_df['barcoding_genes_from_study'].notnull()]['barcoding_genes_from_study'].to_list())
    get_percentage_list(gene_list)
    gene_set = set(gene_list)
    total = len(barcoding_df)
    present_count, absent_count = get_presence_or_absence_col(barcoding_df, 'barcoding_genes_from_study')
    ic(f"barcoding_genes_from_study present_count {present_count}  {present_count/total*100:.2f}%")
    ic(f"barcoding_genes_from_study absent_count {absent_count}   {absent_count/total*100:.2f}%")

    return barcoding_df

def filter_for_aquatic(env_readrun_detail):
    logging.info("filter_for_aquatic")
    df = pd.DataFrame.from_records(env_readrun_detail)

    # logger.info(df["broad_scale_environmental_context"].value_counts())
    # outfile = "broad_scale_environmental_context.txt"
    # with open(outfile, "w") as f:
    #     f.write(df["broad_scale_environmental_context"].value_counts().to_string())
    # logger.info(f"wrote {outfile}")

    # df = df.head(10000)
    logger.info(df.columns)

    aquatic_pattern = re.compile('marine|freshwater|coastal|brackish')
    aquatic_biome_pattern = re.compile('marine|ocean|freshwater|coastal|brackish|estuar|fresh water|groundwater|glacial_spring|^sea|seawater|lake|river|wastewater|waste water|stormwater', re.IGNORECASE)

    def local_process_env_tags(value):
        my_tag_list = value.split(';')

        my_env_tags = [s for s in my_tag_list if "env_" in s]

        return my_env_tags

    def test_if_aquatic(value):
        if re.search(aquatic_pattern, value):
            return True

        return False

    def test_if_ocean(value):
        if len(value) == 0 or value == 'not ocean':
            return False

        return True

    def test_if_aquatic_biome_pattern(value):
        if re.search(aquatic_biome_pattern, value):
            return True

        return False

    logging.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    #print_value_count_table(df.tag)
    # ic(df.tag.head(50))
    #df['env_tax'] = df['tag'].str.extract("(env_tax:[^;]*)")[0]
    df['env_tag'] = df['tag'].apply(local_process_env_tags)
    df['env_tags'] = df['env_tag'].apply(lambda x: ';'.join(x))
    #print_value_count_table(df.env_tags)
    df['aquatic'] = df['env_tags'].apply(test_if_aquatic)
    logging.info(f"aquatic= {df['aquatic'].value_counts()}")
    df_aquatic = df[df['aquatic'] == True]
    df_remainder = df[df['aquatic'] == False]
    logging.info(f"total_records={len(df)}, using env_tags aquatic_filtered={len(df_aquatic)} and remainder={len(df_remainder)}")

    logging.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    df_remainder = process_geographical_data(df_remainder)
    logger.info(df_remainder.columns)
    logging.info(df_remainder['ocean'].value_counts())
    df_remainder['aquatic'] = df_remainder['ocean'].apply(test_if_ocean)
    logging.info(f"ocean: aquatic= {df_remainder['aquatic'].value_counts()}")
    df_remainder_aquatic = df_remainder[df_remainder['aquatic'] == True]
    df_remainder_nonaquatic = df_remainder[df_remainder['aquatic'] == False]
    logging.info(f"after using test_if_ocean aquatic_filtered={len(df_remainder_aquatic)}  not {len(df_remainder_nonaquatic)}")
    df_aquatic = pd.concat([df_aquatic, df_remainder_aquatic])
    logging.info(f"len(df_aquatic) = {len(df_aquatic)}")

    logging.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    df_remainder = df_remainder_nonaquatic.copy()
    df_remainder['aquatic'] = df_remainder['broad_scale_environmental_context'].apply(test_if_aquatic_biome_pattern)
    logging.info(f"broad_scale_environmental_context aquatic= {df_remainder['aquatic'].value_counts()}")
    df_remainder_aquatic = df_remainder[df_remainder['aquatic'] == True]
    df_remainder_nonaquatic = df_remainder[df_remainder['aquatic'] == False]
    logging.info(f"after using test_if_aquatic_biome_pattern={len(df_remainder_aquatic)}  not {len(df_remainder_nonaquatic)}")
    logging.info(f"after using broad_scale_environmental_context aquatic_filtered={len(df_remainder_aquatic)}")
    df_aquatic = pd.concat([df_aquatic, df_remainder_aquatic])
    logging.info(f"len(df_aquatic) = {len(df_aquatic)}")

    return df_aquatic

def main():
    # df_all_study_details = analyse_all_study_details(get_all_study_details())
    # ic(len(df_all_study_details))
    #
    # sample_ids = get_env_sample_ids()
    # ic(len(sample_ids))
    # readrun_ids = get_env_readrun_ids()
    # ic(len(readrun_ids))

    env_readrun_detail = get_env_readrun_detail()
    df_env_readrun_detail = filter_for_aquatic(env_readrun_detail)
    readrun_ids_set = set(df_env_readrun_detail['run_accession'])
    logging.info(f"readrun_ids_set={len(readrun_ids_set)}")
    sample_ids_set = set(df_env_readrun_detail['sample_accession'])
    logging.info(f"sample_ids_set={len(sample_ids_set)}")

    analyse_readrun_detail(df_env_readrun_detail)


if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    logger = logging.getLogger(name = 'mylogger')
    coloredlogs.install(logger = logger)
    logger.propagate = False
    ch = logging.StreamHandler(stream = sys.stdout)
    ch.setFormatter(fmt = my_coloredFormatter)
    logger.addHandler(hdlr = ch)
    logger.setLevel(level = logging.INFO)

    # Read arguments from command line
    prog_des = "Script to query ENA(INSDC) resources, but mainly to analyse the eDNA metadata from the different work"

    parser = argparse.ArgumentParser(description = prog_des)

    # Adding optional argument, n.b. in debugging mode in IDE, had to turn required to false.
    parser.add_argument("-d", "--debug_status",
                        help = "Debug status i.e.True if selected, is verbose",
                        required = False, action = "store_true")

    parser.parse_args()
    args = parser.parse_args()

    if args.debug_status:
        ic.enable()
        logger.setLevel(level = logging.DEBUG)
    else:
        ic.disable()
    logger.info(prog_des)

    main()
