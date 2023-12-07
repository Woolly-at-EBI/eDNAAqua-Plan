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
from itertools import islice
import time

def get_ena_portal_url():
    return "https://www.ebi.ac.uk/ena/portal/api/"

def ena_portal_api_call_basic(url):
    """
    Allows a basic URL call with little error detection
    :param url:
    :return:
    """
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
        ic()
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
    response = requests.post(url, params)
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
            ic()
            print(f"url={url}")
            print(f"params={params}")
            print(f"Error: Unable to fetch data for \"{result_object_type}\" {query_accession_ids} because {response} {response.text}")
    return data, response

def urldata2id_set(data, id_col_pos):
        """
        e.g. my_set = urldata2id_set(data,1)  where id_col_pos is indexed from 0
        :param id_col:
        :return:
        """
        ic()
        my_set = set()
        line_count = 0
        for line in data.split("\n"):
            if line_count > 0 and line != "":
                cols = line.split("\t")
                # ic(cols)
                # ic(cols[id_col_pos])
                my_set.add(cols[id_col_pos])
            line_count += 1
        #ic(my_set)
        return my_set
def chunk_portal_api_call(url, with_obj_type, return_fields, include_accession_type, id_list):
    """
    useful for when there could be a long list of ids, that needs to be chunked to not exceed limits.
    N.B. will need to gradually port the other list chunking methods to here!
    passing a URL with a few specific params is critical, as otherwise too much complexity for this
    :param with_obj_type:
    :parma include_accession_type:  # will only sometimes apply if not will be "none:
    :param id_list:
    :param return_fields:   # is a list
    :return: data (as JSON)

    e.g. https://www.ebi.ac.uk/ena/portal/api/search?, {'result': 'read_run', 'includeAccessions': 'SAMD00099297,SAMD00099298,SAMD00099299,SAMD00099303,SAMD00099304,SAMD00099305,SAMD00099306,SAMD00099308,SAMD00099314,SAMD00099317', 'format': 'json', 'fields': 'run_accession,sample_accession', 'limit': 0, 'include_accession_type': 'sample_accession'}, read_run, run_accession,sample_accession
    [{'run_accession': 'DRR111177', 'sample_accession': 'SAMD00099303'}, {'run_accession': 'DRR111178', 'sample_accession': 'SAMD00099304'}, {'run_accession': 'DRR111179', 'sample_accession': 'SAMD00099305'}, {'run_accession': 'DRR111182', 'sample_accession': 'SAMD00099308'}, {'run_accession': 'DRR111188', 'sample_accession': 'SAMD00099314'}, {'run_accession': 'DRR111171', 'sample_accession': 'SAMD00099297'}, {'run_accession': 'DRR111172', 'sample_accession': 'SAMD00099298'}, {'run_accession': 'DRR111173', 'sample_accession': 'SAMD00099299'}, {'run_accession': 'DRR111180', 'sample_accession': 'SAMD00099306'}, {'run_accession': 'DRR111191', 'sample_accession': 'SAMD00099317'}]
    """
    ic()
    #print(f"url={url}\n, ob_type={with_obj_type}\n, rtn_fields={return_fields}\n, id_list len={len(id_list)}\n")
    combined_data = []
    chunk_count = chunk_pos = 0
    list_size = len(id_list)
    iterator = iter(id_list)
    chunk_size = 400  # 400 about the maximum reliable chunk size for including accessions
    ic(f"{chunk_pos}/{list_size}")
    while chunk := list(islice(iterator, chunk_size)):
        chunk_pos += chunk_size
        chunk_count += 1
        if chunk_count % 50 == 0:   #only print progress every X chunks
            ic(f"{chunk_pos}/{list_size} in chunk_portal_api_call()")
        #ic(chunk[0:3])
        params = {
                "result": with_obj_type,
                "includeAccessions":  ','.join(chunk),
                "format": "json",
                "fields": ','.join(return_fields),
                "limit": 0
            }
        if include_accession_type != None:
            params["include_accession_type"] = include_accession_type
        # print(f"{url}, {params}, {with_obj_type}, {','.join(return_fields)}")
        # print("****************************************************************************************")
        # ic(f"chunked_id_list_size={len(chunk)}")
        (data, response) = ena_portal_api_call(url, params, with_obj_type, chunk)
        # print(f"data={data}")

        if response.status_code != 200:
            doze_time = 10
            print(
                f"Due to response {response.status_code}, having another try for {url} and obj_type={with_obj_type} with {params}, after a little doze of {doze_time} seconds")
            time.sleep(doze_time)
            (data, response) = ena_portal_api_call(url, params, with_obj_type, id_list)
            if response.status_code != 200:
                print(f"Due to response exiting {response.status_code}, tried twice")
                ic()
                sys.exit()
        #print(f"data={data}")
        combined_data += data
    # ic(combined_data)
    return combined_data

def chunk_portal_api_call_w_ands(url, with_obj_type, return_fields, and_accession, id_list):
    """
    useful for when there could be a long list of ids, that needs to be chunked to not exceed limits.
    N.B. will need to gradually port the other list chunking methods to here!
    passing a URL with a few specific params is critical, as otherwise too much complexity for this
    :param with_obj_type:
    :param id_list:
    :param return_fields:
    :return:
    """
    #print(f"url={url}\n, ob_type={with_obj_type}\n, rtn_fields={return_fields}\n, id_list len={len(id_list)}\n")
    combined_data = []
    chunk_count = chunk_pos = 0
    list_size = len(id_list)
    iterator = iter(id_list)
    chunk_size = 10  # 10 about the maximum reliable chunk size for AND accessions
    ic(f"{chunk_pos}/{list_size}")
    pre_url = url  # as need to more to this
    # https://www.ebi.ac.uk/ena/portal/api/search?study_accession$3DPRJNA435556%20OR%20study_accession%3DPRJEB32543
    #works curl -s 'https://www.ebi.ac.uk/ena/portal/api/search?result=sample&query=study_accession%3DPRJNA505510%20OR%20study_accession%3DPRJEB32543&fields=sample_accession%2Csample_description%2Cstudy_accession&format=tsv'
    while chunk := list(islice(iterator, chunk_size)):
        chunk_pos += chunk_size
        chunk_count += 1
        and_accession_string = and_accession + '%3D'
        join_string = '%20OR%20' + and_accession + '%3D'
        and_accession_string += join_string.join(chunk)
        #ic(and_accession_string)
        url = pre_url + 'query='
        url += and_accession_string
        if chunk_count % 10 == 0:   #only print progress every X chunks
            ic(f"{chunk_pos}/{list_size} in chunk_portal_api_call()")
        params = {
                "result": with_obj_type,
                "format": "json",
                "fields": ','.join(return_fields),
                "limit": 0
            }
        #print(f"{url}, {params}, {with_obj_type}, {','.join(return_fields)}")
        (data, response) = ena_portal_api_call(url, params, with_obj_type, chunk)
        # print(f"data={data}")

        if response.status_code != 200:
            doze_time = 10
            print(
                f"Due to response {response.status_code}, having another try for {url} and obj_type={with_obj_type} with {params}, after a little doze of {doze_time} seconds")
            time.sleep(doze_time)
            (data, response) = ena_portal_api_call(url, params, with_obj_type, id_list)
            if response.status_code != 200:
                print(f"Due to response exiting {response.status_code}, tried twice")
                ic()
                sys.exit()
        #print(f"data={data}")
        combined_data += data
    return combined_data




def main():
    url = 'https://www.ebi.ac.uk/ena/portal/api/count?result=sample&dataPortal=ena'
    ena_portal_api_call(url, {}, "sample", "")

if __name__ == '__main__':
    ic()
    main()
