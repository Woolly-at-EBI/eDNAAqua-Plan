#!/usr/bin/env python3
"""Script of analyse_environmental_data_ena.py is to analyse_environmental_data_ena.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-06
__docformat___ = 'reStructuredText'
chmod a+x analyse_environmental_data_ena.py
"""
import sys

from icecream import ic
import os
import argparse
import pandas as pd
import requests
import json
from itertools import islice
from sample_collection import SampleCollection
from sample import Sample

ena_data_dir = "/Users/woollard/projects/eDNAaquaPlan/eDNAAqua-Plan/data/ena_in"
# Define the ENA API URL
ena_api_url = "https://www.ebi.ac.uk/ena/portal/api"


def encode_accession_list(id_list):
    """
    accessions_html_encoded = encode_accession_list(chunk_sample_id_list)
    :param id_list:
    :return:
    """
    return '%2C%20%20'.join(id_list)


def do_portal_api_call(result_object_type, query_accession_ids, return_fields):
    """

    :param result_object_type:
    :param query_accession_ids:
    :param return_fields:
    :return: data # (as list of row hits) e.g.
       [{'description': 'Waikite Restoration Feature 5',
            'sample_accession': 'SAMEA110453696',
            'study_accession': 'PRJEB55115'},
           {'description': 'Waikite Restoration Feature 3',
            'sample_accession': 'SAMEA110453715',
            'study_accession': 'PRJEB55115'},
           {'description': 'Radiata Pool',
            'sample_accession': 'SAMEA110453701',
            'study_accession': 'PRJEB55115'}]
ic| len(data): 3

    """
    result_object_type
    ena_search_url = f"{ena_api_url}/search"
    # Define the query parameters
    sample_accession = "SAMEA110453686"
    sample_accessions = ','.join(query_accession_ids)
    # "query": f"accession={sample_accession}",
    params = {
        "result": result_object_type,
        "format": "json",
        "fields": return_fields,
        "limit": 0
    }
    my_url = ena_search_url + '?includeAccessions=' + sample_accessions
    # Make a GET request to the ENA API
    # ic(my_url)
    response = requests.get(my_url, params)

    # Check if the request was successful (status code 200)
    data = []
    if response.status_code == 200:
        # Parse the JSON response
        #ic(response)
        #ic(response.text)
        data = json.loads(response.text)
        #ic(data)

        # check if any hits
        if len(data) <= 0:
           print(f"WARNING: {result_object_type} {query_accession_ids} no results found")
    else:
        print(f"Error: Unable to fetch data for {result_object_type} {query_accession_ids}")
    return data

def add_info_to_object_list(with_obj_type, obj_dict, data):
    """

    :param with_obj_type:
    :param obj_dict:
    :param data:
    :return:
    """

    #ic(data)
    data_by_id = {}

    if with_obj_type == "sample":
        for dict_row in data:
            #ic(dict_row)
            data_by_id[dict_row['sample_accession']] = dict_row
    # ic(data_by_id)

    #ic("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    for id in obj_dict:
        obj = obj_dict[id]
        if with_obj_type == "sample":
            if obj.sample_accession in data_by_id:
               if 'description' in data_by_id[obj.sample_accession]:
                  obj.description = data_by_id[obj.sample_accession]['description']
               if 'study_accession' in data_by_id[obj.sample_accession]:
                  obj.study_accession = data_by_id[obj.sample_accession]['study_accession']
               if 'environment_biome' in data_by_id[obj.sample_accession]:
                   obj.environment_biome = data_by_id[obj.sample_accession]['environment_biome']
               if 'tax_id' in data_by_id[obj.sample_accession]:
                   obj.tax_id = data_by_id[obj.sample_accession]['tax_id']
            else:
                #ic(f"Warning: {obj.sample_accession} not being found in hits")
                pass
            # print(obj.print_values())

    ic()



def annotate_sample_objs(sample_list, with_obj_type, sample_collection_obj):
    """

    :param sample_list:
    :param with_obj_type:
    :return:
    """
    ic()

    API_pre = "https://www.ebi.ac.uk/ena/portal/api/search?result="

    iterator = iter(sample_list)
    chunk_size = 500

    sample_obj_dict = sample_collection_obj.sample_obj_dict
    # ic(sample_obj_dict)
    while chunk := list(islice(iterator, chunk_size)):
        #ic("++++++++++++++++++++++++++++++++++++++++++++++++++++")
        chunk_sample_id_list = []
        for sample in chunk:
            # ic(sample.sample_accession)
            chunk_sample_id_list.append(sample.sample_accession)
            sample_obj_dict[sample.sample_accession] = sample
            # ic(sample_obj_dict[sample.sample_accession].sample_accession)
        #ic(chunk_sample_id_list)
        return_fields = ""
        data = []

        if with_obj_type == "study":
            ic(with_obj_type)
            pass
        elif with_obj_type == "sample":
            #ic(with_obj_type)
            #return_fields = "sample_accession,description,study_accession,environment_biome,tax_id,'country locality of sample isolation'"
            return_fields = "sample_accession,description,study_accession,environment_biome,tax_id"
            data = do_portal_api_call(with_obj_type, chunk_sample_id_list, return_fields)
            add_info_to_object_list(with_obj_type, sample_obj_dict, data)
    if with_obj_type == "sample":
       sample_collection_obj.get_sample_collection_stats()
       ic(sample_collection_obj.environmental_study_accession_set)
       ic(len(sample_collection_obj.environmental_study_accession_set))
    return


def sample_analysis(sample_collection_obj):
    """ sample_analysis
    all from the ena_expt_searchable_EnvironmentalSample_summarised are EnvironmentalSample tagged in the ENA archive!
    """
    ic()
    infile = ena_data_dir + "/" + "ena_expt_searchable_EnvironmentalSample_summarised.txt"
    sample_env_df = pd.read_csv(infile, sep = '\t')
    # ic(sample_env_df.head())
    env_sample_list = sample_env_df['sample_accession'].to_list()
    limit_length=3000
    env_sample_list = env_sample_list[0:limit_length]
    ic(len(env_sample_list))
    count = 0
    sample_set = set()
    for sample_accession in env_sample_list:
        sample = Sample(sample_accession)
        sample_set.add(sample)
        sample.setEnvironmentalSample(True)
        #ic(sample.sample_accession)
        #ic(sample.EnvironmentalSample)

        # if count > 3:
        #    break
        #    # pass
        count += 1

    sample_collection_obj.put_sample_set(sample_set)
    annotate_sample_objs(list(sample_set), "sample", sample_collection_obj)

    sample_collection_obj.get_sample_collection_stats()
    print(sample_collection_obj.print_summary())

    # for sample_obj in sample_set:
    #     print(sample_obj.print_values())

    return sample_collection_obj


def main():
    sample_collection_obj = SampleCollection()
    sample_analysis(sample_collection_obj)
    sample_set = sample_collection_obj.sample_set
    ic(len(sample_set))


if __name__ == '__main__':
    ic()
    main()
