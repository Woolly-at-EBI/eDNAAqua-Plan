#!/usr/bin/env python3
"""Script of study_collection.py is to study_collection.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-18
__docformat___ = 'reStructuredText'
chmod a+x study_collection.py
"""
import sys

from icecream import ic

from ena_portal_api import get_ena_portal_url, ena_portal_api_call_basic


class StudyCollection:
    """

    """

    def __init__(self):
        ic()
        self.name = "TBD"
        self.study_dict = {'study' : {}, 'sample': {}}

    def get_name(self):
        return(self.name)


    def get_global_study_dict(self):
        return self.study_dict

    def get_sample_id_list(self):
        my_dict = self.get_global_study_dict()
        global_sample_set = set()
        for study_id in self.study_dict['study']:
            global_sample_set.update(self.study_dict['study'][study_id]['sample_acc_set'])
        return sorted(list(global_sample_set))

def study2sample(study_id_list, study_collection, debug_status):
    """

    :param study_id_list:
    :param study_collection:  # if None creates it!
    :return: sample_acc_list

    curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=sample&query=study_accession%3D%22PRJDB13387%22&fields=sample_accession%2Csample_description%2Cstudy_accession&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search"
    sample_accession	sample_description	study_accession
    SAMD00454395	Mus musculus	PRJDB13387
    SAMD00454397	Mus musculus	PRJDB13387
    SAMD00454399	Mus musculus	PRJDB13387
    SAMD00454401	Mus musculus	PRJDB13387
    SAMD00454396	Mus musculus	PRJDB13387
    SAMD00454398	Mus musculus	PRJDB13387
    SAMD00454400	Mus musculus	PRJDB13387
    SAMD00454394	Mus musculus	PRJDB13387
    """
    #
    # if study_collection == None:
    #     study_collection = StudyCollection()

    #ic(study_collection.get_global_study_dict())

    result_object_type = 'sample'
    limit = 0
    study_id = 'PRJDB13387'
    my_set = set()

    # curl - X POST - H "Content-Type: application/x-www-form-urlencoded" - d
    # 'result=sample&query=study_accession%3DPRJDB13387&fields=sample_accession%2Csample_description
    # %2Cstudy_accession&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search"

    #currently very inefficient doing one call per study_id
    pre_url = get_ena_portal_url() + "search?" + 'result=' + result_object_type + '&fields=sample_accession&format=tsv'
    pre_url += '&limit=' + str(limit) + '&query=study_accession' + '%3D'

    study_id_pos = 0
    ic(f"{study_id_pos+1}/{len(study_id_list)}")
    #study_collection.study_dict
    for study_id in study_id_list:
       if study_id_pos%100 == 0:
           ic(f"{study_id_pos}/{len(study_id_list)}")
       study_id_pos += 1
       if study_id in study_collection.study_dict:
           my_set.add(study_collection.study_dict[study_id]['sample_acc_set'])
       else:
          url = pre_url + study_id
          if debug_status:
              ic(url)
          (data, response) = ena_portal_api_call_basic(url)
          # returns tsv text block with fields: experiment_accession	sample_accession

          my_local_sample_acc_set = set()
          my_row_count = 0
          for row in data.split("\n"):
              if my_row_count > 0 and row != "":   #  title row not needed
                  my_set.add(row)
                  my_local_sample_acc_set.add(row)
              my_row_count += 1
          study_collection.study_dict['study'][study_id] = {}
          #ic(study_collection.study_dict)
          study_collection.study_dict['study'][study_id]['sample_acc_set'] = my_local_sample_acc_set

          if debug_status:
                ic(f"\tfor {study_id} found a total of {len(my_local_sample_acc_set)} samples: {my_local_sample_acc_set}")
    #my_set.remove("sample_accession")  # not needed as would be the title line.
    return sorted(list(my_set))


def main():
    ic()
    study_collection = StudyCollection()

    ic(study_collection.get_name())
    study_acc_list = ['PRJNA435556',
                     'PRJEB32543',
                     'PRJNA505510',
                     'PRJEB25385',
                     'PRJNA993105',
                     'PRJNA522285',
                     'PRJEB28751',
                     'PRJEB36404',
                     'PRJEB27360',
                     'PRJEB40122', "madeup"]
    ic(study_acc_list)

    sample_acc_list = study2sample(study_acc_list, study_collection,False)

    ic(len(study_collection.get_sample_id_list()))

if __name__ == '__main__':
    ic()
    main()
