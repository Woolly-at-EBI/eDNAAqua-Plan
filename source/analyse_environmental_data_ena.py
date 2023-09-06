#!/usr/bin/env python3
"""Script of analyse_environmental_data_ena.py is to analyse_environmental_data_ena.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-06
__docformat___ = 'reStructuredText'
chmod a+x analyse_environmental_data_ena.py
"""

from icecream import ic
import os
import argparse
import pandas as pd
ena_data_dir = "../data/ena_in"

class Sample:
    """
    objects for storing the environmental status of each sample
    """
    def __init__(self, sample_accession_id):
        self.sample_accession_id = sample_accession_id
    def setEnvironmentalSample(self, boolean_flag):
        """

        :param boolean_flag:
        :return:
        """
        self.EnvironmentalSample=boolean_flag


def sample_analysis():
    """"""
    ic()
    infile=ena_data_dir + "/" + "ena_sample_searchable_EnvironmentalSample_summarised.txt"
    sample_env_df = pd.read_csv(infile, sep='\t')
    ic(sample_env_df.head())
    env_sample_list=sample_env_df['sample_accession'].to_list()
    count=0
    sample_set = set()
    for sample_accession_id in  env_sample_list:
        sample = Sample(sample_accession_id)
        sample_set.add(sample)
        sample.setEnvironmentalSample(True)
        ic(sample.sample_accession_id)
        ic(sample.EnvironmentalSample)

        if count >3:
            break
        count += 1
    #
    # ic("++++++++++++++++++++++++++++++++++++++")
    # for sample in sample_set:
    #     ic(sample.sample_accession_id)
    #     ic(sample.EnvironmentalSample)

    return sample_set



def main():
    sample_set = sample_analysis()
    ic(len(sample_set))

if __name__ == '__main__':
    ic()
    main()
