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
                 '%22%20OR%20CHECKLIST%3D%22ERC000031%22%20OR%20CHECKLIST%3D%22ERC000036%22)%20OR'
                 '(ncbi_reporting_standard%3D%22*ENV*%22%20ORncbi_reporting_standard%3D%22*WATER*%22'
                 '%20ORncbi_reporting_standard%3D%22*SOIL*%22%20ORncbi_reporting_standard%3D%22*AIR*%22'
                 '%20ORncbi_reporting_standard%3D%22*SEDIMENT*%22%20ORncbi_reporting_standard%3D%22*BUILT%22%20))'
                 'AND%20not_tax_tree('
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
    env_read_run_detail_file = "read_run_ena_detail.pickle"
    env_read_run_detail_file = "read_run_allinsdc_detail.pickle"
    if os.path.exists(env_read_run_detail_file):
        ic(f"{env_read_run_detail_file} exists, so can unpickle it")
        return unpickle_data_structure(env_read_run_detail_file)

    fields = ("sample_accession%2Crun_accession%2Clibrary_strategy%2Clibrary_source%2Cinstrument_platform%2Clat%2Clon%2Ccountry"
              "%2Cbroad_scale_environmental_context%2Ctax_id%2Cchecklist%2Ccollection_date%2Cncbi_reporting_standard%2Ctarget_gene%2Ctag%2Cstudy_accession%2Cstudy_title")

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

def get_all_study_details():
    study_details_file = "study_details.pickle"
    if os.path.exists(study_details_file):
        ic("env_sample_id_file exists, so can unpickle it")
        record_list = unpickle_data_structure(study_details_file)
        return pd.DataFrame.from_records(record_list)

    #'result=study&fields=study_accession%2Cstudy_title%2Cstudy_description&format=tsv'
    query_params_json = get_query_params()
    srv = query_params_json['srv']
    fields = ("study_accession%2Cstudy_title%2Cstudy_description")
    params = "result=study" + "&fields=" + fields + "&format=json"
    limit = '&limit=0'
    url = srv + '?' + params + limit
    ic(url)
    record_list = json.loads(run_webservice(url))
    #ic(record_list)

    pickle_data_structure(record_list, study_details_file)
    return pd.DataFrame.from_records(record_list)

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
    ic(df['target_gene'].value_counts().head())



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
            ic(f"Sunburst plot to {plotfile}")
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
    #df['env_tax'] = df['tag'].str.extract("(env_tax:[^;]*)")[0]
    df['env_tag'] = df['tag'].apply(process_env_tags)
    df['env_tags'] = df['env_tag'].apply(lambda x: ';'.join(x))
    # ic(df['env_tag'].value_counts().head(5))

    tmp_df = df[df.env_tag.str.len() > 0]
    # print_value_count_table(tmp_df.env_tag)
    #ic(tmp_df['env_tag'].value_counts().head(5))
    #ic(tmp_df['env_tag'].explode().unique())
    tmp_df['env_tag_string'] = tmp_df['env_tag'].str.join(';')
    # ic(tmp_df['env_tag_string'].unique())
    # ic(my_env_lists['env_tag'])
    #  for tag in tmp_df['env_tag'].unique():
    #      ic(tag)

    tag_string_assignment = {}
    # f = tmp_df['env_tag_string'].str.contains("env_geo",na=False)
    # sys.exit()

    not_assigned = []
    multiples = []
    aquatic_tag_set = ['env_geo:marine', 'env_geo:freshwater', 'env_geo:brackish', 'env_geo:coastal', 'env_tax:marine',
                        'env_tax:freshwater', 'env_tax:brackish', 'env_tax:coastal']
    terrestrial_tag_set = ['env_geo:terrestrial', 'env_tax:terrestrial']
    for tags in tmp_df['env_tag_string'].unique():
        tag_list = tags.split(';')
        # ic(tags)
        # ic(tag_list)

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
                        ic(msg)
                        multiples.append(msg)
                else:
                    ic(msg)
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
                    ic("________________________________________________________")

                    ic(matches[0])
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
                            ic(f"Not assigned--->{tags} len_tags={len(tag_list)}")
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
            ic()

    # ic(tag_string_assignment)
    if len(multiples) > 0:
        ic("Apologies: you need to address this cases before proceeding")
        ic(multiples)
        ic(not_assigned)
        sys.exit()
    elif len(not_assigned) > 0:
        ic("Apologies: you need to address this cases before proceeding")
        ic(not_assigned)
        sys.exit()

    # ic('env_tax:freshwater;env_tax:terrestrial;env_geo:marine')
    # tmp_df = df[df['env_tags'].str.contains('env_tax:freshwater;env_tax:terrestrial;env_geo:marine')]
    # ic(tmp_df['sample_accession'].unique())

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
    print(df.groupby(['env_prediction', 'env_confidence']).size().to_frame().to_string())
    print_value_count_table(df['env_prediction'])
    print()
    print_value_count_table(df['env_prediction_hl'])


    path = ['env_prediction_hl', 'env_prediction', 'env_confidence','continent']
    value_field = 'record_count'
    plot_df = df.groupby(path).size().to_frame('record_count').reset_index()
    plotfile = "../images/env_predictions.png"
    plot_sunburst(plot_df, "Figure: ENA readrun environmental predictions using species and lat/lons (Sunburst Plot)", path, value_field, plotfile)

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
    print_value_count_table(df.scientific_name)

    df['lineage'] = df['tax_id'].apply(lineage_lookup)

    # ic(df['lineage'].value_counts())
    print_value_count_table(df.lineage)
    df['tax_lineage'] = df['tax_id'].apply(tax_lineage_lookup)
    df['lineage_2'] = df['lineage'].str.extract("^([^;]*);")[0]
    df['lineage_3'] = df['lineage'].str.extract("^[^;]*;([^;]*);")[0]
    ic(df['lineage_3'].value_counts())
    print_value_count_table(df.lineage_3)
    df['lineage_minus2'] = df['lineage'].str.extract("([^;]*);[^;]*$")[0]
    df['lineage_minus3'] = df['lineage'].str.extract("([^;]*);[^;]*;[^;]*$")[0]
    print_value_count_table(df.lineage_minus2)

    ic(df['tax_id'].value_counts())
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


def analyse_readrun_detail(env_readrun_detail):
    # count = 0
    # for record in env_readrun_detail:
    #
    #     ic(record)
    #     count = count + 1
    #     if count > 3:
    #         break

    df = pd.DataFrame.from_records(env_readrun_detail)
    ic(df.columns)
    # ['sample_accession', 'run_accession', 'library_strategy',
    #                        'library_source', 'instrument_platform', 'lat', 'lon', 'country',
    #                        'broad_scale_environmental_context', 'tax_id', 'checklist',
    #                        'collection_date', 'ncbi_reporting_standard', 'target_gene', 'tag']
    # dtype = 'object')
    ic()
    # df = df.sample(n=100000)
    # df['sample_accession'] = df['sample_accession'].to_string()
    ic(df['sample_accession'])
    df = add_insdc_member_receiver(df)
    print_value_count_table(df.insdc_member_receiver)

    # outfile = all_sample_accessions.tsv"
    # ic(outfile)
    # df.sample_accession.to_csv(outfile)
    target_gene_analysis(df)

    sys.exit()
    print('NCBI "checklists":')
    print_value_count_table(df.ncbi_reporting_standard)
    print('ENA "checklists":')
    print_value_count_table(df.checklist)




    sys.exit()
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

def analyse_all_study_details(df):
    """
    Generates a subset of the df, indexed from sample_accession
    Plus annotates two columns using
    barcoding_df['barcoding_genes_from_study'] = list of genes
    barcoding_df['is_barcoding_experiment_probable'] = True

    :param df:
    :return: barcoding_df
    """
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

        genes = list(set(re.findall(r'16[Ss] ?rRNA|16[Ss] ?rDNA|18[Ss]|ITS|26[Ss]|5.8[Ss]|RBCL|matK|MATK|COX1|CO1|COI|mtCO', value)))
        if len(genes) > 0:
            # ic(genes)
            return genes
        else:
            genes = list(set(re.findall(r'16[Ss]', value)))
            if len(genes) > 0:
                return genes
            return None
    barcoding_df['barcoding_genes_from_study'] = barcoding_df.combined_tit_des.apply(get_barcoding_genes)
    ic(barcoding_df['barcoding_genes_from_study'].value_counts())
    print_value_count_table(barcoding_df['barcoding_genes_from_study'])

    return barcoding_df

def main():
    df_all_study_details = analyse_all_study_details(get_all_study_details())
    ic(len(df_all_study_details))
    sys.exit()
    sample_ids = get_env_sample_ids()
    ic(len(sample_ids))
    readrun_ids = get_env_readrun_ids()
    ic(len(readrun_ids))

    env_readrun_detail = get_env_readrun_detail()
    ic(len(env_readrun_detail))
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
