#!/usr/bin/env python3
"""Script of data_utils.py is to provided data_utilities for the other classes here etc.

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-12-04
__docformat___ = 'reStructuredText'
"""

from icecream import ic
import pandas as pd

def get_data_location_dict():
    """

    :return: data_location_dict
    """
    base_dir = '/Users/woollard/projects/eDNAaquaPlan/eDNAAqua-Plan/'
    base_data_dir = base_dir + 'data/'
    data_location_dict = {
        'base_dir': base_dir,
        'base_data_dir': base_data_dir,
        'requirements_dir': base_data_dir + 'requirements_in/'
    }
    return data_location_dict

def get_requirements_df():
    """

    :return: requirements_df
    """
    data_location_dict = get_data_location_dict()
    ic(data_location_dict['requirements_dir'])
    req_xlsx = data_location_dict['requirements_dir'] + 'WP2-WP3_metadata_reqs.xlsx'
    requirements_df = pd.read_excel(req_xlsx, sheet_name=0, index_col='No.')
    return requirements_df

def get_required_metadata_field_list():
    """

    :return: required_metadata_field_list
    """
    requirements_df = get_requirements_df()
    return list(requirements_df['Name'])

def main():
    data_location_dict = get_data_location_dict()
    ic(data_location_dict)
    ic(get_requirements_df())
    ic(get_required_metadata_field_list())

if __name__ == '__main__':
    ic()
    main()
