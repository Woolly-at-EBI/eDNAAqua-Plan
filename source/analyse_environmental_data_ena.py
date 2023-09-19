#!/usr/bin/env python3
"""Script of analyse_environmental_data_ena.py is to analyse_environmental_data_ena.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-06
__docformat___ = 'reStructuredText'
chmod a+x analyse_environmental_data_ena.py
"""
import sys

from icecream import ic
import os
import argparse
import pandas as pd
import re

from itertools import islice
from sample_collection import SampleCollection, get_sample_field_data
from sample import Sample
from geography import Geography
from ena_portal_api import ena_portal_api_call, get_ena_portal_url, ena_portal_api_call_basic
from study_collection import study2sample, StudyCollection

ena_project_dir = "/Users/woollard/projects/eDNAaquaPlan/eDNAAqua-Plan/"
ena_data_dir = ena_project_dir + "data/ena_in/"
ena_data_out_dir = ena_project_dir + "data/out/"
# Define the ENA API URL
ena_api_url = "https://www.ebi.ac.uk/ena/portal/api"


def encode_accession_list(id_list):
    """
    accessions_html_encoded = encode_accession_list(chunk_sample_id_list)
    :param id_list:
    :return:
    """
    return '%2C%20%20'.join(id_list)





def add_info_to_object_list(with_obj_type, obj_dict, data):
    """

    :param with_obj_type:
    :param obj_dict:
    :param data:
    :return:
    """

    #ic(data)
    data_by_id = {}

    if with_obj_type == "sample":
        for dict_row in data:
            #ic(dict_row)
            data_by_id[dict_row['sample_accession']] = dict_row
    # ic(data_by_id)
    geography = Geography()

    #ic("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    for id in obj_dict:
        obj = obj_dict[id]
        if with_obj_type == "sample":
            if obj.sample_accession in data_by_id:
               if 'description' in data_by_id[obj.sample_accession]:
                  obj.description = data_by_id[obj.sample_accession]['description']
               if 'study_accession' in data_by_id[obj.sample_accession]:
                  obj.study_accession = data_by_id[obj.sample_accession]['study_accession']
               if 'environment_biome' in data_by_id[obj.sample_accession]:
                   obj.environment_biome = data_by_id[obj.sample_accession]['environment_biome']
               if 'taxonomic_identity_marker' in data_by_id[obj.sample_accession]:
                   if data_by_id[obj.sample_accession]['taxonomic_identity_marker'] != "":
                      obj.taxonomic_identity_marker = data_by_id[obj.sample_accession]['taxonomic_identity_marker']
               if 'tax_id' in data_by_id[obj.sample_accession]:
                   obj.tax_id = data_by_id[obj.sample_accession]['tax_id']

               if 'country' in data_by_id[obj.sample_accession]:
                   obj.country = data_by_id[obj.sample_accession]['country']
                   obj.country_clean = geography.clean_insdc_country_term(obj.country)
                   if obj.country_clean != "":
                       obj.country_is_european = geography.is_insdc_country_in_europe(obj.country_clean)
               if 'location_start' in data_by_id[obj.sample_accession]:
                   obj.location_start = data_by_id[obj.sample_accession]['location_start']
               if 'location_end' in data_by_id[obj.sample_accession]:
                   obj.location_end = data_by_id[obj.sample_accession]['location_end']

            else:
                #ic(f"Warning: {obj.sample_accession} not being found in hits")
                pass
            # print(obj.print_values())

    #ic()



def annotate_sample_objs(sample_list, with_obj_type, sample_collection_obj):
    """
     annotate all the sample objects - CONSIDER moving to the sample_collection, even in an OO way
    :param sample_list:
    :param with_obj_type:
    :return:
    """
    ic()
    ic(with_obj_type)
    sample_rtn_fields = ','.join(sample_collection_obj.sample_fields)
    #ic(','.join(sample_collection_obj.sample_fields))
    sample_obj_dict = sample_collection_obj.sample_obj_dict

    for sample in sample_list:
        # ic(sample.sample_accession)
        sample_obj_dict[sample.sample_accession] = sample

    all_sample_data = get_sample_field_data(sample_list, sample_rtn_fields)
    for sample_ena_data in all_sample_data:
        add_info_to_object_list(with_obj_type, sample_obj_dict, sample_ena_data)
    ic()
    if with_obj_type == "sample":
       sample_collection_obj.addTaxonomyAnnotation()
       sample_collection_obj.get_sample_collection_stats()
       ic()
       print(sample_collection_obj.print_summary())

    return


def get_environmental_sample_list():
    """
    all from the ena_expt_searchable_EnvironmentalSample_summarised are EnvironmentalSample tagged in the ENA archive!
    curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=environmental_sample%3Dtrue&fields=experiment_accession%2Cexperiment_title%2Cenvironmental_sample&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
    curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=environmental_sample%3Dtrue&fields=experiment_accession&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search"
    curl 'https://www.ebi.ac.uk/ena/portal/api/search?result=read_experiment&query=environmental_sample=true&fields=experiment_accession&format=tsv&limit=10'
    :return:
    """
    # infile = ena_data_dir + "/" + "ena_expt_searchable_EnvironmentalSample_summarised.txt"
    # sample_env_df = pd.read_csv(infile, sep = '\t')
    # # ic(sample_env_df.head())
    # env_sample_list = sample_env_df['sample_accession'].to_list()
    # return sample_env_df['sample_accession'].to_list()

    result_object_type = 'read_experiment'
    limit = 0
    url = get_ena_portal_url() + "search?" + 'result=read_experiment&query=environmental_sample=true&fields=sample_accession&format=tsv&limit=' + str(limit)

    (data, response) = ena_portal_api_call_basic(url)
    # returns tsv text block with fields: experiment_accession	sample_accession

    my_set = set()
    for line in data.split("\n"):
        if line != "":
            cols = line.split("\t")
            #ic(cols)
            #ic(cols[1])
            my_set.add(cols[1])

    my_set.remove("sample_accession")
    #print(my_set)
    return list(my_set)

def get_barcode_study_list():
    """
    curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22barcoding%22%20OR%20study_title%3D%22barcoding%22%20OR%20study_description%3D%22barcoding%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search"
        :return:
    """
    # infile = ena_data_dir + "/" + "ena_expt_searchable_EnvironmentalSample_summarised.txt"
    # sample_env_df = pd.read_csv(infile, sep = '\t')
    # # ic(sample_env_df.head())
    # env_sample_list = sample_env_df['sample_accession'].to_list()
    # return sample_env_df['sample_accession'].to_list()

    result_object_type = 'study'
    limit = 0
    url = get_ena_portal_url() + "search?" + 'result=' + result_object_type
    #url += '&query=study_name%3D%22barcoding%22%20OR%20study_title%3D%22barcoding%22%20OR%20study_description%3D%22barcoding%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=json'
    url += '&query=study_name%3D%22barcoding%22%20OR%20study_title%3D%22barcoding%22%20OR%20study_description%3D%22barcoding%22&fields=study_accession&format=tsv'
    url += '&limit=' + str(limit)
    (data, response) = ena_portal_api_call_basic(url)
    # returns tsv text block with fields: experiment_accession	sample_accession
    # print(data)
    my_set = set()
    for row in data.split("\n"):
        if row != "":
            my_set.add(row)
    my_set.remove("study_accession")
    ic(f"barcode study total={len(my_set)}")
    return list(my_set)

def clean_target_genes(target_gene_list):
    """
     This cleans the target gene list
    :param target_gene_list:
    :return: clean_set, target_gene_dict
    the target_gene_dict as the term as in the provided list. The value is a list of cleaned matches
    """
    clean_set = set()
    missing_set = set()
    target_gene_dict = {}
    for term in target_gene_list:
        #ic(term)
        terms = term.split(",")
        local_list = []
        for sub_term in terms:
            # print(f"\t{sub_term}")
            match = re.search(r'(\d+S|ITS[1-2]?|CO1|rbcL|trnL|LSU)', sub_term)
            if match:
                # print(f"\t\t++++{match.group()}++++")
                #print(f"\t\t++++{match(str).group(1)}++++")
                clean_set.add(match.group())
                local_list.append(match.group())
            else:
                match = re.search(r'(\d+s|ribulose|oxygenase)', sub_term)
                if match:
                        #print(f"\t\t++++{match.group()}++++")
                        matching_term = match.group()
                        if "ribulose" in matching_term:
                            matching_term = 'rbcL'
                        elif "oxygenase" in matching_term:
                                matching_term = 'CO1'
                        else:
                            matching_term = matching_term.upper()
                        clean_set.add(matching_term)
                        local_list.append(match.group())
                else:
                    #print(f"\t\tTBD={sub_term}")
                    missing_set.add(sub_term)
        target_gene_dict[term] = local_list
    ic(f"Terms not able to be recognised as target_genes: {missing_set}")
    return clean_set, target_gene_dict
def get_ITS_sample_list():
    """

if ! test -f $outfile; then
  echo "generating "$field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=target_gene%3D%2216S%22%20OR%20%20target_gene%3D%2223S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20target_gene%3D%22ITS%22%20OR%20target_gene%3D%22cytochrome%20B%22%20OR%20target_gene%3D%22CO1%22%20OR%20target_gene%3D%22rbcL%22%20OR%20target_gene%3D%22matK%22%20OR%20target_gene%3D%22ITS2%22%20or%20target_gene%3D%22trnl%22&fields=experiment_accession%2Cexperiment_title%2Ctarget_gene&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
  echo "generating "field" "$outfile
  infile=$outfile
  echo "total;cleaned_target_gene" > $outfile
  cut -f4 $infile  |  tr '[A-Z]' '[a-z]' | sed 's/ribulose-1,5-bisphosphate carboxylase\/oxygenase gene large-subunit//;s/cytochrome c oxidase i/co1/;s/internal transcribed spacer/its/g' | sed 's/[,;:)(-]/ /g' | tr ' ' '\n'  | sed '/^$/d;/^of$/d;/^v[0-9]*$/d;/^gene/d;/^and$/d;/^[0-9]*$/d' | awk '!/^on$|^bp$|^the$|^regions$|^variable$|^bacterial$|^archaeal$|mitochondrial$|^fungal$|^to$|^cyanobacteria|^cdna$|^rdna|converted|^target_gene$|^metagenome$|^hypervariable$|^ribsomal$|^region$|^ribosomal$|transcriptome$|^rna$|^rrna$|^v3v4|518r|27f|^subunit$|^large$|^nuclear$|^intron$|^uaa$|^\.$/' | sort | uniq -c | sort -nr | sed 's/^ *//;s/ /;/;' >> $outfile
fi
    """
    # infile = ena_data_dir + "/" + "ena_expt_searchable_EnvironmentalSample_summarised.txt"
    # sample_env_df = pd.read_csv(infile, sep = '\t')
    # # ic(sample_env_df.head())
    # env_sample_list = sample_env_df['sample_accession'].to_list()
    # return sample_env_df['sample_accession'].to_list()

    result_object_type = 'read_experiment'
    limit = 0
    url = get_ena_portal_url() + "search?" + 'result=' + result_object_type
    url += '&query=target_gene%3D%2216S%22%20OR%20%20target_gene%3D%2223S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20target_gene%3D%22ITS%22%20OR%20target_gene%3D%22cytochrome%20B%22%20OR%20target_gene%3D%22CO1%22%20OR%20target_gene%3D%22rbcL%22%20OR%20target_gene%3D%22matK%22%20OR%20target_gene%3D%22ITS2%22%20or%20target_gene%3D%22trnl%22&fields=experiment_accession%2Cexperiment_title%2Ctarget_gene'
    url += '&limit=' + str(limit)
    (data, response) = ena_portal_api_call_basic(url)
    # returns tsv text block with fields: experiment_accession	sample_accession
    #print(data)
    my_set = set()
    target_gene_set = set()
    # experiment_accession	experiment_title	sample_accession	target_gene
    row_count = 0
    for row in data.split("\n"):
        if row_count > 0 and row != "":
            line = row.split("\t")
            my_set.add(line[2])
            target_gene_set.add(line[3])
        row_count += 1
    # ic(my_set)
    # ic(f"sample total={len(my_set)}")
    # ic(target_gene_set)

    #not using the below information yet, but will need it soon.
    clean_set, target_gene_dict = clean_target_genes(list(target_gene_set))
    ic(f"target_genes: {', '.join(list(clean_set))}")
    sys.exit()

    return list(my_set)

def sample_analysis(category, sample_list):
    """
    """
    ic()
    sample_collection_obj = SampleCollection()

    ic(len(sample_list))
    count = 0
    sample_set = set()
    for sample_accession in sample_list:
        sample = Sample(sample_accession)
        sample_set.add(sample)
        if category == "environmental_sample_tagged":
            sample.setEnvironmentalSample(True)
        sample.setCategory(category)
        #ic(sample.sample_accession)
        #ic(sample.EnvironmentalSample)

        # if count > 3:
        #    break
        #    # pass
        count += 1

    sample_collection_obj.put_sample_set(sample_set)
    if sample_collection_obj.get_sample_set_size() <= 0:
        print("ERROR: Sample_set size is 0, so something serious has gone wrong with the code or data...")
        sys.exit()
    else:
        ic(sample_collection_obj.get_sample_set_size() )


    annotate_sample_objs(list(sample_set), "sample", sample_collection_obj)

    sample_collection_obj.get_sample_collection_stats()

    # for sample_obj in sample_set:
    #     print(sample_obj.print_values())

    print("\n+++++++++++++++++++++++++++++++++++")
    print("************** Summary of the ENA samples **************\n")
    print(sample_collection_obj.print_summary())
    print("+++++++++++++++++++++++++++++++++++")


    ic(len(sample_collection_obj.environmental_study_accession_set))
    print(", ".join(sample_collection_obj.environmental_study_accession_set))

    ic("..............")
    ic(sample_collection_obj.get_sample_coll_df())
    df = sample_collection_obj.get_sample_coll_df()
    print(df.head(3).to_markdown())

    ena_env_sample_df_file = ena_data_out_dir + "ena_env_sample_df.parquet"
    ic(f"writing {ena_env_sample_df_file}")
    df = sample_collection_obj.get_sample_coll_df()
    df.to_parquet(ena_env_sample_df_file)

    return sample_collection_obj
def clean_acc_list(sample_acc_list):
    """
    remove redundancy etc.
    split on on ";'
    sample_acc_list = clean_acc_list(sample_acc_list)
    :param sample_acc_list:
    :return: sorted non-redundant list
    """
    clean_set = set()
    for term in sample_acc_list:
        for sub_term in term.split(";"):
            clean_set.add(sub_term)

    ic(f"clean_acc_list input total={len(sample_acc_list)} output total = {len(clean_set)}")

    return sorted(clean_set)

def main():
    categories = ["environmental_sample_tagged"]
    categories = ["barcode_study_list"]
    categories = ["ITS_experiment"]


    study_collection = StudyCollection()

    for category in categories:
        ic(f"*********** category={category} ***********")
        if category == "environmental_sample_tagged":
           sample_acc_list = get_environmental_sample_list()
           limit_length = 1000

           sample_acc_list = sample_acc_list[0:limit_length]

           ic(len(sample_set))
        elif category == "barcode_study_list":
           study_acc_list = get_barcode_study_list()
           # limit_length = 0
           # study_acc_list = study_acc_list[0:limit_length]
           #ic(study_acc_list)
           sample_acc_list = study2sample(study_acc_list, study_collection, False)
           ic(len(sample_acc_list))
           ic(len(study_collection.get_sample_id_list()))
        elif category == "ITS_experiment":
           sample_acc_list = get_ITS_sample_list()
        ic()
        ic(sample_acc_list)
        sample_acc_list = clean_acc_list(sample_acc_list)
        sample_collection_obj = sample_analysis(category, sample_acc_list)
        sample_set = sample_collection_obj.sample_set


    ic("******* END OF MAIN *******")


if __name__ == '__main__':
    ic()
    main()
