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
import sys

def get_ena_portal_url():
    return "https://www.ebi.ac.uk/ena/portal/api/"

def ena_portal_api_call_basic(url):
    """
    Allows a basic URL call with little error detection
    :param url:
    :return:
    """

    #ic(url)
    response = requests.get(url)
    # print(f"content={response.content}")
    # ic(type(response.content))
    # print(f"content={response.text}")
    # sys.exit()
    # data = []

    if response.status_code == 200:  # i.e. ok
        # ic(response.status_code)
        # Parse the JSON response
        # ic(response)
        # ic(response.text)
        data = response.text
    else:
        print(f"Error: Unable to fetch data for {url} because {response}")
        sys.exit()
    return data, response

def ena_portal_api_call(url, params, result_object_type, query_accession_ids):
    """
    URL API call allowing slightly more complex situations than ena_portal_api_call_basic i.e. using params
    :param url:
    :param params:
    :param result_object_type:  #don't use it just for debugging
    :param query_accession_ids:  #don't use it just for debugging
    :return:
    """
    #ic()
    response = requests.get(url, params)
    #ic(url)
    #ic(params)

    data = []
    if response.status_code == 200:  # i.e. ok
        #ic(response.status_code)
        # Parse the JSON response
        # ic(response)
        # ic(response.text)
        data = json.loads(response.text)
        #ic(data)

        # check if any hits
        if type(data) is int:
            #ic("data type is okay!")
            pass
        elif len(data) <= 0:
            print(f"WARNING: {result_object_type} {query_accession_ids} no results found")
    else:
            print(f"Error: Unable to fetch data for {result_object_type} {query_accession_ids} because {response}")
    return data, response

def main():
    url = 'https://www.ebi.ac.uk/ena/portal/api/count?result=sample&dataPortal=ena'
    ena_portal_api_call(url, {}, "sample", "")


if __name__ == '__main__':
    ic()
    main()
