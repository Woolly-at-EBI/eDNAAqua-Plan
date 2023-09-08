#!/usr/bin/env python3
"""Script of ena_portal_api.py is to ena_portal_api.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-08
__docformat___ = 'reStructuredText'
chmod a+x ena_portal_api.py
"""


from icecream import ic
import os
import argparse

import requests
import json
def ena_portal_api_call(url, params, result_object_type, query_accession_ids):
    """

    :param url:
    :param params:
    :param result_object_type:
    :param query_accession_ids:
    :return:
    """
    response = requests.get(url, params)
    #ic(url)
    #ic(params)

    data = []
    if response.status_code == 200:
        # Parse the JSON response
        # ic(response)
        # ic(response.text)
        data = json.loads(response.text)
        #ic(data)

        # check if any hits
        if type(data) is int:
            pass
        elif len(data) <= 0:
            print(f"WARNING: {result_object_type} {query_accession_ids} no results found")
    else:
        print(f"Error: Unable to fetch data for {result_object_type} {query_accession_ids}")
    return data, response

def main():
    url = 'https://www.ebi.ac.uk/ena/portal/api/count?result=sample&dataPortal=ena'
    ena_portal_api_call(url, {}, "sample", "")


if __name__ == '__main__':
    ic()
    main()
