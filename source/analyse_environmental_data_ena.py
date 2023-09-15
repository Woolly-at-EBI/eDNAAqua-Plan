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
from sample_collection import SampleCollection, get_sample_field_data
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
    sample_obj_dict = sample_collection_obj.sample_obj_dict

    for sample in sample_list:
        ic(sample.sample_accession)
        sample_obj_dict[sample.sample_accession] = sample

    all_sample_data = get_sample_field_data(sample_list, sample_rtn_fields)
    for sample_ena_data in all_sample_data:
        add_info_to_object_list(with_obj_type, sample_obj_dict, sample_ena_data)
    ic()
    if with_obj_type == "sample":
       sample_collection_obj.addTaxonomyAnnotation()
       sample_collection_obj.get_sample_collection_stats()
       ic()
       print(sample_collection_obj.print_summary())

    return


def get_environmental_sample_list():
    """
    all from the ena_expt_searchable_EnvironmentalSample_summarised are EnvironmentalSample tagged in the ENA archive!
    :return:
    """
    infile = ena_data_dir + "/" + "ena_expt_searchable_EnvironmentalSample_summarised.txt"
    sample_env_df = pd.read_csv(infile, sep = '\t')
    # ic(sample_env_df.head())
    env_sample_list = sample_env_df['sample_accession'].to_list()
    return sample_env_df['sample_accession'].to_list()

def sample_analysis(sample_list):
    """
    """
    ic()
    sample_collection_obj = SampleCollection()
    limit_length = 10
    sample_list = sample_list[0:limit_length]
    ic(len(sample_list))
    count = 0
    sample_set = set()
    for sample_accession in sample_list:
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
    if sample_collection_obj.get_sample_set_size() <= 0:
        print("ERROR: Sample_set size is 0, so something serious has gone wrong with the code or data...")
        sys.exit()
    else:
        ic(sample_collection_obj.get_sample_set_size() )


    annotate_sample_objs(list(sample_set), "sample", sample_collection_obj)

    sample_collection_obj.get_sample_collection_stats()

    # for sample_obj in sample_set:
    #     print(sample_obj.print_values())

    print("\n+++++++++++++++++++++++++++++++++++")
    print("************** Summary of the ENA samples **************\n")
    print(sample_collection_obj.print_summary())
    print("+++++++++++++++++++++++++++++++++++")

    ic(len(sample_collection_obj.environmental_study_accession_set))
    print(", ".join(sample_collection_obj.environmental_study_accession_set))

    ic("..............")
    ic(sample_collection_obj.get_sample_coll_df())

    ena_env_sample_df_file = ena_data_out_dir + "ena_env_sample_df.parquet"
    ic(f"writing {ena_env_sample_df_file}")
    df = sample_collection_obj.get_sample_coll_df()
    df.to_parquet(ena_env_sample_df_file)

    return sample_collection_obj


def main():
    env_sample_acc_list = get_environmental_sample_list()
    sample_collection_obj = sample_analysis(env_sample_acc_list)
    sample_set = sample_collection_obj.sample_set
    ic(len(sample_set))

    ic("******* END OF MAIN *******")


if __name__ == '__main__':
    ic()
    main()
