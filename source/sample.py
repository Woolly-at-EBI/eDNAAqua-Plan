#!/usr/bin/env python3
"""Script of sample.py is to sample.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-07
__docformat___ = 'reStructuredText'
chmod a+x sample.py
"""


from icecream import ic
import os
import argparse


class Sample:
    """
    objects for storing the environmental status of each sample
    They also get much annotation added by other function,
    """

    def __init__(self, sample_accession):
        self.sample_accession = sample_accession
        self.study_accession = ""
        self.description = ""

    def setEnvironmentalSample(self, boolean_flag):
        """

        :param boolean_flag:
        :return:
        """
        self.environmental_sample = boolean_flag


    def print_values(self):
        out_string = f"sample_accession: {self.sample_accession}\n"
        out_string += f"environmental_sample: {self.environmental_sample}\n"
        out_string += f"study_accession: {self.study_accession}\n"
        out_string += f"description: {self.description}\n"
        return out_string


def main():
    pass

if __name__ == '__main__':
    ic()
    main()
