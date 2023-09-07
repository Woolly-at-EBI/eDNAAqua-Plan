#!/usr/bin/env python3
"""Script of sample_collection.py is to sample_collection.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-07
__docformat___ = 'reStructuredText'
chmod a+x sample_collection.py
"""


from icecream import ic
import os
import argparse

class SampleCollection:

    def __init__(self):
        self.sample_obj_dict = {}


    def put_sample_set(self, sample_set):
        self.sample_set = sample_set

    def print_summary(self):
        outstring = f"sample set size={len(self.sample_set)}\n"
        outstring += f"sample dict size={len(self.sample_obj_dict)}"
        return outstring

def main():
    pass

if __name__ == '__main__':
    ic()
    main()
