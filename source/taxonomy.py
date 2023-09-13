#!/usr/bin/env python3
"""Script of taxonomy.py is to taxonomy.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-08
__docformat___ = 'reStructuredText'
chmod a+x taxonomy.py
"""


from icecream import ic
import os
import argparse
from  ena_portal_api import ena_portal_api_call, ena_portal_url
from itertools import islice
import sys


class taxon:
   """
        self.scientific_name
        self.tax_id
        self.tax_list
   """

   def __init__(self, hit):
        """
        :param hit:
            # {'scientific_name': 'Chloephaga melanoptera',
            #     'tag': 'marine;marine_low_confidence;coastal_brackish;coastal_brackish_low_confidence;freshwater;freshwater_low_confidence;terrestrial;terrestrial_low_confidence',
            #     'tax_division': 'VRT',
            #     'tax_id': '8860'},
        #fails safe, but where high or medium confidence they are marked True
        self.isTerrestrial = False
        self.isTerrestrial = False
        self.isCoastal = False
        self.isFreshwater = False

        """
        self.scientific_name = hit['scientific_name']
        self.tax_id = hit['tax_id']
        self.tag_list = sorted(hit['tag'].split(';'))

           # 'coastal_brackish',
           # 'coastal_brackish_low_confidence',
           # 'freshwater',
           # 'freshwater_low_confidence',
           # 'marine',
           # 'marine_low_confidence',
           # 'terrestrial',
           # 'terrestrial_low_confidence']
        self.isTerrestrial = False
        self.isMarine = False
        self.isCoastal = False
        self.isFreshwater = False
        for tag in self.tag_list:
           splits = tag.split(",")
           if len(splits)==3 and splits[2] == "confidence" and (splits[1] == "medium" or splits[1] == "high"):
               if splits[0] == "terrestrial":
                   self.isTerrestrial = True
               elif splits[0] == "marine":
                    self.isMarine = True
               elif splits[0] == "coastal":
                    self.isCoastal = True
               elif  splits[0] == "freshwater":
                    self.isFreshwater = True
               else:
                   print(f"WARNING: {splits[0]} is not yet handled for {splits[0]} for tax_id:{self.tax_id}")


class taxon_collection:
    def __init__(self, hit_list):
        self.tax_id_dict = {}
        self.tax_obj_list = []
        for hit in hit_list:
            taxon_obj = taxon(hit)
            self.tax_id_dict[taxon_obj.tax_id] = taxon_obj
            self.tax_obj_list.append(taxon_obj)

    def get_taxon_obj_by_id(self, tax_id):
        return self.tax_id_dict[tax_id]

    def get_all_taxon_obj_list(self):
        return self.tax_obj_list


def do_portal_api_tax_call(result_object_type, query_accession_ids, return_fields):
    """

    :param result_object_type:
    :param query_accession_ids:
    :param return_fields:
    :return: data # (as list of row hits) e.g.
    [{'scientific_name': 'root', 'tag': '', 'tax_division': 'UNC', 'tax_id': '1'},
               {'scientific_name': 'Chloephaga melanoptera',
                'tag': 'marine;marine_low_confidence;coastal_brackish;coastal_brackish_low_confidence;freshwater;freshwater_low_confidence;terrestrial;terrestrial_low_confidence',
                'tax_division': 'VRT',
                'tax_id': '8860'},
               {'scientific_name': 'Homo sapiens',
                'tag': '',
                'tax_division': 'HUM',
                'tax_id': '9606'}]
    """

    ena_api_url = ena_portal_url()
    ena_search_url = f"{ena_api_url}search?"
    # Define the query parameters
    #ic(query_accession_ids)
    tax_accessions_string = ','.join(query_accession_ids)
    # "query": f"accession={sample_accession}",
    #ic(tax_accessions_string)
    return_fields_string = ','.join(return_fields)

    params = {
        "result": result_object_type,
        "includeAccessions": tax_accessions_string,
        "includeAccessionType": result_object_type,
        "format": "json",
        "fields": return_fields_string,
        "limit": 0
    }

    #ic(ena_search_url)
    my_url = ena_search_url
    # Make a GET request to the ENA API
    # ic(my_url)
    # ic(params)
    # ic(query_accession_ids)
    (data, response) = ena_portal_api_call(my_url, params, result_object_type, query_accession_ids)

    #  curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=taxon&fields=tax_id%2Cscientific_name%2Ctag%2Cdescription%2Ctax_division&includeAccessionType=taxon&includeAccessions=9606%2C8802%2C8888%2C1&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search"
    # curl   'https://www.ebi.ac.uk/ena/portal/api/search?result=taxon&fields=tax_id%2Cscientific_name%2Ctag%2Cdescription%2Ctax_division&includeAccessionType=taxon&includeAccessions=9606%2C8802%2C8888%2C1&format=tsv'
    return data


def create_taxonomy_hash(tax_list):
    """
        allows chunking, so can run a very long list and do in chunks (currently 500, seems to be what
    :param tax_list:
    :return: a list of hits:
    [{'scientific_name': 'root', 'tag': '', 'tax_division': 'UNC', 'tax_id': '1'},
               {'scientific_name': 'Chloephaga melanoptera',
                'tag': 'marine;marine_low_confidence;coastal_brackish;coastal_brackish_low_confidence;freshwater;freshwater_low_confidence;terrestrial;terrestrial_low_confidence',
                'tax_division': 'VRT',
                'tax_id': '8860'},
               {'scientific_name': 'Homo sapiens',
                'tag': '',
                'tax_division': 'HUM',
                'tax_id': '9606'}]
    """
    iterator = iter(tax_list)
    chunk_size = 500

    tax_hash = []
    # ic(sample_obj_dict)
    taxonomy_rtn_fields = ['tax_id','tax_division', 'tag','scientific_name']
    with_obj_type = "taxon"
    combined_data = []
    while chunk := list(islice(iterator, chunk_size)):
            data = []
            return_fields = taxonomy_rtn_fields
            # ic(f"{with_obj_type} ++++ {chunk} ++++++ {return_fields}")
            data = do_portal_api_tax_call(with_obj_type, chunk, return_fields)
            combined_data += data
    return combined_data

def generate_taxon_collection(tax_id_list):
    combined_data = create_taxonomy_hash(tax_id_list)
    taxon_collection_obj = taxon_collection(combined_data)
    return taxon_collection_obj


def main():
    tax_id_list = ['9606', '8860', '1']
    ic(tax_id_list)
    create_taxonomy_hash(tax_id_list)

if __name__ == '__main__':
    ic()
    main()
