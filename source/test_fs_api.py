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

from statsmodels.stats.descriptivestats import Description

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


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
        logging.info(f"record_set id={record_set['id']} {record_set['attributes']['metadata']['name']} type={record_set['type']}")
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
    logging.debug("inside process_query_out_json")
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
    #logging.info("merge on standard")
    #logging.info("What is coming in")
    #logging.info(df.head(2))
    #logging.info(len(df))
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
    #logging.info("What is leaving")
    #logging.info(len(df))
    df['search_term'] = ['; '.join(v) for v in cmnts.values()]

    return df

def mine_existing_data():
    search_query_dict = get_search_query_dict()
    logging.info("in mine_existing_data")
    my_records = []
    for search_entry in search_query_dict:
        logging.info("----------------------------------------------------------------------")
        logging.info(f"search_term={search_query_dict[search_entry]['query']}")
        logging.info(f"outfile={search_query_dict[search_entry]['outfile']}")
        fairshare_json = json.load(open(search_query_dict[search_entry]['outfile']))
        my_records = process_query_out_json(my_records, fairshare_json['data'], search_query_dict[search_entry]['query'])
        logging.info(f"len of my_records={len(my_records)}")
        continue

    df = pd.DataFrame(my_records)

    df = merge_on_column(df, 'search_term', 'Standard')
    print(df.head())
    logging.info(df['Type'].value_counts())

    type_sets = ["terminology_artefact", "model_and_format", "reporting_guideline", "identifier_schema"]
    for type in type_sets:
        print(f"-----------{type}-------------")
        df_standards = df.query('Type == @type')
        print(df_standards.groupby(['search_term', 'Standard', 'Type']).size().to_frame('record_count').reset_index())
        # print(df_standards['Standard'])


    outfile = "test_fs_api.xlsx"
    logging.info(outfile)
    df.to_excel(outfile, index=False)


def get_search_query_dict():
    # searching is case insensitive,
    search_query_dict = {
                 "biodiversity": { "query": "biodiversity ", "outfile": "../data/biodiversity/biodiversity.json"},
                 "tax_class": {"query": "Taxonomic classification", "outfile": "../data/biodiversity/taxonomic_classification.json"},
                 "ecosystem": {"query": "ecosystem",  "outfile": "../data/biodiversity/ecosystem.json"},
                 "biological_sample": {"query": "biological sample", "outfile": "../data/biodiversity/biological_sample.json"},
                 "abundance": {"query": "abundance", "outfile": "../data/biodiversity/abundance.json"},
                 "occurrence": {"query": "occurrence", "outfile": "../data/biodiversity/occurrence.json"}
            }
    search_query_dict = {
             "subject=biodiversity": {"query": "subject=biodiversity", "outfile": "../data/biodiversity/subject_biodiversity.json"},
            "biodiversity": {"query": "biodiversity", "outfile": "../data/biodiversity/biodiversity.json"},
        "tax_class": {"query": "Taxonomic classification",
                      "outfile": "../data/biodiversity/taxonomic_classification.json"},
        "ecosystem": {"query": "ecosystem", "outfile": "../data/biodiversity/ecosystem.json"},
        "biological_sample": {"query": "biological sample", "outfile": "../data/biodiversity/biological_sample.json"},
        "abundance": {"query": "abundance", "outfile": "../data/biodiversity/abundance.json"},
        "occurrence": {"query": "occurrence", "outfile": "../data/biodiversity/occurrence.json"}
    }

    return search_query_dict
def do_searches(jwt):
    logging.info("Doing searches")
    base_url = "https://api.fairsharing.org/search/fairsharing_records"

    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': "Bearer {0}".format(jwt),
    }

    search_query_dict = get_search_query_dict()


    for search_entry in search_query_dict:
        logging.info("----------------------------------------------------------------------")
        search_term = search_query_dict[search_entry]['query']
        logging.info(f"search_term={search_term}")
        url = base_url + '?q=' + search_term
        if search_term.startswith('subject='):
            url = base_url + '?' + search_term
        logging.info(url)


        response = requests.request("POST", url, headers = headers)
        test_response(response)
        logging.debug(response.text)
        logging.info(f"writing to {search_query_dict[search_entry]['outfile']}")
        with open(search_query_dict[search_entry]['outfile'], "w") as outfile:
            json.dump(response.json(), outfile)

        logging.debug(json.dumps(response.json()))
        logging.info(f"length of response,json={len(response.json())}")
        my_records = process_query_out_json([], response.json()['data'], search_query_dict[search_entry]['query'])
        df = pd.DataFrame(my_records)
        logging.info(df.head(1))
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

    if args.test_connection:
        simple_test(jwt, url)
    elif args.mine:
        mine_existing_data()
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
    parser.parse_args()
    args = parser.parse_args()

    if args.debug_status:
        logging.basicConfig(level = logging.DEBUG)
        logging.info(prog_des)
    else:
        logging.basicConfig(level = logging.INFO)

    main()


