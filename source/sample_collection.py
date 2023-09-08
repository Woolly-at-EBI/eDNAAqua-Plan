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
from datetime import datetime

class SampleCollection:

    def __init__(self):
        self.type = "SampleCollection"
        self.sample_obj_dict = {}
        self.environmental_sample_set = set()
        self.environmental_study_accession_set = set()
        self.european_environmental_set = set()
        self.european_sample_set = set()
        self.sample_fields = ['sample_accession', 'description', 'study_accession', 'environment_biome', 'tax_id', 'taxonomic_identity_marker', 'country', 'location_start', 'location_end']
        self.total_archive_sample_size = self.get_total_archive_sample_size()

    def put_sample_set(self, sample_set):
        self.sample_set = sample_set

    def get_total_archive_sample_size(self):
       url='https://www.ebi.ac.uk/ena/portal/api/count?result=sample&dataPortal=ena'
       (total,response)= ena_portal_api_call(url, {}, "sample", "")
       ic(total)
       return total

    def print_summary(self):
        outstring = f"Run date={datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')}\n"
        outstring += f"sample_set_size={len(self.sample_set)}\n"
        outstring += f"total_ena_sample_size={self.total_archive_sample_size}\n"
        outstring += f"environmental_sample_total: {len(self.get_environmental_sample_list())}\n"
        outstring += f"European_environmental_sample_total: {len(self.european_environmental_set)}\n"
        outstring += f"European_sample_total: {len(self.european_sample_set)}\n"
        outstring += f"environmental_study_total: {len(self.get_environmental_study_accession_list())}\n"


        outstring += f"sample_dict_size={len(self.sample_obj_dict)}\n"
        outstring +='#####################################\n'
        sample_obj = random.choice(list(self.sample_set))
        outstring += f"Random sample: {sample_obj.print_values()}\n"

        print('#####################################')
        sample_obj = random.choice(list(self.sample_set))
        outstring += f"Random sample: {sample_obj.print_values()}\n"
        print('#####################################')
        sample_obj = random.choice(list(self.sample_set))
        outstring += f"Random sample: {sample_obj.print_values()}\n"
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
