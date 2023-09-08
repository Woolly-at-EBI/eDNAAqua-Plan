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
        self.tax_id = ""
        self.environment_biome = ""
        self.taxonomic_identity_marker = ""
        self.country = ""  # country	locality of sample isolation
        self.location_start = ""
        self.location_end = ""

    def setEnvironmentalSample(self, boolean_flag):
        """
        this is what is tagged in ENA archive uner experiment.environmental_sample
        :param boolean_flag:
        :return:
        """
        self.environmental_sample = boolean_flag

    def print_values(self):
        out_string = f"    sample_accession: {self.sample_accession}\n"
        out_string += f"    environmental_sample: {self.environmental_sample}\n"
        out_string += f"    study_accession: {self.study_accession}\n"
        out_string += f"    description: {self.description}\n"
        out_string += f"    tax_id: {self.tax_id}\n"
        out_string += f"    environment_biome: {self.environment_biome}\n"
        out_string += f"    taxonomic_identity_marker: {self.taxonomic_identity_marker}\n"
        out_string += f"    country: {self.country}\n"
        out_string += f"    location_start: {self.location_start}\n"
        out_string += f"    location_end: {self.location_end}\n"
        return out_string


def main():
    test_id="test_id"
    sample = Sample(test_id)

if __name__ == '__main__':
    ic()
    main()
