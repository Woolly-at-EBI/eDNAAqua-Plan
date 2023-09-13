#!/usr/bin/env python3
"""Script of sample_collection.py is to sample_collection.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-07
__docformat___ = 'reStructuredText'
chmod a+x sample_collection.py
"""


from icecream import ic
import sys
import os
import argparse
import random
from sample import Sample
from ena_portal_api import ena_portal_api_call
from taxonomy import generate_taxon_collection, taxon
from datetime import datetime
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

class SampleCollection:

    def __init__(self):
        self.type = "SampleCollection"
        self.sample_obj_dict = {}
        self.environmental_sample_set = set()
        self.environmental_study_accession_set = set()
        self.european_environmental_set = set()
        self.european_sample_set = set()
        self.tax_id_set = set()
        self.sample_fields = ['sample_accession', 'description', 'study_accession', 'environment_biome', 'tax_id', 'taxonomic_identity_marker', 'country', 'location_start', 'location_end']
        self.total_archive_sample_size = self.get_total_archive_sample_size()

    def put_sample_set(self, sample_set):
        self.sample_set = sample_set


    def get_total_archive_sample_size(self):
       url='https://www.ebi.ac.uk/ena/portal/api/count?result=sample&dataPortal=ena'
       (total, response) = ena_portal_api_call(url, {}, "sample", "")
       ic(total)
       return total

    def get_sample_coll_df(self):
        """
        put all into a big column orientated dict. Tried to do in a field independent way
        then generate the df.
        There is probably a more efficient way to do this.
        :return:
        """
        print("++++++++++++++++++++++++++++++++++++++++++++")
        if hasattr(self, 'sample_df'):
            return self.sample_df
        else:

            count =0
            columns_list = []
            coll_dict = {}
            for sample_obj in self.sample_set:
                sample_dict = sample_obj.get_summary_dict()
                if count == 0:   # first time around
                    columns_list = sorted(sample_dict.keys())
                    for field in columns_list:
                        coll_dict[field] = []
                for field in columns_list:
                    coll_dict[field].append(sample_dict[field])
                count += 1
            coll_df = pd.DataFrame.from_dict(coll_dict)
            self.sample_df = coll_df
            return self.sample_df
    def addTaxonomyAnnotation(self):
        """

        :return:
        """
        for sample_obj in self.sample_set:
            self.tax_id_set.add(sample_obj.tax_id)
        tax_id_list = sorted(self.tax_id_set)
        ic(tax_id_list)
        taxon_collection_obj = generate_taxon_collection(tax_id_list)
        for sample_obj in self.sample_set:
            ic(sample_obj.tax_id)
            taxonomy_obj = taxon_collection_obj.get_taxon_obj_by_id(sample_obj.tax_id)
            if taxonomy_obj and hasattr(taxonomy_obj, 'tax_id'):
                sample_obj.taxonomy_obj = taxonomy_obj
                ic(sample_obj.taxonomy_obj.tax_id)
            else:
                ic(f"Warning: for {sample_obj.tax_id} generating a dummy")
                sample_obj.taxonomy_obj = taxon({'tax_id': ''})  # generates a dummy


    def print_summary(self):
        outstring = f"Run date={datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')}\n"
        outstring += f"sample_set_size={len(self.sample_set)}\n"
        outstring += f"total_ena_sample_size={self.total_archive_sample_size}\n"
        outstring += f"total_ena_tax_id_count={len(self.tax_id_set)}\n"
        outstring += f"environmental_sample_total: {len(self.get_environmental_sample_list())}\n"
        outstring += f"European_environmental_sample_total: {len(self.european_environmental_set)}\n"
        outstring += f"European_sample_total: {len(self.european_sample_set)}\n"
        outstring += f"environmental_study_total: {len(self.get_environmental_study_accession_list())}\n"


        outstring += f"sample_dict_size={len(self.sample_obj_dict)}\n"
        outstring +='#####################################\n'
        sample_obj1 = random.choice(list(self.sample_set))
        outstring += f"Random sample: {sample_obj1.print_values()}\n"

        print('#####################################')
        sample_obj2 = random.choice(list(self.sample_set))
        outstring += f"Random sample: {sample_obj2.print_values()}\n"

        print('#####################################')
        sample_obj3 = random.choice(list(self.sample_set))
        outstring += f"Random sample: {sample_obj3.print_values()}\n"


        return outstring

    def get_sample_collection_stats(self):

        if hasattr(self,"sample_collection_stats_dict"):
            return self.sample_collection_stats_dict
        else:
            sample_collection_stats_dict = {'by_sample_id': {}, 'by_study_id': {}}


            for sample_obj in self.sample_set:
                sample_collection_stats_dict['by_sample_id'][sample_obj.sample_accession] = \
                    {
                        "sample_accession": sample_obj.sample_accession,
                         "study_accession": sample_obj.study_accession,
                         "is_environmental_sample": sample_obj.is_environmental_sample
                      }
                if sample_obj.is_environmental_sample:
                    print(".", end="")
                    self.environmental_sample_set.add(sample_obj)
                    if sample_obj.country_is_european:
                        self.european_environmental_set.add(sample_obj)
                if sample_obj.country_is_european:
                        self.european_sample_set.add(sample_obj)
                # ic(sample_collection_stats_dict['by_study_id'])
                if sample_obj.study_accession != "":
                    for study_accession in sample_obj.study_accession.split(';'):
                      sample_collection_stats_dict['by_study_id'][study_accession] = {'sample_id': { sample_obj.sample_accession : sample_collection_stats_dict['by_sample_id'][sample_obj.sample_accession]} }
                      self.environmental_study_accession_set.add(study_accession)

                self.sample_collection_stats_dict = sample_collection_stats_dict
            self.sample_count = len(sample_collection_stats_dict['by_sample_id'])
            # ic(self.sample_collection_stats_dict)
        return self.sample_collection_stats_dict

    def get_environmental_sample_list(self):
        """
          list of object tagged with environment_sample in ENA
        :return:
        """
        return list(self.environmental_sample_set)

    def get_environmental_study_accession_list(self):
        return list(self.environmental_study_accession_set)
def main():
    pass

if __name__ == '__main__':
    ic()
    main()
