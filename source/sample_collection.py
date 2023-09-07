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

class SampleCollection:

    def __init__(self):
        self.sample_obj_dict = {}
        self.environmental_sample_set = set()


    def put_sample_set(self, sample_set):
        self.sample_set = sample_set


    def print_summary(self):
        outstring = f"sample set size={len(self.sample_set)}\n"
        outstring += f"sample dict size={len(self.sample_obj_dict)}\n"
        sample_obj = random.choice(list(self.sample_set))
        outstring += f"Random sample: {sample_obj.print_values()}\n"
        outstring += f"environmental_sample_total: {len(self.get_environmental_sample_list())}\n"
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
                         "environmental_sample": sample_obj.environmental_sample
                      }
                if sample_obj.environmental_sample:
                    print(".", end="")
                    self.environmental_sample_set.add(sample_obj)
                if sample_obj.study_accession != "":
                    sample_collection_stats_dict['by_study_id'][sample_obj.study_accession] = { 'sample_id': { sample_obj.sample_accession : sample_collection_stats_dict['by_sample_id'][sample_obj.sample_accession]} }
                    # ic(sample_collection_stats_dict['by_study_id'])
                self.sample_collection_stats_dict = sample_collection_stats_dict
            self.sample_count = len(sample_collection_stats_dict['by_sample_id'])
            # ic(self.sample_collection_stats_dict)
        print()
        return self.sample_collection_stats_dict

    def get_environmental_sample_list(self):
        """
          list of object tagged with environment_sample in ENA
        :return:
        """
        return list(self.environmental_sample_set)
def main():
    pass

if __name__ == '__main__':
    ic()
    main()
