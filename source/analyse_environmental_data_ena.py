#!/usr/bin/env python3
"""Script of analyse_environmental_data_ena.py is to analyse_environmental_data_ena.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-06
__docformat___ = "reStructuredText"
chmod a+x analyse_environmental_data_ena.py
"""
import os.path
import re
import sys

from icecream import ic
from py_markdown_table.markdown_table import markdown_table
import pickle
import plotly.express as px
import pandas as pd
from io import StringIO

pd.set_option("display.max_rows", 1000)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)

from ena_portal_api import get_ena_portal_url, ena_portal_api_call_basic, chunk_portal_api_call, urldata2id_set, get_sample_run_accessions
from geography import Geography
from sample import Sample
from sample_collection import SampleCollection, get_sample_field_data
from study_collection import study2sample, StudyCollection
from data_utils import *
from processed_categories import ProcessedCategories

ena_project_dir = "/Users/woollard/projects/eDNAaquaPlan/eDNAAqua-Plan/"
ena_data_dir = ena_project_dir + "data/ena_in/"
ena_data_out_dir = ena_project_dir + "data/out/"
# Define the ENA API URL
ena_api_url = "https://www.ebi.ac.uk/ena/portal/api"



def add_info_to_object_list(with_obj_type, obj_dict, data):
    """
    adds information from multiple ids to object.
    :param with_obj_type:
    :param obj_dict:
    :param data:
    :return:
    """
    ic()

    # ic(data)
    data_by_id = {}
    id_list = []

    if with_obj_type == "sample":
        for dict_row in data:
            # ic(dict_row["sample_accession"])
            # ic(dict_row)
            data_by_id[dict_row["sample_accession"]] = dict_row
            id_list.append(dict_row["sample_accession"])
    geography = Geography()

    # ic("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    for id in id_list:
        # ic(id)
        obj = obj_dict[id]
        if with_obj_type == "sample":
            if obj.sample_accession in data_by_id:
                if "description" in data_by_id[obj.sample_accession]:
                    obj.description = data_by_id[obj.sample_accession]["description"]
                if "study_accession" in data_by_id[obj.sample_accession]:
                    obj.study_accession = data_by_id[obj.sample_accession]["study_accession"]
                if "environment_biome" in data_by_id[obj.sample_accession]:
                    obj.environment_biome = data_by_id[obj.sample_accession]["environment_biome"]
                if "taxonomic_identity_marker" in data_by_id[obj.sample_accession]:
                    if data_by_id[obj.sample_accession]["taxonomic_identity_marker"] != "":
                        obj.taxonomic_identity_marker = data_by_id[obj.sample_accession]["taxonomic_identity_marker"]
                if "tax_id" in data_by_id[obj.sample_accession]:
                    obj.tax_id = data_by_id[obj.sample_accession]["tax_id"]
                if "country" in data_by_id[obj.sample_accession]:
                    obj.country = data_by_id[obj.sample_accession]["country"]
                    obj.country_clean = geography.clean_insdc_country_term(obj.country)
                    if obj.country_clean != "":
                        obj.country_is_european = geography.is_insdc_country_in_europe(obj.country_clean)
                if "location_start" in data_by_id[obj.sample_accession]:
                    obj.location_start = data_by_id[obj.sample_accession]["location_start"]
                if "location_end" in data_by_id[obj.sample_accession]:
                    obj.location_end = data_by_id[obj.sample_accession]["location_end"]
            if "tag" in data_by_id[obj.sample_accession]:
                obj.tag = data_by_id[obj.sample_accession]["tag"]
                if ("freshwater_medium_confidence" in obj.tag) or ("freshwater_high_confidence" in obj.tag):
                    obj.sample_tag_is_freshwater = True
                if ("marine_medium_confidence" in obj.tag) or ("marine_high_confidence" in obj.tag):
                    obj.sample_tag_is_marine = True
                if ("terrestrial_medium_confidence" in obj.tag) or ("terrestrial_high_confidence" in obj.tag):
                    obj.sample_tag_is_terrestrial = True
                if ("coastal_brackish_medium_confidence" in obj.tag) or ("coastal_brackish_high_confidence" in obj.tag):
                    obj.sample_tag_is_coastal_brackish = True

            else:
                # ic(f"Warning: {obj.sample_accession} not being found in hits")
                pass
            # print(obj.print_values())
    return


def annotate_sample_objs(sample_list, with_obj_type, sample_collection_obj):
    """
     annotate all the sample objects - CONSIDER moving to the sample_collection, even in an OO way
    :param sample_list:
    :param with_obj_type:
    :return:
    """
    ic()
    sample_rtn_fields = sample_collection_obj.sample_fields

    # ic(",".join(sample_collection_obj.sample_fields))
    # sample_list = sample_list[0:10]
    # ic(sample_list[0:3])
    sample_obj_dict = sample_collection_obj.sample_obj_dict

    for sample in sample_list:
        # ic(sample.sample_accession)
        sample_obj_dict[sample.sample_accession] = sample

    all_sample_data = get_sample_field_data(sample_list, sample_rtn_fields)
    add_info_to_object_list(with_obj_type, sample_obj_dict, all_sample_data)

    # ic()
    if with_obj_type == "sample":
        sample_collection_obj.addTaxonomyAnnotation()
        sample_collection_obj.get_sample_collection_stats()
        # ic()
        # print(sample_collection_obj.print_summary())

    return


def get_environmental_sample_list(limit_length):
    """
    all from the ena_expt_searchable_EnvironmentalSample_summarised are EnvironmentalSample tagged in the ENA archive!
    curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "result=read_experiment&query=environmental_sample%3Dtrue&fields=experiment_accession%2Cexperiment_title%2Cenvironmental_sample&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
    curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "result=read_experiment&query=environmental_sample%3Dtrue&fields=experiment_accession&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search"
    curl "https://www.ebi.ac.uk/ena/portal/api/search?result=read_experiment&query=environmental_sample=true&fields=experiment_accession&format=tsv&limit=10"
    :return:
    """
    # infile = ena_data_dir + "/" + "ena_expt_searchable_EnvironmentalSample_summarised.txt"
    # sample_env_df = pd.read_csv(infile, sep = "\t")
    # # ic(sample_env_df.head())
    # env_sample_list = sample_env_df["sample_accession"].to_list()
    # return sample_env_df["sample_accession"].to_list()

    result_object_type = "read_experiment"
    url = get_ena_portal_url() + "search?" + "result=read_experiment&query=environmental_sample=true&fields=run_accession,experiment_accession,sample_accession&format=tsv&limit=" + str(
        limit_length)
    ic(url)
    (data, response) = ena_portal_api_call_basic(url)
    # returns tsv text block with fields: experiment_accession	sample_accession
    my_set = urldata2id_set(data, 2)
    # print(my_set)
    return list(my_set)


def get_barcode_study_list():
    """
    curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "result=study&query=study_name%3D%22barcoding%22%20OR%20study_title%3D%22barcoding%22%20OR%20study_description%3D%22barcoding%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search"
        :return:
    """
    # infile = ena_data_dir + "/" + "ena_expt_searchable_EnvironmentalSample_summarised.txt"
    # sample_env_df = pd.read_csv(infile, sep = "\t")
    # # ic(sample_env_df.head())
    # env_sample_list = sample_env_df["sample_accession"].to_list()
    # return sample_env_df["sample_accession"].to_list()

    result_object_type = "study"
    limit = 0
    url = get_ena_portal_url() + "search?" + "result=" + result_object_type
    # url += "&query=study_name%3D%22barcoding%22%20OR%20study_title%3D%22barcoding%22%20OR%20study_description%3D%22barcoding%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=json"
    url += "&query=study_name%3D%22barcoding%22%20OR%20study_title%3D%22barcoding%22%20OR%20study_description%3D%22barcoding%22&fields=study_accession&format=tsv"
    url += "&limit=" + str(limit)
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
        # ic(term)
        terms = term.split(",")
        local_list = []
        for sub_term in terms:
            # print(f"\t{sub_term}")
            match = re.search(r"(\d+S|ITS[1-2]?|CO1|rbcL|trnL|LSU)", sub_term)
            if match:
                # print(f"\t\t++++{match.group()}++++")
                # print(f"\t\t++++{match(str).group(1)}++++")
                clean_set.add(match.group())
                local_list.append(match.group())
            else:
                match = re.search(r"(\d+s|ribulose|oxygenase)", sub_term)
                if match:
                    # print(f"\t\t++++{match.group()}++++")
                    matching_term = match.group()
                    if "ribulose" in matching_term:
                        matching_term = "rbcL"
                    elif "oxygenase" in matching_term:
                        matching_term = "CO1"
                    else:
                        matching_term = matching_term.upper()
                    clean_set.add(matching_term)
                    local_list.append(match.group())
                else:
                    # print(f"\t\tTBD={sub_term}")
                    missing_set.add(sub_term)
        target_gene_dict[term] = local_list
    ic(f"Terms not able to be recognised as target_genes: {list(missing_set)[0:10]}")
    return clean_set, target_gene_dict


def tsvString_col2set(data, column_name):
    df = pd.read_csv(StringIO(data), sep = "\t")
    # ic(df.columns)
    return set(df[column_name])

def get_ITS_sample_list(limit):
    """

    :return: sample_acc_set
    """
    """
outfile="mytmp.txt"
if ! test -f $outfile; then
  echo "generating "$field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "result=read_experiment&query=target_gene%3D%2216S%22%20OR%20%20target_gene%3D%2223S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20target_gene%3D%22ITS%22%20OR%20target_gene%3D%22cytochrome%20B%22%20OR%20target_gene%3D%22CO1%22%20OR%20target_gene%3D%22rbcL%22%20OR%20target_gene%3D%22matK%22%20OR%20target_gene%3D%22ITS2%22%20or%20target_gene%3D%22trnl%22&fields=experiment_accession%2Cexperiment_title%2Ctarget_gene&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
  echo "generating "field" "$outfile
  infile=$outfile
  echo "total;cleaned_target_gene" > $outfile
  cut -f4 $infile  |  tr "[A-Z]" "[a-z]" | sed "s/ribulose-1,5-bisphosphate carboxylase\/oxygenase gene large-subunit//;s/cytochrome c oxidase i/co1/;s/internal transcribed spacer/its/g" | sed "s/[,;:)(-]/ /g" | tr " " "\n"  | sed "/^$/d;/^of$/d;/^v[0-9]*$/d;/^gene/d;/^and$/d;/^[0-9]*$/d" | awk "!/^on$|^bp$|^the$|^regions$|^variable$|^bacterial$|^archaeal$|mitochondrial$|^fungal$|^to$|^cyanobacteria|^cdna$|^rdna|converted|^target_gene$|^metagenome$|^hypervariable$|^ribsomal$|^region$|^ribosomal$|transcriptome$|^rna$|^rrna$|^v3v4|518r|27f|^subunit$|^large$|^nuclear$|^intron$|^uaa$|^\.$/" | sort | uniq -c | sort -nr | sed "s/^ *//;s/ /;/;" >> $outfile
fi
    """
    result_object_type = "read_experiment"
    targets = ["16S", "23S", "12S", "ITS", "ITS1", "ITS2", "cytochrome%20B", "CO1", "rbcL", 'matK', 'trnl']
    return_fields = ["experiment_accession", "experiment_title", "sample_accession", "target_gene"]
    url = get_ena_portal_url() + "search?" + "result=" + result_object_type
    #url += "&query=target_gene%3D%2216S%22%20OR%20%20target_gene%3D%2223S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20target_gene%3D%22ITS%22%20OR%20target_gene%3D%22cytochrome%20B%22%20OR%20target_gene%3D%22CO1%22%20OR%20target_gene%3D%22rbcL%22%20OR%20target_gene%3D%22matK%22%20OR%20target_gene%3D%22ITS2%22%20or%20target_gene%3D%22trnl%22&fields=experiment_accession%2Cexperiment_title%2Ctarget_gene"
    url += '&query=target_gene%3D%22' + '%22%20OR%20%20target_gene%3D%22'.join(targets)
    url += "%22&fields=" + '%2C'.join(return_fields) + "&limit=" + str(limit)
    print(url)
    (data, response) = ena_portal_api_call_basic(url)
    target_gene_set = tsvString_col2set(data, 'target_gene')
    sample_acc_set = tsvString_col2set(data, 'sample_accession')

    # not using the below information yet, but will need it soon.
    clean_set, target_gene_dict = clean_target_genes(list(target_gene_set))
    ic(f"target_genes: {', '.join(list(clean_set))}")
    #ic(f"samples: {', '.join(list(sample_acc_set))}")

    return list(sample_acc_set)




def sample_analysis(category, sample_list):
    """
    """
    ic()
    sample_collection_obj = SampleCollection(category)

    # ic(len(sample_list))
    count = 0
    sample_set = set()
    for sample_accession in sample_list:
        sample = Sample(sample_accession)
        sample_set.add(sample)
        if category == "environmental_sample_tagged":
            sample.setEnvironmentalSample(True)
        sample.setCategory(category)
        # ic(sample.sample_accession)
        # ic(sample.EnvironmentalSample)

        # if count > 3:
        #    break
        #    # pass
        count += 1

    sample_collection_obj.put_sample_set(sample_set)
    if sample_collection_obj.get_sample_set_size() <= 0:
        print("ERROR: Sample_set size is 0, so something serious has gone wrong with the code or data...")
        ic()
        sys.exit()
    else:
        # ic(sample_collection_obj.get_sample_set_size())
        pass

    annotate_sample_objs(list(sample_set), "sample", sample_collection_obj)

    ic(len(sample_collection_obj.get_all_sample_acc_set()))
    ic(len(sample_collection_obj.get_total_read_run_accession_set()))
    sample_collection_obj.get_aquatic_sample_acc_by_sample_tag_set()

    sample_collection_obj.get_sample_collection_stats()

    return sample_collection_obj


def analysis_summary_output():
    print(f"************** Summary of the ENA samples for {sample_collection_obj.category} **************\n")
    print(sample_collection_obj.print_summary())
    print("+++++++++++++++++++++++++++++++++++")

    ic(len(sample_collection_obj.environmental_study_accession_set))
    # print(", ".join(sample_collection_obj.environmental_study_accession_set))

    # ic(sample_collection_obj.get_sample_coll_df())
    df = sample_collection_obj.get_sample_coll_df()
    print(df.head(3).to_markdown())
    ic()




    file_name = "ena_" + category + "_sample_df"
    ena_env_sample_df_file = ena_data_out_dir + file_name
    ic(f"writing {ena_env_sample_df_file} as .parquet and .tsv")
    df = sample_collection_obj.get_sample_coll_df()
    df.to_parquet(ena_env_sample_df_file + ".parquet")
    df.to_csv(ena_env_sample_df_file + ".tsv", sep = "\t")

    return sample_collection_obj


def clean_acc_list(sample_acc_list):
    """
    remove redundancy etc.
    split on on ";"
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


def generated_combined_summary(sample_accs_by_category):
    """

    :param sample_accs_by_category:
    :return:
    """
    print("===================== generated_combined_summary =============================")

    all_categories = list(sample_accs_by_category.keys())
    stats = {"combined": {"sample_set_intersect_total": 0, "uniq_sample_set_total": 0}, "individual": {}}
    total_uniq_sample_set = set()
    total_intersect_sample_set = set()
    category_count = 0
    sample_acc_set_cat_list = ["sample_acc_list_european", "sample_acc_list_freshwater", "sample_acc_list_marine",
                               "sample_acc_list_coastal_brackish", "sample_acc_list_terrestrial"]
    tag_dict = {}

    for category in all_categories:
        sample_collection_obj = sample_accs_by_category[category]["sample_collection_obj"]
        # ic(f"{category}  {len(sample_accs_by_category[category]["sample_acc_list"])}")
        sample_accs_by_category[category]["sample_acc_set"] = set(sample_accs_by_category[category]["sample_acc_list"])
        for sample_acc_set_cat in sample_acc_set_cat_list:
            ic(sample_acc_set_cat)
            sample_accs_by_category[category][sample_acc_set_cat] = set(
                sample_accs_by_category[category][sample_acc_set_cat])
        total_uniq_sample_set.update(sample_accs_by_category[category]["sample_acc_set"])
        if category_count == 0:
            total_intersect_sample_set.update(sample_accs_by_category[category]["sample_acc_set"])
        else:
            total_intersect_sample_set.intersection_update(sample_accs_by_category[category]["sample_acc_set"])
        stats["individual"][category] = {
            "sample_acc_set": {"total": len(sample_accs_by_category[category]["sample_acc_list"])}}
        stats["combined"][category] = {}
        #
        # sample_accs_by_category[category] = {"sample_acc_list": sample_acc_list}
        # sample_collection_obj = detailed_sample_analysis(category, sample_acc_list)
        # sample_accs_by_category[category]["sample_collection_obj"] = sample_collection_obj

        ic(sample_collection_obj.print_summary())
        ic(len(sample_collection_obj.get_european_sample_accession_list()))
        len(sample_collection_obj.european_sample_set)
        for sample_acc_set_cat in sample_acc_set_cat_list:
            ic(sample_acc_set_cat)
            if sample_acc_set_cat == "sample_acc_list_european":
                stats["individual"][category]["sample_acc_list_european"] = {
                    "total": len(sample_collection_obj.european_sample_set)}
            else:
                (blank, prefix, tag_name) = sample_acc_set_cat.partition("sample_acc_list_")
                stats["individual"][category][sample_acc_set_cat] = {
                    "total": len(sample_collection_obj.get_sample_tag_list(tag_name))}
        category_count += 1

    for category in all_categories:
        # ic(f"{category} {len(sample_accs_by_category[category]["sample_acc_set"])}")
        for category2 in all_categories:
            if category != category2:
                # ic(f"\t{category2} {len(sample_accs_by_category[category2]["sample_acc_set"])}")
                tmp_set = sample_accs_by_category[category]["sample_acc_set"].copy()
                tmp_set.intersection_update(sample_accs_by_category[category2]["sample_acc_set"])
                stats["combined"][category][category2] = {"total_intersect": len(tmp_set)}

    stats["combined"]["sample_set_intersect_total"] = len(total_intersect_sample_set)
    stats["combined"]["uniq_sample_set_total"] = len(total_uniq_sample_set)

    generate_combined_summary_table(all_categories, stats)

    return stats


def generate_total_summary_table(all_categories, stats):
    # generate Total tables
    individual_total_data = []
    for category in all_categories:
        # print(f"\t{category}  {stats["individual"][category]["sample_acc_set"]["total"]}")
        ic(stats["individual"][category])
        individual_total_data.append(
            {"Category": category, "Sample_total": stats["individual"][category]["sample_acc_set"]["total"], \
             "European_sample_total": stats["individual"][category]["sample_acc_list_european"]["total"], \
             "freshwater_sample_total": stats["individual"][category]["sample_acc_list_freshwater"]["total"], \
             "marine_sample_total": stats["individual"][category]["sample_acc_list_marine"]["total"], \
             "coastal_brackish_sample_total": stats["individual"][category]["sample_acc_list_coastal_brackish"][
                 "total"], \
             "terrestrial_sample_total": stats["individual"][category]["sample_acc_list_terrestrial"]["total"] \
             })
    ic(individual_total_data)
    markdown = markdown_table(individual_total_data).get_markdown()
    print(markdown)

    df = pd.DataFrame.from_records(individual_total_data)
    ic(df.head(3))
    # fig = px.bar(df, x="Category", y="total_intersect", color="Category_2", title="In ENA: Overlaps between different environment search category searches")
    # fig.show()

    value_vars_set = set(df.columns)
    value_vars_set.remove("Category")
    value_vars_list = list(value_vars_set)
    ic(value_vars_list)
    long_df = df.melt(id_vars = ["Category"], value_vars = value_vars_list)
    ic(long_df.head())
    return long_df


def generate_combined_summary_table(all_categories, stats):
    """

    :param all_categories:
    :param stats:
    :return:
    """
    ic()
    ic(all_categories)
    generate_total_summary_table(all_categories, stats)

    combined_total_data = []
    for category in all_categories:
        ic(category)
        for category2 in all_categories:
            if category != category2:
                ic(category2)
                # print(f"\t{category} {category2} {stats["combined"][category][category2]["total_intersect"]}")
                combined_total_data.append({"Category_1": category, "Category_2": category2, \
                                            "total_intersect": stats["combined"][category][category2]["total_intersect"] \
                                            })

    ic(combined_total_data)
    markdown = markdown_table(combined_total_data).get_markdown()
    print(markdown)
    df = pd.DataFrame.from_records(combined_total_data)
    # ic(df.head(3))
    fig = px.bar(df, x = "Category_1", y = "total_intersect", color = "Category_2",
                 title = "In ENA: Overlaps between different environment search category searches")
    # fig.show()
    image_filename = (ena_data_out_dir + "ENA_environment_search_strategy_overlaps" + ".png")
    print(f"Writing to {image_filename}")
    fig.write_image(image_filename)


def tax_ids2sample_ids(tax_id_list):
    """

    :param tax_id_list:
    :return: sample_id_list
    """
    ic()
    # "result=sample&fields=sample_accession%2Csample_description&limit=100&includeAccessionType=taxon&includeAccessions=9606%2C1%2C2&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search"
    #
    url = "https://www.ebi.ac.uk/ena/portal/api/search?dataPortal=ena" + "&includeAccessionType=taxon"
    with_obj_type = "sample"
    return_fields = ["sample_accession", "tax_id"]
    data = chunk_portal_api_call(url, with_obj_type, return_fields, tax_id_list)
    sample_id_set = set()
    # ic(data)
    for row in data:
        sample_id_set.add(row["sample_accession"])
    return list(sample_id_set)

def process_sample_tag_table(data, tag_list):
    """
    This is the data table from an API query
    :param data:
    :return: dictionary, with a key for all the tag_list
    """
    df = pd.read_csv(StringIO(data), sep = "\t")
    df = df.sample(25)
    sample_tag_dict = {}

    # ic(sorted(df['sample_accession']))
    for tag in tag_list:
        # ic(tag)
        high_name = tag + ":high_confidence"
        medium_name = tag + ":medium_confidence"
        high_set = set(df.loc[df.tag.str.contains(high_name)]['sample_accession'])
        medium_set = set(df.loc[df.tag.str.contains(medium_name)]['sample_accession'])
        # ic(len(high_set))
        # ic(len(medium_set))
        combined_set = high_set.union(medium_set)
        # ic(len(combined_set))
        sample_tag_dict[tag] = {}
        sample_tag_dict[tag]['sample_accession'] = list(combined_set)

    return sample_tag_dict





def get_aquatic_environmental_tagged_sample_id_list(limit_length):
    """
    just doing for tax at the moment
    :param limit_length:
    :return: sample_acc_list, sample_tag_dict
    """
    ic()
    # limit_length = 1000
    limit = "&limit=" + str(limit_length)
    # tag="coastal_brackish_high_confidence" AND tag="freshwater_high_confidence" AND tag="marine_high_confidence" AND tag="environmental" AND tag="arrayexpress"
    # curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "result=taxon&query=tag%3D%22coastal_brackish_high_confidence%22%20AND%20tag%3D%22freshwater_high_confidence%22%20AND%20tag%3D%22marine_high_confidence%22%20AND%20tag%3D%22environmental%22%20AND%20tag%3D%22arrayexpress%22&fields=tax_id%2Cscientific_name%2Ctag&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search"

    aquatic_tags = sorted(["marine_medium_confidence", "marine_high_confidence", "freshwater_medium_confidence",
                           "freshwater_high_confidence", "coastal_brackish_medium_confidence",
                           "coastal_brackish_high_confidence"])
    ic(', '.join(aquatic_tags))
    aquatic_url_part = 'tag%3D' + '%20OR%20tag%3D'.join(aquatic_tags)
    ic(aquatic_url_part)

    aquatic_tag_list = ['freshwater', 'marine', 'coastal_brackish']

    source_type = "sample"
    if source_type == "taxon":
        url = "https://www.ebi.ac.uk/ena/portal/api/search?result=taxon&query=" + aquatic_url_part + "&fields=tax_id&dataPortal=ena&format=tsv" + limit
        # url = "https://www.ebi.ac.uk/ena/portal/api/search?result=taxon&query=tag%3Dmarine_medium_confidence%20OR%20tag%3Dmarine_high_confidence%20OR%20tag%3Dfreshwater_medium_confidence%20OR%20tag%3Dfreshwater_high_confidence%20OR%20tag%3Dcoastal_brackish_medium_confidence%20OR%20tag%3Dcoastal_brackish_high_confidence&fields=tax_id&dataPortal=ena&format=tsv" + limit
        ic(url)
        (data, response) = ena_portal_api_call_basic(url)
        tax_id_list = urldata2id_set(data, 0)
        #ic("Now doing tax_ids2sample_ids")
        sample_acc_list = tax_ids2sample_ids(tax_id_list)
        ic(f"in get_aquatic_environmental_tagged_sample_id_list {len(sample_acc_list)} from tax tagging")
    if source_type == "sample":
        # url = "https://www.ebi.ac.uk/ena/portal/api/search?result=sample&query=" + aquatic_url_part + "&fields=sample_accession,description,tag&dataPortal=ena&format=tsv" + limit
        url = "https://www.ebi.ac.uk/ena/portal/api/search?result=sample&query=" + aquatic_url_part + "&fields=sample_accession,tag&dataPortal=ena&format=tsv" + limit
        ic(url)
        (data, response) = ena_portal_api_call_basic(url)
        # print(data)
        sample_acc_list = sorted(set(tsvString_col2set(data, 'sample_accession')))
        sample_tag_dict = process_sample_tag_table(data, aquatic_tag_list)

    # ic(', '.join(sample_acc_list))
    ic(len(sample_acc_list))
    return sample_acc_list, sample_tag_dict

def get_taxonomic_environmental_tagged_sample_id_list(limit_length):
    ic()
    # tag="coastal_brackish_high_confidence" AND tag="freshwater_high_confidence" AND tag="marine_high_confidence" AND tag="environmental" AND tag="arrayexpress"
    # curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "result=taxon&query=tag%3D%22coastal_brackish_high_confidence%22%20AND%20tag%3D%22freshwater_high_confidence%22%20AND%20tag%3D%22marine_high_confidence%22%20AND%20tag%3D%22environmental%22%20AND%20tag%3D%22arrayexpress%22&fields=tax_id%2Cscientific_name%2Ctag&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search"

    # https://www.ebi.ac.uk/ena/portal/api/search?result=taxon&query=tag%3Dmarine_medium_confidence%20OR%20tag%3Dmarine_high_confidence%20OR%20tag%3Dfreshwater_medium_confidence%20OR%20tag%3Dfreshwater_high_confidence%20OR%20tag%3Dcoastal_brackish_medium_confidence%20OR%20tag%3Dcoastal_brackish_high_confidence&fields=tax_id%2Ctag&limit=10&dataPortal=ena&dccDataOnly=false&format=tsv&download=false
    limit = "&limit=" + str(limit_length)
    url = "https://www.ebi.ac.uk/ena/portal/api/search?result=taxon&query=tag%3Dmarine_medium_confidence%20OR%20tag%3Dmarine_high_confidence%20OR%20tag%3Dfreshwater_medium_confidence%20OR%20tag%3Dfreshwater_high_confidence%20OR%20tag%3Dcoastal_brackish_medium_confidence%20OR%20tag%3Dcoastal_brackish_high_confidence&fields=tax_id&dataPortal=ena&format=tsv" + limit
    ic(url)
    (data, response) = ena_portal_api_call_basic(url)

    # ic(data)
    tax_id_list = urldata2id_set(data, 0)
    # ic("Now doing tax_ids2sample_ids")
    sample_acc_list = tax_ids2sample_ids(tax_id_list)
    # ic(len(sample_acc_list))
    return sample_acc_list

def get_environmental_properties_sample_id_list(limit_length):
    """
    currently only using broad_scale_environmental_context, as found few instances of other columns being used when this was not.

    :param limit_length:
    :return: sample_id_list
    """
    ic()
    sample_acc_list = []
    infile = ena_data_dir + "ena_all_env.txt"
    if limit_length == 0:
        df = pd.read_csv(infile, sep = "\t", on_bad_lines = "skip")
    else:
        df = pd.read_csv(infile, sep = "\t", on_bad_lines = "skip", nrows = limit_length)

    ic(df.columns)
    # ic(df)
    # df.columns: Index(
    #  ["sample_accession", "broad_scale_environmental_context", "environment_biome", "environment_feature",
    #    "environment_material", "environmental_medium", "environmental_sample", "local_environmental_context"], dtype="object")
    columns = ["broad_scale_environmental_context"]
    exclusion_terms = {
        "broad_scale_environmental_context": "healthy_adult|not aplicable|[Nn]ot [Aa]pplicable|not provided|Mouse gut|incubation experiment|female-fallopian tubes|Intestinal tract|^Control|^a$|^[0-9]+$|gut microbiome|Herdsmen|nematode body|^missing$|intestinal[ _]tract|animal cage|intestine environment|Mosue colon|^mouse|animal distal gut|bodily fluid material biome|animal facilities|^urine|^[Ss]tool|Sealed jar in the lab|retail food|^skin|^lung|^Lung|^colon$|^[Cc]hicken|mice|^mouth|chiclken|intestinal|^Saliva|^[Ff]ood$|^oral|^nasal|anaerobic sludge blanket reactor|^[Cc]hicken$|^[Mm]ouse$|Bos taurus|digestive tract|infant|digestive system|[Hh]ospital|stool sample|^Gallus gallus|poultry|RUSITEC|children|^gut$|mouse-gut|AA broiler breeder gut|attus norvegicus gut|Infant stool|tongue coat|tongue coat|gut mucosa|pig|Vagina|Gut|Oral|nan|human|Human|chicken gut|^rat|pH|mouse digestive system|entity|food material|vagina|Anaerobic Reactor|anaerobic bioreactor|biogas|cecum|Anerobic Reactor|[Hh]omo [Ss]apien|commercial food enzyme product|foodon|pig feces|laboratory colony|gerbil|Reactor|not applicable|meat part|laboratory|Laboratory|Laboratory|fermented vegetable food product|Larval rearing tank|Aged care home"
        }

    sample_acc_set = set()
    ic(len(df))
    for my_col in columns:
        # print(my_col)
        # print(df[my_col].value_counts())
        df[my_col] = df[my_col].astype(str)
        # ic(df[df[my_col].str.contains("biome")])
        exclusion_terms = exclusion_terms[my_col]
        tmp_df = df[~df[my_col].str.contains(exclusion_terms)]
        ic(len(tmp_df))
        # ic()
        # print(tmp_df.to_string())
        # print(tmp_df[my_col].value_counts().to_string())
        # select_columns = ["broad_scale_environmental_context", "local_environmental_context"]
        ic(len(tmp_df[my_col].to_list()))
        ic(tmp_df[my_col].value_counts().head(5))

        sample_acc_set.update(set(tmp_df["sample_accession"].to_list()))
        ic(len(sample_acc_set))
    # ic(df[select_columns].groupby(select_columns).size().reset_index(name="count").sort_values(by=["count"], ascending=False).head(10))

    return sorted(sample_acc_set)


def detailed_sample_analysis(category, sample_acc_list):
    ic()
    # ic(len(sample_acc_list))
    # ic(sample_acc_list[0:10])
    sample_acc_list = clean_acc_list(sample_acc_list)
    sample_collection_obj = sample_analysis(category, sample_acc_list)
    ic(f"category={category} total sample total={len(sample_collection_obj.sample_set)}")

    return sample_collection_obj


def process_categories(categories, sample_accs_by_category, limit_length):
    """
    sample_accs_by_category[category] = {"sample_acc_list": sample_acc_list, "tag_dict": tag_dict}

    :param categories:
    :param sample_accs_by_category:
    :param limit_length:
    :return:
    """
    ic()
    ic(categories)
    ic(limit_length)
    ic(sample_accs_by_category)
    for category in categories:
        ic(f"*********** category={category} ***********")
        study_collection = StudyCollection()
        sample_collection = SampleCollection(category)
        if category in sample_accs_by_category:
            ic()
            if category == "environmental_sample_tagged":
                ic(len(sample_accs_by_category[category]["sample_acc_list"]))
            # if commented
            sample_collection_obj = sample_accs_by_category[category]["sample_collection_obj"]
            print("\n+++++++++++++++++++++++++++++++++++")
            print(f"************** Summary of the ENA samples for: {category} **************\n")
            print(sample_collection_obj.print_summary())
            print("+++++++++++++++++++++++++++++++++++")
            ic()
            sys.exit()
            # sample_collection_obj = detailed_sample_analysis(category, sample_accs_by_category[category]["sample_acc_list"])
            continue  # I.E. if this already exists, don"t bother recreating it.
        ic(f"+++++++++++++ about to run sample get for category={category}  +++++++++++++++")
        if category == "environmental_sample_tagged":
            sample_acc_list = get_environmental_sample_list(limit_length)
            # ic(len(sample_acc_list))
        elif category == "barcode_study_list":
            study_acc_list = get_barcode_study_list()
            if limit_length != 0:
                study_acc_list = study_acc_list[0:limit_length]
            sample_acc_list = study2sample(study_acc_list, study_collection, False)
            # ic(len(study_collection.get_sample_id_list()))
        elif category == "ITS_experiment":
            sample_acc_list = get_ITS_sample_list(limit_length)
            if limit_length != 0:
                sample_acc_list = sample_acc_list[0:limit_length]
        elif category == "sample_aquatic_domain_tagged":
            sample_acc_list, tag_dict = get_aquatic_environmental_tagged_sample_id_list(limit_length)
            if limit_length != 0:
                sample_acc_list = sample_acc_list[0:limit_length]
        elif category == "taxonomic_aquatic_domain_tagged":
                ic()
                # sample_acc_list = get_aquatic_environmental_tagged_sample_id_list(limit_length)
                # sample_accs_by_category[category] = {"sample_acc_list": sample_acc_list}
                # if limit_length != 0:
                #     sample_acc_list = sample_acc_list[0:limit_length]
        elif category == "taxonomic_environmental_domain_tagged":
            # ic()
            sample_acc_list = get_taxonomic_environmental_tagged_sample_id_list(limit_length)
            sample_accs_by_category[category] = {"sample_acc_list": sample_acc_list}
            if limit_length != 0:
                sample_acc_list = sample_acc_list[0:limit_length]
        elif category == "environmental_sample_properties":
            sample_acc_list = get_environmental_properties_sample_id_list(limit_length)
            if limit_length != 0:
                sample_acc_list = sample_acc_list[0:limit_length]
        else:
            # ena_all_env.txt
            print(f"ERROR: category {category} has no fetch methods etc.")
            sys.exit()

        # ic(len(sample_acc_list))
        ic(sample_accs_by_category.keys())
        sample_accs_by_category[category] = {"sample_acc_list": sample_acc_list, "tag_dict": tag_dict}
        sample_collection_obj = detailed_sample_analysis(category, sample_acc_list)
        sample_collection_obj.decorate_sample_tags(tag_dict)
        # ic(sample_acc_list)
        run_accession_list = get_sample_run_accessions(sample_acc_list)

        ic(len(sample_collection_obj.freshwater_sample_acc_tag_set))
        ic(len(sample_collection_obj.get_aquatic_sample_acc_by_sample_tag_set()))
        ic(len(sample_collection_obj.get_aquatic_run_read_by_sample_tag_set()))

        # ic(get_sample_run_accessions(sample_collection_obj.get_aquatic_sample_acc_by_sample_tag_set()))
        ic()
        sys.exit()




        sample_accs_by_category[category][
            "sample_acc_list_european"] = sample_collection.get_european_sample_accession_list()
        sample_accs_by_category[category]["sample_acc_list_freshwater"] = sample_collection.get_sample_tag_list(
            "freshwater")
        sample_accs_by_category[category]["sample_acc_list_marine"] = sample_collection.get_sample_tag_list("marine")
        sample_accs_by_category[category]["sample_acc_list_terrestrial"] = sample_collection.get_sample_tag_list(
            "terrestrial")
        sample_accs_by_category[category]["sample_acc_list_coastal_brackish"] = sample_collection.get_sample_tag_list(
            "coastal_brackish")
        sample_accs_by_category[category]["sample_collection_obj"] = sample_collection_obj

        print(f"total_ena_archive_sample_size={sample_collection.get_total_archive_sample_size()}")
        ic()
        sys.exit()
        # sys.exit()  # end of loop

    return sample_accs_by_category




def generate_source_metadata_summary(stats, out_dir):
    """
    :param stats:
    :param out_dir:
    :return:
    """
    ic()
    my_summary_dict = {}
    my_sample_collect = SampleCollection("category")
    ic()
    total_archive_sample_size = my_sample_collect.get_total_archive_sample_size()

    required_metadata_field_list = get_required_metadata_field_list()

    metadata_preknown_dict = get_metadata_preknown_dict()
    metadata_preknown_dict['number of records']['value'] = total_archive_sample_size

    ic(metadata_preknown_dict)

    for metadata_req in required_metadata_field_list:
        ic(metadata_req)
        my_summary_dict[metadata_req] = {}
        if metadata_req not in metadata_preknown_dict:
            ic(f"{metadata_req} not known")
            my_summary_dict[metadata_req]['value'] = {}
        else:
            ic(metadata_preknown_dict[metadata_req])
            ic(metadata_preknown_dict[metadata_req]['value'])
            my_summary_dict[metadata_req]['value'] = str(metadata_preknown_dict[metadata_req]['value'])
            my_summary_dict[metadata_req]['example'] = str(metadata_preknown_dict[metadata_req]['example'])
            my_summary_dict[metadata_req]['comment'] = str(metadata_preknown_dict[metadata_req]['comment'])
    # print(f""{metadata_req}": [],")
    df = pd.DataFrame.from_dict(my_summary_dict, orient='index')
    ic(df)
    out_file = out_dir + "ena_edna_info.xlsx"
    ic(out_file)
    df.to_excel(out_file)
    ic()
    sys.exit()
    ic("___________________________________")
    ic(my_summary_dict)


def main(limit_length):
    ic()
    data_location_dict = get_data_location_dict()
    stats = {}
    # generate_source_metadata_summary(stats, data_location_dict["out_dir"])
    # sys.exit()
    # ic(get_required_metadata_field_list())
    # sys.exit()

    categories = ["environmental_sample_properties", "environmental_sample_tagged", "barcode_study_list",
                  "ITS_experiment", "taxonomic_environmental_domain_tagged", "taxonomic_aquatic_domain_tagged"]
    categories = ["environmental_sample_properties"]
    categories = ["ITS_experiment", "taxonomic_aquatic_domain_tagged"]
    categories = ["sample_aquatic_domain_tagged"]
    # categories = ["ITS_experiment"]
    sample_accs_by_category = {}
    sabc_pickle_filename = "sample_acc_by_category.pickle"
    if os.path.isfile(sabc_pickle_filename):
        ic(f"For sample_acc_by_category using {sabc_pickle_filename}")
        with open(sabc_pickle_filename, "rb") as f:
            sample_accs_by_category = pickle.load(f)
    else:
        ic("******* WARNING: Need to run the search scripts *******")
        sample_accs_by_category = process_categories(categories, sample_accs_by_category, limit_length)

    ic()
    sys.exit()
    # # categories = ["environmental_sample_properties",  "taxonomic_environmental_domain_tagged"]
    # # categories = ["taxonomic_environmental_domain_tagged"]
    # sample_accs_by_category = process_categories(categories, sample_accs_by_category, limit_length)
    #
    # processed_categories_obj = ProcessedCategories(sample_accs_by_category)
    # processed_categories_obj.print_summary()
    # ic("AFTER {sample_accs_by_category.keys()}")
    #
    # processed_categories_obj = ProcessedCategories(sample_accs_by_category)
    #
    # sys.exit()
    #
    # with open(sabc_pickle_filename, "wb") as f:
    #     ic(f"writing sample_accs_by_category to {sabc_pickle_filename}")
    #     pickle.dump(sample_accs_by_category, f)
    #
    # stats = generated_combined_summary(sample_accs_by_category)
    # ic(stats)
    # # generate_combined_summary_table(categories, sample_accs_by_category, stats)
    ic()
    sys.exit()
    generate_source_metadata_summary(stats, data_location_dict['out_dir'])

    ic("******* END OF MAIN *******")


if __name__ == "__main__":
    ic()
    limit_length = 100000
    limit_length = 10000
    main(limit_length)
