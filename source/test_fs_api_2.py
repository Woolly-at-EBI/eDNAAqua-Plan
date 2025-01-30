#!/usr/bin/env python3
"""Script of test_fs_api.py
   based on fairshare's
___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2024-05-21
__docformat___ = 'reStructuredText'
"""

import sys
import requests
import json
import os
import argparse
import logging
import pandas as pd
import re

from statsmodels.stats.descriptivestats import Description

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

data_dir = "/Users/woollard/projects/eDNAaquaPlan/eDNAAqua-Plan/data/biodiversity/2025_Jan"

relevant_topics_array = ["biodiversity", "tax_class","ecosystem", "biological_sample", "abundance", "occurrence"]
relevant_topics_array = ['Marine metagenome', 'Marine coral reef biome', 'Marine environment', 'Marine metagenome', "Biodiversity", "Taxonomy",
                         "Taxonomic classification", "Biological sample", "Abundance", "Occurrence", "Ecosystem",
                         'Environmental Science', 'Geographic Location', 'Microbial Ecology', 'Ecosystem Science',
                         'Ecology', 'Subject agnostic',  'knowledge and information systems', 'Life Cycle State']
# some extra ones to test in the description
desc_topics_array = ['TDWG', 'DwC', 'biodiversity', 'taxonomy', 'ecology']

standard_doi_2024_May_list = ['10.25504/FAIRsharing.0362d8', '10.25504/FAIRsharing.2b04ae', '10.25504/FAIRsharing.3ngg40', '10.25504/FAIRsharing.4c0b6b', '10.25504/FAIRsharing.560f4e', '10.25504/FAIRsharing.5794af', '10.25504/FAIRsharing.90fd70', '10.25504/FAIRsharing.93g1th', '10.25504/FAIRsharing.94ca5a', '10.25504/FAIRsharing.akmeb9', '10.25504/FAIRsharing.azqskx', '10.25504/FAIRsharing.dS2o69', '10.25504/FAIRsharing.e6e5d3', '10.25504/FAIRsharing.fgmzk8', '10.25504/FAIRsharing.hakg7c', '10.25504/FAIRsharing.j4encb', '10.25504/FAIRsharing.kay31r', '10.25504/FAIRsharing.kj336a', '10.25504/FAIRsharing.mqspgs', '10.25504/FAIRsharing.r3vtvx', '10.25504/FAIRsharing.t4be96', '10.25504/FAIRsharing.tghhc4', '10.25504/FAIRsharing.w69t6r', 'https://doi.org/10.1038/s41597-022-01491-3', 'https://doi.org/10.25504/FAIRsharing.1rj558', 'https://doi.org/10.25504/FAIRsharing.23th83', 'https://doi.org/10.25504/FAIRsharing.2b3at8', 'https://doi.org/10.25504/FAIRsharing.322dc0', 'https://doi.org/10.25504/FAIRsharing.384x47', 'https://doi.org/10.25504/FAIRsharing.49bmk', 'https://doi.org/10.25504/FAIRsharing.4c9hhn', 'https://doi.org/10.25504/FAIRsharing.546873', 'https://doi.org/10.25504/FAIRsharing.5970hq', 'https://doi.org/10.25504/FAIRsharing.7tx4ac', 'https://doi.org/10.25504/FAIRsharing.8ktkqy', 'https://doi.org/10.25504/FAIRsharing.8sz2fa', 'https://doi.org/10.25504/FAIRsharing.8wgn56', 'https://doi.org/10.25504/FAIRsharing.9091d9', 'https://doi.org/10.25504/FAIRsharing.9aa0zp', 'https://doi.org/10.25504/FAIRsharing.A29ckB', 'https://doi.org/10.25504/FAIRsharing.NYAjYd', 'https://doi.org/10.25504/FAIRsharing.PB6595', 'https://doi.org/10.25504/FAIRsharing.a3d34f', 'https://doi.org/10.25504/FAIRsharing.ayjdsm', 'https://doi.org/10.25504/FAIRsharing.b8233y', 'https://doi.org/10.25504/FAIRsharing.c2wkqx', 'https://doi.org/10.25504/FAIRsharing.ckg5a2', 'https://doi.org/10.25504/FAIRsharing.d261e1', 'https://doi.org/10.25504/FAIRsharing.db1fb2', 'https://doi.org/10.25504/FAIRsharing.de40c7', 'https://doi.org/10.25504/FAIRsharing.eff3b2', 'https://doi.org/10.25504/FAIRsharing.ezwdhz', 'https://doi.org/10.25504/FAIRsharing.f3a3ca', 'https://doi.org/10.25504/FAIRsharing.feb85q', 'https://doi.org/10.25504/FAIRsharing.fj07xj', 'https://doi.org/10.25504/FAIRsharing.fkrc9', 'https://doi.org/10.25504/FAIRsharing.fmz635', 'https://doi.org/10.25504/FAIRsharing.fzkw7z', 'https://doi.org/10.25504/FAIRsharing.hFLKCn', 'https://doi.org/10.25504/FAIRsharing.hgnk8v', 'https://doi.org/10.25504/FAIRsharing.hgsFLe', 'https://doi.org/10.25504/FAIRsharing.hqyeb7', 'https://doi.org/10.25504/FAIRsharing.jq69k3', 'https://doi.org/10.25504/FAIRsharing.k5ky44', 'https://doi.org/10.25504/FAIRsharing.kr3215', 'https://doi.org/10.25504/FAIRsharing.md3e78', 'https://doi.org/10.25504/FAIRsharing.nft558', 'https://doi.org/10.25504/FAIRsharing.ny9vnm', 'https://doi.org/10.25504/FAIRsharing.p1sejz', 'https://doi.org/10.25504/FAIRsharing.p9EyGm', 'https://doi.org/10.25504/FAIRsharing.pzxjh', 'https://doi.org/10.25504/FAIRsharing.qzrbk', 'https://doi.org/10.25504/FAIRsharing.rnckxp', 'https://doi.org/10.25504/FAIRsharing.svzbnp', 'https://doi.org/10.25504/FAIRsharing.t9fvdn', 'https://doi.org/10.25504/FAIRsharing.v5xfnf', 'https://doi.org/10.25504/FAIRsharing.vq28qp', 'https://doi.org/10.25504/FAIRsharing.vywjrq', 'https://doi.org/10.25504/FAIRsharing.wf28wm', 'https://doi.org/10.25504/FAIRsharing.xfz72j', 'https://doi.org/10.25504/FAIRsharing.xvf5y3', 'https://doi.org/10.25504/FAIRsharing.y49yj6', 'https://fairsharing.org/1387', 'https://fairsharing.org/366', 'https://fairsharing.org/707', 'https://fairsharing.org/726', 'https://fairsharing.org/FAIRsharing.2hh7g7', 'https://fairsharing.org/FAIRsharing.7501d8', 'https://fairsharing.org/FAIRsharing.a55z32', 'https://fairsharing.org/FAIRsharing.b4671a', 'https://fairsharing.org/FAIRsharing.ca48xs', 'https://fairsharing.org/FAIRsharing.em3cg0', 'https://fairsharing.org/FAIRsharing.hn155r', 'https://fairsharing.org/FAIRsharing.jb7wzc', 'https://fairsharing.org/FAIRsharing.nd9ce9', 'https://fairsharing.org/FAIRsharing.va1hck', 'https://fairsharing.org/FAIRsharing.zvrep1']

FAIRSHARE_pattern = re.compile("(FAIRsharing.*$)")

def simple_test(jwt, url):
    base_url = "https://api.fairsharing.org/fairsharing_records/"
    url = base_url + "1"

    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': "Bearer {0}".format(jwt),
    }

    response = requests.request("GET", url, headers = headers)
    print(response.text)

def test_response(response):
    if response.status_code != 200:
        logging.error(f"response status code={response.status_code}")
        logging.info(f"for url={response.url}")
        sys.exit(-1)

def get_record_summary(record_set, search_term):
        logging.debug("inside get_record_summary")
        logging.debug(f"record_set={record_set}")

        def get_first_publication_date(publications):
            year_list = []
            for publication in publications:
                year_list.append(publication['year'])
            year_list = sorted(year_list, reverse = False)
            return year_list[0]

        # print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logging.debug(f"record_set id={record_set['id']} {record_set['attributes']['metadata']['name']} type={record_set['type']}")
        row_hash = {}
        row_hash['search_term'] = search_term
        row_hash['doi'] = record_set['attributes']['doi']
        row_hash['Standard'] = record_set['attributes']['metadata']['name']
        row_hash['Type'] = record_set['attributes']['record_type']
        row_hash['Status'] = record_set['attributes']['metadata']['status']
        row_hash['Description'] = record_set['attributes']['metadata']['description']
        row_hash['Subject'] = ', '.join(record_set['attributes']['subjects'])
        row_hash['Taxonomic Range'] = ', '.join(record_set['attributes']['taxonomies'])

        row_hash[('Homepage')] = record_set['attributes']['metadata']['homepage']
        row_hash['Year of Creation'] = record_set['attributes']['created_at'][0:4]
        row_hash['Countries developing this resource'] = ','.join(record_set['attributes']['countries'])
        row_hash['Domains'] = ', '.join(record_set['attributes']['domains'])
        if row_hash['Domains'] == "":
            row_hash['Domains'] = 'None'
        row_hash['Other subjects'] = ''
        row_hash['Already In FAIRSharing?'] = 'Y'
        row_hash['Added to FAIRSharing'] = ''

        if search_term == "biodiversity":
            row_hash['Already with Biodiversity Subject?'] = "Y"
        else:
            row_hash['Already with Biodiversity Subject?'] = ''

        row_hash['Biodiversity subject added'] = ''
        row_hash['Notes'] = ''
        row_hash['Notes(Peter)'] = ''

        # row_hash['Publications'] = get_first_publication_date(record_set['attributes']['publications'])
        # print()
        # print(row_hash)
        # print()
        # print(json.dumps(row_hash, indent=4))
        # print()
        # logging.info("........................................")
        # for attribute in record_set['attributes']:
        #     logging.info(f"\tattribute={attribute}")
        #     if attribute == 'metadata':
        #         for metadata in record_set['attributes']['metadata']:
        #             logging.info(f"\tmetadata={metadata} value={record_set['attributes']['metadata'][metadata]}")
        #         #sys.exit()
        #
        # logging.info("........................................")
        return row_hash


def process_query_out_json(my_records, fairshare_json, search_query):
    logging.debug(f"inside process_query_out_json starting with {len(my_records)}")
    logging.debug(fairshare_json)
    for record_set in fairshare_json:
        row_hash = get_record_summary(record_set, search_query)
        my_records.append(row_hash)

        # sys.exit()

        # logging.info(f"record_set id={record_set['id']} type={record_set['type']}")
        # logging.info(f"{record_set['attributes']['metadata']['name']}")
        # for attribute in record_set['attributes']:
        #     logging.info(f"\tattribute={attribute}")
        #     if attribute == 'metadata':
        #        for metadata in record_set['attributes']['metadata']:
        #             logging.info(f"\tmetadata={metadata} value={record_set['attributes']['metadata'][metadata]}")
        # #        sys.exit()

        logging.debug("........................................")
        # sys.exit()
        # continue
        logging.debug(row_hash)
    return my_records



def merge_on_column(df, col2merge, col2merge_on):
    """
        for a df where one field col2merge is the only unique one
        use col2merge_on as the unique column value
        :param df:
        :param col2merge:
        :param col2merge_on:
        :return: df
    """
    logging.info(f"merge on standard {col2merge_on}")
    logging.info(f"What is starting len={len(df)}")
    #logging.info(df.head(2))
    merge_name = col2merge_on
    cmnts = {}
    for i, row in df.iterrows():
        while True:
            try:
                if row[col2merge]:
                    cmnts[row[merge_name]].append(row[col2merge])

                else:
                    cmnts[row[merge_name]].append('n/a')

                break

            except KeyError:
                cmnts[row[merge_name]] = []

    df.drop_duplicates(merge_name, inplace=True)
    logging.info(f"What is leaving len={len(df)}")
    df['search_term'] = ['; '.join(v) for v in cmnts.values()]

    return df


def get_all_data(jwt):
    logging.info(f"get_all_data")

    logging.info("Doing searches")
    base_url = "https://api.fairsharing.org/search//fairsharing_records"
    # base_url = "https://api.fairsharing.org/search/record_types"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': "Bearer {0}".format(jwt),
    }

    init = 1
    size = 25
    max_records = 4400   #4295
    max_records = 8000   # needs some way of knowing if

    max = int(max_records / size)
    logging.info(f"max_records={max_records}, so number of loops={max}")

    my_records = []
    for i in range(init, max):

        start = i

        url = 'https://api.fairsharing.org/fairsharing_records/?page[number]=' + str(start) + '&page[size]=' + str(size)
        logging.info(url)
        outfile = data_dir + "/all/" + str(start) + "_" + str(size) + ".json"

        # continue

        if os.path.isfile(outfile) and os.path.getsize(outfile) > 500:
            logging.info(f"  This already exists {outfile} so will omit the search")
            my_json_file = outfile
            with open(my_json_file, 'r') as json_file:
                fairshare_json = json.load(json_file)
        else:
            response = requests.request("get", url, headers = headers)
            test_response(response)
            fairshare_json = json.loads(response.text)

            #biodiversity/i

            logging.info(len(fairshare_json))
            logging.info(f"writing to {outfile}")
            with open(outfile, "w") as outfile:
                json.dump(fairshare_json, outfile)

        my_records = process_query_out_json(my_records, fairshare_json['data'], 'all')
        logging.info(f"len of my_records={len(my_records)}")

    df = pd.DataFrame(my_records)
    print(df.head())
    logging.info(df['Type'].value_counts())
    outfile = "all_fairshare_records.xlsx"
    logging.info(outfile)
    df.to_excel(outfile, index=False)




def mine_all(my_records):

    all_data_dir = data_dir + "/all/"
    all_files = os.listdir(all_data_dir)
    logging.info(f"all_files: total {len(all_files)}")
    for file_node_name in all_files:
        file_name = all_data_dir + file_node_name
        fairshare_json = json.load(open(file_name))
        logging.debug(f"file_name={file_name}")
        print(".",end="")
        my_records = process_query_out_json(my_records, fairshare_json['data'],
                                            "whatever")
        # break
    print()
    return my_records

    #fairshare_json = json.load(open(search_query_dict[search_entry]['outfile']))

def get_count_of_individual_terms(my_list):
    logger.info(f"get_count_of_individual_terms: {len(my_list)}")
    my_topic_dict = {}
    for record in my_list:
        my_array = record.split(', ')
        for term in my_array:
            if term not in my_topic_dict:
                my_topic_dict[term] = 1
            else:
                my_topic_dict[term] += 1

    print(my_topic_dict)
    # print(sorted(my_topic_dict.keys(), reverse=False))

    my_target_topic_dict = {}
    for topic_term in relevant_topics_array:
        if topic_term in my_topic_dict:
            my_target_topic_dict[topic_term] = my_topic_dict[topic_term]
    print("<-------------------------------------------------->")
    print(my_target_topic_dict)

def annotate_hit_search_words(my_df):
    """
    want for the search_term field to record what the hit terms are
    :param my_df:
    :return: my_df
    """

    # Function to find relevant terms in the subject column
    # Function to find relevant terms in both columns
    def find_relevant_terms(row):
        # Handle missing values by replacing None/NaN with an empty string
        subject = str(row["Subject"]) if pd.notna(row["Subject"]) else ""
        domain = str(row["Domains"]) if pd.notna(row["Domains"]) else ""

        text_to_search = f"{subject} {domain}".lower() # Combine both columns
        found_terms = [term for term in relevant_topics_array if term.lower() in text_to_search]
        return ", ".join(found_terms) if found_terms else None

    # Apply function to create 'search_term' column
    my_df["search_term"] = my_df.apply(find_relevant_terms, axis=1)
    # print(my_df["search_term"].value_counts())

    return my_df


def compare2lists(left_list, right_list):
    """

    :param left_list:
    :param right_list:
    :return:
    """
    left_list = [item for item in left_list if not (pd.isna(item))]
    right_list = [item for item in right_list if not (pd.isna(item))]


    left_set = set(left_list)
    right_set = set(right_list)


    print("Doing the comparison between left and right as straight DOI strings")
    print(f"counts: left={len(left_set)} right={len(right_set)}")
    print(f"intersection: len={len(left_set.intersection(right_set))}")
    print(f"intersection: {left_set.intersection(right_set)}")

    left_string = ','.join(left_list)
    for right_term in right_set:
        if right_term in left_string:
            print(f"{right_term} -------in left_string")




    def clean_FAIR_DOI_set(left_set):
        """
        # do FAIR stripping as URL is inconsistent....
        :param left_set:
        :return: clean_set
        """
        clean_left_set = set()
        logger.info(f"clean_FAIR_DOI_set input len={len(left_set)}")
        doi_pattern = re.compile(r"doi.org")
        not_matched_set = set()


        for left_term in left_set:
            # logger.info(f"left={left_term}")
            result_list = re.findall(FAIRSHARE_pattern, left_term)
            #logging.info(f"type(result_list)={type(result_list)}")
            if len(result_list) > 0:
                #print(f"{left_term} -------in match: {result_list[0]}")
                clean_left_set.add(result_list[0])
            else:
                result_list = re.findall(doi_pattern, left_term)
                if len(result_list) > 0:
                    clean_left_set.add(left_term)
                else:
                    not_matched_set.add(left_term)
        logger.info(f"no matches for len={len(not_matched_set)} elements={not_matched_set}")
        logger.info(f"clean_FAIR_DOI_set output len={len(clean_left_set)}")
        return clean_left_set

    left_set = clean_FAIR_DOI_set(left_set)
    right_set = clean_FAIR_DOI_set(right_set)

    logger.info(f"----------AFTER CLEANING OF THE DOI to use SUFFIX------------------")
    print(f"counts: left={len(left_set)} right={len(right_set)}")
    print(f"intersection: len={len(left_set.intersection(right_set))}")
    print(f"intersection: {left_set.intersection(right_set)}")
    print(f"unique to right list:len=({len(right_set.difference(left_set))}) values={right_set.difference(left_set)}")


def do_standards_reporting(all_filtered_df):
    """

    :param all_filtered_df:
    :return:
    """
    print("-------------------get standards------------------------------------")
    standard_types = ['identifier_schema', 'journal', 'model_and_format', 'reporting_guideline', 'research and development programme', 'terminology_artefact']
    standard_types_str = "|".join(map(re.escape, standard_types))
    standards_df = all_filtered_df[all_filtered_df["Type"].str.contains(standard_types_str, case = False)]

    logger.info(f"standards_df len={len(standards_df)}")

    out_file = "standards_reporting.tsv"
    logging.info(f"out_file={out_file}")
    ffs = sorted(standards_df["Standard"].unique())
    with open(out_file, "w") as outfile:
        for ff in ffs:
            # print(ff)
            outfile.write(f"{ff}\n")
    logging.info(f"out_file={out_file}")
    logger.info(f"all_filtered_df columns={all_filtered_df.columns}")
    doi_latest_list = list(all_filtered_df["doi"].unique())
    logger.info(f"doi_latest_list={doi_latest_list}")
    compare2lists(doi_latest_list, standard_doi_2024_May_list)


def mine_existing_data():
    logging.info("in mine_existing_data")
    search_query_dict = get_search_query_dict()

    logging.info(search_query_dict)

    my_records = []

    # this was from May 2024
    # for search_entry in search_query_dict:
    #     logging.info("----------------------------------------------------------------------")
    #     logging.info(f"search_term={search_query_dict[search_entry]['query']}")
    #     logging.info(f"outfile={search_query_dict[search_entry]['outfile']}")
    #     fairshare_json = json.load(open(search_query_dict[search_entry]['outfile']))
    #     my_records = process_query_out_json(my_records, fairshare_json['data'], search_query_dict[search_entry]['query'])
    #     logging.info(f"len of my_records={len(my_records)}")

    my_records = mine_all(my_records)

    df = pd.DataFrame(my_records)
    df = df.replace("\n", " ", regex = True)

    df = merge_on_column(df, 'search_term', 'Standard')
    print(df.head())
    logger.info(df['Type'].value_counts())

    logger.info(f"{df['Domains'].value_counts()}")

    outfile = "all_fairshare_records.tsv"
    logging.info(outfile)
    df.to_csv(outfile, sep='\t', index = False)

    # filtering for relevant terms
    logger.info(f"relevant_topics_array: {relevant_topics_array}")
    relevant_topics = "|".join(relevant_topics_array)
    filtered_df = df[df['Subject'].str.contains(relevant_topics, case=False )]
    other_filtered_df = df[df['Other subjects'].str.contains(relevant_topics, case=False )]
    domain_filtered_df = df[df["Domains"].str.contains(relevant_topics, case = False)]
    desc_topics = "|".join(desc_topics_array)
    description_filtered_df = df[df["Description"].str.contains(desc_topics, case = False)]
    logger.info(f"description_filtered_df total={len(description_filtered_df)}")
    logger.info(description_filtered_df.head())
    # print({description_filtered_df['Description'].unique})
    # sys.exit()
    all_filtered_df =  pd.concat([filtered_df, other_filtered_df, domain_filtered_df, description_filtered_df], ignore_index=True)
    all_filtered_df = all_filtered_df.drop_duplicates(keep = 'first').reset_index(drop=True)
    # logger.info(all_filtered_df.head(5).transpose().to_string(index=True))
    logger.info(all_filtered_df.head(2).to_string(index = True))
    logger.info(f"start={len(df)}   filtered={len(filtered_df)} end={len(all_filtered_df)}")

    tmp_df = all_filtered_df[["Type", "Domains", "Subject"]]
    logger.info(tmp_df)

    # print(sorted(set(tmp_df["Domains"])))
    # get_count_of_individual_terms(tmp_df["Domains"])
    #
    # sys.exit()

    logger.info(f"cols={list(filtered_df.columns)}")
    # logger.info(f"{all_filtered_df['Subject'].value_counts()}")
    print("---------------Subject---------------")
    get_count_of_individual_terms(all_filtered_df['Subject'].to_list())
    print("---------------Other subjects---------------")
    logger.info(f"Other subjects={all_filtered_df['Other subjects'].to_list()}")
    get_count_of_individual_terms(all_filtered_df['Other subjects'].to_list())


    type_sets = ["terminology_artefact", "model_and_format", "reporting_guideline", "identifier_schema"]
    for type in type_sets:
        print(f"-----------{type}-------------")
        df_standards = df.query('Type == @type')
        if len(df_standards) > 0:
            print(df_standards.groupby(['search_term', 'Standard', 'Type']).size().to_frame('record_count').reset_index())
        # print(df_standards['Standard'])

    # print("---------------TESTING---------------")
    # tmp_df = all_filtered_df.head(3)
    # print(tmp_df.to_markdown())
    # tmp_df = annotate_hit_search_words(tmp_df)
    # print(tmp_df.to_markdown())
    # sys.exit()
    all_filtered_df = annotate_hit_search_words(all_filtered_df)

    outfile = data_dir + "/all_filtered.xlsx"
    logger.info(outfile)
    all_filtered_df.to_excel(outfile, index=False)

    outfile = data_dir + "/all_filtered.tsv"
    logger.info(outfile)
    all_filtered_df.to_csv(outfile, sep='\t', index=False)

    do_standards_reporting(all_filtered_df)




def get_search_query_dict():
    # searching is case insensitive,
    search_query_dict = {
                 "biodiversity": { "query": "biodiversity ", "outfile": data_dir + "/biodiversity.json"},
                 "tax_class": {"query": "Taxonomic classification", "outfile": data_dir + "/taxonomic_classification.json"},
                 "ecosystem": {"query": "ecosystem",  "outfile": data_dir + "/ecosystem.json"},
                 "biological_sample": {"query": "biological sample", "outfile": data_dir + "/biological_sample.json"},
                 "abundance": {"query": "abundance", "outfile": data_dir + "/abundance.json"},
                 "occurrence": {"query": "occurrence", "outfile": data_dir + "/occurrence.json"}
            }
    search_query_dict = {
             "biodiversity": { "query": "biodiversity ", "outfile": data_dir + "/biodiversity.json"},
        "subjects=biodiversity": {"query": "subjects=biodiversity", "outfile": data_dir + "/subjects_biodiversity.json"},
            "biodiversity": {"query": "q=biodiversity", "outfile": data_dir + "/biodiversity.json"},
        "subject=biodiversity": {"query": "subject=biodiversity",
                                  "outfile": data_dir + "/subject_biodiversity.json"},
        "biodiversity": {"query": "q=biodiversity", "outfile": data_dir + "/biodiversity.json"},
        "tax_class": {"query": "q=Taxonomic classification",
                      "outfile": data_dir + "/taxonomic_classification.json"},
        "ecosystem": {"query": "q=ecosystem", "outfile": data_dir + "/ecosystem.json"},
        "biological_sample": {"query": "q=biological sample", "outfile": data_dir + "/biological_sample.json"},
        "abundance": {"query": "q=abundance", "outfile": data_dir + "/abundance.json"},
        "occurrence": {"query": "q=occurrence", "outfile": data_dir + "/occurrence.json"}
    }

    search_query_dict = {

        # "subjects=database": {"query": "q=biodiversity and fairsharing_registry=database",
        #                           "outfile": data_dir + "/database.json"},
        # "q=database": {"query": "q=biodiversity&fairsharing_registry=database",
        #                       "outfile": data_dir + "/bio_database.json"},
        # "recordType=identifier_schema": {"query": "recordType=identifier_schema",
        #                "outfile": data_dir + "/identifier_schema.json"}
        # "recordType=identifier_schema": {"query": "q=identifier_schema",
        #                                  "outfile": data_dir + "/identifier_schema.json"}

        "biodiversity": {"query": "biodiversity ", "outfile": data_dir + "/biodiversity.json"},
        "subjects=biodiversity": {"query": "subjects=biodiversity",
                                  "outfile": data_dir + "/subjects_biodiversity.json"},
    }
    # search_query_dict = {
    #     "subject=biodiversity": {"query": "record_type=Policy", "outfile": data_dir + "/policy.json"}
    #
    #
    # }

    return search_query_dict
def do_searches(jwt):
    logging.info("Doing searches")
    base_url = "https://api.fairsharing.org/search//fairsharing_records"
    # base_url = "https://api.fairsharing.org/search/record_types"

    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': "Bearer {0}".format(jwt),
    }

    search_query_dict = get_search_query_dict()


    for search_entry in search_query_dict:
        logging.info("----------------------------------------------------------------------")
        logging.info(search_query_dict[search_entry])
        search_term = search_query_dict[search_entry]['query']
        logging.info(f"search_term--->{search_term}<---")

        FFS=False
        if  FFS: # os.path.isfile(search_query_dict[search_entry]['outfile']):
            logging.info(f"  This already exists {search_query_dict[search_entry]['outfile']} so will omit the search")
            my_json_file = search_query_dict[search_entry]['outfile']
            with open(my_json_file, 'r') as json_file:
                json_response = json.load(json_file)
        else:
            url = base_url + '?' + search_term
            logging.info(url)

            # response = requests.request("POST", url, headers = headers)
            response = requests.request("GET", url, headers = headers)
            json_response = json.loads(response.text)
            test_response(response)
            logging.debug(response.text)
            logging.info(f"writing to {search_query_dict[search_entry]['outfile']}")
            with open(search_query_dict[search_entry]['outfile'], "w") as outfile:
                json.dump(response.json(), outfile)

        logging.debug(json.dumps(json_response))
        logging.info(f"length of response,json={len(json_response)}")
        my_records = process_query_out_json([], json_response['data'], search_query_dict[search_entry]['query'])
        df = pd.DataFrame(my_records)
        logging.info(df.head(1))
        if len(df) >0:
            logging.info(df['Type'].value_counts())
def main():
    ###################################################
    url = "https://api.fairsharing.org/users/sign_in"

    username = os.environ['emailaddress']
    password = os.environ['fairshare_pass']

    payload = {"user": {"login": username, "password": password}}
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    ###################################################


    response = requests.request("POST", url, headers = headers, data = json.dumps(payload))

    # Get the JWT from the response.text to use in the next part.
    data = response.json()
    jwt = data['jwt']

    # sys.exit(print(jwt))

    if args.test_connection:
        simple_test(jwt, url)
    elif args.mine:
        mine_existing_data()
    elif args.all:
        get_all_data(jwt)
    else:
        do_searches(jwt)


if __name__ == '__main__':
    # Read arguments from command line
    prog_des = "Script to test using the FAIRSHARING API"

    parser = argparse.ArgumentParser(description = prog_des)

    # Adding optional argument, n.b. in debugging mode in IDE, had to turn required to false.
    parser.add_argument("-d", "--debug_status",
                        help = "Debug status i.e.True if selected, is verbose",
                        required = False, action = "store_true")
    parser.add_argument("-t", "--test_connection",
                        help = "test the connnection",
                        required = False, action = "store_true")

    parser.add_argument("-m", "--mine",
                        help = "mine the existing queries",
                        required = False, action = "store_true")
    parser.add_argument("-a", "--all",
                        help = "grab all existing records",
                        required = False, action = "store_true")
    parser.parse_args()
    args = parser.parse_args()

    if args.debug_status:
        logging.basicConfig(level = logging.DEBUG)
        logging.info(prog_des)
    else:
        logging.basicConfig(level = logging.INFO)
    logger = logging.getLogger(name = 'mylogger')

    main()


