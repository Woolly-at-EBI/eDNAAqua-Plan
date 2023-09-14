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

from itertools import islice
from sample_collection import SampleCollection
from sample import Sample
from geography import Geography
from ena_portal_api import ena_portal_api_call

ena_project_dir = "/Users/woollard/projects/eDNAaquaPlan/eDNAAqua-Plan/"
ena_data_dir = ena_project_dir + "data/ena_in/"
ena_data_out_dir = ena_project_dir + "data/out/"
# Define the ENA API URL
ena_api_url = "https://www.ebi.ac.uk/ena/portal/api"


def encode_accession_list(id_list):
    """
    accessions_html_encoded = encode_accession_list(chunk_sample_id_list)
    :param id_list:
    :return:
    """
    return '%2C%20%20'.join(id_list)



def do_portal_api_sample_call(result_object_type, query_accession_ids, return_fields):
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
    (data, response) = ena_portal_api_call(my_url, params, result_object_type, query_accession_ids)

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
    geography = Geography()

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
               if 'taxonomic_identity_marker' in data_by_id[obj.sample_accession]:
                   if data_by_id[obj.sample_accession]['taxonomic_identity_marker'] != "":
                      obj.taxonomic_identity_marker = data_by_id[obj.sample_accession]['taxonomic_identity_marker']
               if 'tax_id' in data_by_id[obj.sample_accession]:
                   obj.tax_id = data_by_id[obj.sample_accession]['tax_id']

               if 'country' in data_by_id[obj.sample_accession]:
                   obj.country = data_by_id[obj.sample_accession]['country']
                   obj.country_clean = geography.clean_insdc_country_term(obj.country)
                   if obj.country_clean != "":
                       obj.country_is_european = geography.is_insdc_country_in_europe(obj.country_clean)
               if 'location_start' in data_by_id[obj.sample_accession]:
                   obj.location_start = data_by_id[obj.sample_accession]['location_start']
               if 'location_end' in data_by_id[obj.sample_accession]:
                   obj.location_end = data_by_id[obj.sample_accession]['location_end']

            else:
                #ic(f"Warning: {obj.sample_accession} not being found in hits")
                pass
            # print(obj.print_values())

    #ic()

def annotate_sample_objs(sample_list, with_obj_type, sample_collection_obj):
    """
     annotate all the sample objects
    :param sample_list:
    :param with_obj_type:
    :return:
    """
    ic()
    ic(with_obj_type)
    sample_rtn_fields = ','.join(sample_collection_obj.sample_fields)
    #ic(','.join(sample_collection_obj.sample_fields))

    API_pre = "https://www.ebi.ac.uk/ena/portal/api/search?result="

    iterator = iter(sample_list)
    chunk_size = 500
    sample_list_size = len(sample_list)
    sample_obj_dict = sample_collection_obj.sample_obj_dict
    # ic(sample_obj_dict)
    chunk_count =    chunk_pos =0
    while chunk := list(islice(iterator, chunk_size)):
        chunk_count +=1
        chunk_pos += chunk_size
        if chunk_count % 100 == 0:
           ic(f"{chunk_pos}/{sample_list_size}")
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
            return_fields = sample_rtn_fields
            sample_ena_data = do_portal_api_sample_call(with_obj_type, chunk_sample_id_list, return_fields)
            add_info_to_object_list(with_obj_type, sample_obj_dict, sample_ena_data)
    ic()
    if with_obj_type == "sample":
       sample_collection_obj.addTaxonomyAnnotation()
       ic("just added taxonomyAnnotation")
       sample_collection_obj.get_sample_collection_stats()
       ic()
       print(sample_collection_obj.print_summary())

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
    limit_length=1000
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

    # for sample_obj in sample_set:
    #     print(sample_obj.print_values())

    print("\n+++++++++++++++++++++++++++++++++++")
    print("************** Summary of the ENA samples **************\n")
    print(sample_collection_obj.print_summary())
    print("+++++++++++++++++++++++++++++++++++")

    ic(sample_collection_obj.environmental_study_accession_set)
    ic(len(sample_collection_obj.environmental_study_accession_set))

    ic("..............")
    ic(sample_collection_obj.get_sample_coll_df())

    ena_env_sample_df_file = ena_data_out_dir + "ena_env_sample_df.parquet"
    ic(f"writing {ena_env_sample_df_file}")
    df = sample_collection_obj.get_sample_coll_df()
    df.to_parquet(ena_env_sample_df_file)


    return sample_collection_obj


def main():
    sample_collection_obj = SampleCollection()
    sample_analysis(sample_collection_obj)
    sample_set = sample_collection_obj.sample_set
    ic(len(sample_set))

    ic("******* END OF MAIN *******")


if __name__ == '__main__':
    ic()
    main()
