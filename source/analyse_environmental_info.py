#!/usr/bin/env python3
"""Script of get_environmental_info.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2024-05-09
__docformat___ = 'reStructuredText'
chmod a+x get_taxononomy_scientific_name.py
"""

import json
import pickle
import re
import sys
import time
import random

import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import logging
import coloredlogs

from collections import Counter

from geography import Geography
from taxonomy import *
from eDNA_utilities import pickle_data_structure, unpickle_data_structure,  print_value_count_table,\
    plot_sankey, get_percentage_list, my_coloredFormatter, plot_countries, capitalise

from get_environmental_info import get_all_study_details, process_geographical_data

logger = logging.getLogger(name = 'mylogger')
pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)




def clean_dates_in_df(df):
    df['collection_year'] = df['collection_date'].apply(collection_date_year)
    df['collection_year'] = pd.to_numeric(df['collection_year'], errors = 'coerce').astype('Int64')
    df = df.sort_values(by = ['collection_date'])
    df['collection_year_bin'] = df['collection_year'].apply(create_year_bins)

    return df



def select_first_part(value):
    """
    select just the first part of value before the :
    :param value:
    :return:
    """

    my_list = value.split(":")
    if len(my_list[0]) > 0:
        return my_list[0]
    else:
        return "missing"

    # #logger.info(value[:value.find(":")])
    # if value.find(":") >= 0:
    #     return value[:value.find(":")+1]
    # else:
    #     return value

def isNaN(num):
    return num != num

def get_presence_or_absence_col(df, col_name):
    # col with and without values
    # FFS isnull etc. did not work
    col_list = df[col_name].to_list()
    absent_count = 0
    present_count = 0

    for val in col_list:
        logger.debug("val: {}".format(val))
        if val == None or isNaN(val):
            absent_count += 1
        elif type(val) == list and len(val) == 0:
            absent_count += 1
        else:
            present_count += 1
    return present_count, absent_count


def experimental_analysis_inc_filtering(df):
    logger.info(df.columns)

    logger.info("before filtering")
    print_value_count_table(df.library_source)
    print_value_count_table(df.library_strategy)


    strategy_list_to_keep = ['AMPLICON', 'WGS', 'RNA-Seq', 'WGA', 'Targeted-Capture', 'ssRNA-seq', 'miRNA-Seq']
    logger.info(strategy_list_to_keep)
    df = df.loc[df['library_strategy'].isin(strategy_list_to_keep)]
    logger.info("after filtering")

    print_value_count_table(df.library_source)
    print_value_count_table(df.library_strategy)


    logger.info(df['library_strategy'].value_counts())
    print_value_count_table(df.library_source)

    logger.info(df.columns)
    logger.info(df['library_strategy'].value_counts())
    logger.info(f"type = {type(df)}")
    logger.info(df['instrument_platform'])
    plot_df = df.groupby(['instrument_platform']).size().to_frame('record_count').reset_index().sort_values(by=['record_count'], ascending=False)
    logger.info(f"Instruments\n{plot_df.to_string(index=False)}")

    print(df.groupby(['library_source', 'library_strategy']).size().reset_index().to_string(index=False))
    logger.info(df.columns)
    path_list = ['library_source', 'library_strategy', 'instrument_platform', 'collection_year_bin']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plotfile = "../images/experimental_analysis_strategy.png"
    logger.info(f"plotting {plotfile}")
    sankey_link_weight = 'record_count'
    plot_sankey(plot_df, sankey_link_weight, path_list,
                'Figure ENA Aquatic "Environmental" readrun record count: library_source, library_strategy, platform, collection_date',
                plotfile)

    return df

def get_filtered_study_details(df):
    """
    get_filtered_study_details provides a data frame on a limited set of study details
    :param df: where "study_accession" is a field
    :return: df_filtered_study_details
    """
    logger.info(df.columns)
    study_accession_list = list(set(df['study_accession'].unique()))
    logger.debug(f"study_accession_list from  all studies total={len(study_accession_list)}")


    df_all_study_details = get_all_study_details()
    all_aquatic_study_accession_list = list(set(df_all_study_details['study_accession'].to_list()))
    logger.debug(f"Number of TOTAL aquatic studies: {len(all_aquatic_study_accession_list)}")

    df_filtered_study_details = df_all_study_details[df_all_study_details['study_accession'].isin(study_accession_list)]
    logger.debug(f"Number of FILTERED aquatic study IDS: {len(all_aquatic_study_accession_list)}")

    return df_filtered_study_details

def target_gene_analysis(df):
    """
    for the target genes as a checklist field
    :param df:
    :return:
    """
    logger.info(f"Coming into target gene analysis have total tows of {len(df)}")


    analyse_barcode_study_details(df)

    logger.info("for the target genes as a checklist field")
    logger.debug(df['target_gene'].value_counts().head())
    # print_value_count_table(df['target_gene'])
    total = len(df)

    df["target_gene_clean_set"] = df["target_gene"].apply(get_barcoding_genes)

    tmp_df = df[df['target_gene'] != ""]
    print_value_count_table(tmp_df['target_gene'])

    print_value_count_table(tmp_df['target_gene_clean_set'])

    total_w_tgs = len(tmp_df)
    logger.info(f"total target_gene count = {total_w_tgs} / {total} = {round((100 * total_w_tgs/ total),2)}%")
    logger.info("---------------+++++++++++++++++++----------------")

    return

def plot_sunburst(df, title, path_list, value_field, plotfile):
    """

    :param df:
    :param title:
    :param path_list:
    :param value_field:
    :param plotfile:
    :return:
    """
    fig = px.sunburst(
            df,
            path = path_list,
            values = value_field,
            title = title,
        )
    # fig.update_layout(legend = dict(
    #     orientation = 'h',
    #     yanchor = 'bottom',
    #     y = 1.02,
    #     xanchor = 'right',
    #     x = 1
    # ))
    # fig.show()
    if plotfile == "plot":
            fig.show()
    else:
            logger.info(f"Sunburst plot to {plotfile}")
            fig.write_image(plotfile)


def taxonomic_analysis(df):
    """
    Doing much taxonomic analysis
    :param df:
    :return:
    """

    tax_id_list = df['tax_id'].unique()
    def lineage_lookup(value):
        # logger.info(taxonomy_hash_by_tax_id[value])
        if value in taxonomy_hash_by_tax_id:
            return taxonomy_hash_by_tax_id[value]['lineage']
        else:
            print(f"warning  taxonomy_hash_by_tax_id:{value} does not exist")
            return ""

    def tax_lineage_lookup(value):
        # logger.info(taxonomy_hash_by_tax_id[value])
        if value in taxonomy_hash_by_tax_id:
            return taxonomy_hash_by_tax_id[value]['tax_lineage']
        else:
            print(f"warning  taxonomy_hash_by_tax_id:{value} does not exist")
            return ""

    def scientific_name_lookup(value):
        # logger.info(taxonomy_hash_by_tax_id[value])
        if value in taxonomy_hash_by_tax_id:
            return taxonomy_hash_by_tax_id[value]['scientific_name']
        else:
            print(f"warning  taxonomy_hash_by_tax_id:{value} does not exist")
            return ""

    logger.info("About to analyse_environment")
    #analyse_environment(df)
    logger.info("RETURNED FROM analyse_environment")

    logger.info("about to create_taxonomy_hash_by_tax_id")
    taxonomy_hash_by_tax_id = create_taxonomy_hash_by_tax_id(tax_id_list)
    logger.info("returned from create_taxonomy_hash_by_tax_id")

    df['scientific_name'] = df['tax_id'].apply(scientific_name_lookup)
    # print_value_count_table(df.scientific_name)

    df['lineage'] = df['tax_id'].apply(lineage_lookup)
    # print_value_count_table(df.lineage)
    df['tax_lineage'] = df['tax_id'].apply(tax_lineage_lookup)
    df['lineage_2'] = df['lineage'].str.extract("^([^;]*);")[0]
    df['lineage_3'] = df['lineage'].str.extract("^[^;]*;([^;]*);")[0]
    # print_value_count_table(df.lineage_3)
    df['lineage_minus2'] = df['lineage'].str.extract("([^;]*);[^;]*$")[0]
    df['lineage_minus3'] = df['lineage'].str.extract("([^;]*);[^;]*;[^;]*$")[0]
    print_value_count_table(df.lineage_minus2)
    tax_id_list = df['tax_id'].unique()
    logger.info(len(tax_id_list))

    path_list = ['lineage_2', 'lineage_minus2', 'scientific_name']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plotfile = "../images/taxonomic_analysis_sunburst.png"
    plot_sunburst(plot_df, 'Figure: ENA "Environmental" readrun records, tax lineage(select)', path_list, 'record_count', plotfile)

    path_list = ['lineage_2', 'lineage_minus3', 'lineage_minus2', 'scientific_name', 'lineage']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plot_df = plot_df[plot_df['lineage_2'] == 'Eukaryota']
    logger.info(f"\n{plot_df}")
    path_list = ['lineage_minus3', 'lineage_minus2', 'scientific_name']
    plotfile = "../images/taxonomic_analysis_euk_sunburst.png"
    plot_sunburst(plot_df, 'Figure: ENA "Environmental" readrun records, tax lineage(Euk)', path_list,
                  'record_count', plotfile)


    path_list = ['lineage_2', 'lineage_minus3', 'lineage_minus2', 'scientific_name', 'lineage']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plot_df = plot_df[plot_df['lineage'].str.contains('Vertebrata')]
    path_list = ['lineage_minus3', 'lineage_minus2', 'scientific_name']
    plotfile = "../images/taxonomic_analysis_euk_sunburst.png"
    plot_sunburst(plot_df, 'Figure: ENA "Environmental" readrun records, Vertebrata', path_list,
              'record_count', plotfile)


    path_list = ['library_source', 'library_strategy', 'lineage_2']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plotfile = "../images/experimental_analysis_strategy_tax.png"
    sankey_link_weight = 'record_count'
    plot_sankey(plot_df, sankey_link_weight, path_list, 'Figure ENA "Environmental" readrun record count: library_source, library_strategy & tax', plotfile)
    return df


def delist_col(my_list):
    """
    deconvolute a list of list
    :param my_list:
    :return: list
    """
    gene_list = []
    for gene_row_list in my_list:
        for gene in gene_row_list:
             gene_list.append(gene)
    return gene_list

def get_barcoding_genes(value):
        """
        method to get barcoding genes
        it is typically run as an apply on a dataframe
        It is used for both analysing the target_genes from the defined metadata and the text in the study description.
        :param value: a string of one or more barcoding gene names
        :return: a set of cleaner values
        """

        sgenes_pattern = re.compile(r'^([1-9]{2}|5\.8)([sS])[ ]?(r)?([RD]NA)?', flags=0)
        sgenes_pattern = re.compile(r'^([1-9]{2}|5\.8)([sS])[ ]?r?(RNA|DNA|ribo)?', flags=0)
        rbcl_pattern = re.compile(r'^(RBCL)', re.IGNORECASE)
        its_pattern = re.compile(r'^(ITS)([1-2])?')
        matk_pattern = re.compile(r'^(matk)', re.IGNORECASE)
        COX1_pattern = re.compile('^COX1|CO1|COI|mtCO|Cytochrome c oxidase|cytochrome oxidase', re.IGNORECASE)
        def clean_name(my_list):
            """
             a clean harmonised list of barcoding gene names
            :param  list of gene names:
            :return: harmonised list.
            """
            clean_set = set()
            #logger.info("-----------------------------------------------------------")
            for my_gene in my_list:
                #logger.info(my_gene)

                match = re.search(rbcl_pattern, my_gene)
                if match:
                    # logger.info(f"----------clean=rbcL")
                    clean_set.add("rbcL")
                    continue
                match = re.search(its_pattern, my_gene)
                if match:
                    if match.group(2):
                        # logger.info(f"----------clean=ITS{match.group(2)}")
                        clean_set.add("ITS" + match.group(2))
                    else:
                        # logger.info(f"----------clean=ITS")
                        clean_set.add("ITS")
                    continue
                match = re.search(matk_pattern, my_gene)
                if match:
                        # logger.info("----------clean=matK")
                        clean_set.add("matK")
                        continue
                match = re.search(COX1_pattern, my_gene)
                if match:
                        # logger.info("----------clean=COX1")
                        clean_set.add("COX1")
                        continue

                match = re.search(sgenes_pattern, my_gene)
                if match:
                    # logger.info(match.group(1))
                    # logger.info(match.group(2))
                    clean_gene_name = match.group(1) + "S"
                    if match.group(3):
                        # logger.info(f"---------------{match.group(3)}")
                        clean_gene_name += " r" + match.group(3)
                    clean_set.add(clean_gene_name)
                    # logger.info(clean_gene_name)
                    continue

                logger.error(f"remaining gene in get_barcoding_genes -->{my_gene}<--")
                sys.exit()


            return clean_set
        barcode_genes_pattern = re.compile('16[sS][ ]?r?[RD]NA|16[sS][ ]?ribo|18S|ITS[12]?|26[Ss]|5\.8[Ss]|rbcL|rbcl|RBCL|matK|MATK|cox1|co1|COX1|CO1|COI|mtCO|cytochrome c oxidase|cytochrome oxidase')
        genes = list(set(re.findall(barcode_genes_pattern, value)))
        if len(genes) > 0:
            # logger.info(genes)
            return list(clean_name(genes))
        else:
            genes = list(set(re.findall(r'16[Ss]', value)))
            if len(genes) > 0:
                return list(clean_name(genes))
            return None

def analyse_barcode_study_details(df):
    """
    Generates a subset of the df, indexed from sample_accession
    Plus annotates two columns using
    barcoding_df['barcoding_genes_from_study'] = list of genes
    barcoding_df['is_barcoding_experiment_probable'] = True

    :param df:
    :return: df: with extra annotations
    """
    dff = get_filtered_study_details(df)
    logger.info(f"in analyse_all_study_details for study_total={len(dff)} total unique study_accession={dff['study_accession'].nunique()}")
    logger.info(dff.columns)
    barcoding_pattern = '16S|18S|ITS|26S|5.8S|RBCL|rbcL|matK|MATK|COX1|CO1|mtCO|barcod'
    barcoding_title_df = dff[dff.study_title.str.contains(barcoding_pattern, regex= True, na=False)]
    logger.info(f"'study_title' with barcoding genes total={len(barcoding_title_df)}")
    logger.debug(barcoding_title_df['study_title'].sample(n=3))

    barcoding_description_df = dff[dff.study_description.str.contains(barcoding_pattern, regex= True, na=False)]
    logger.info(f"'study_description' with barcoding genes total={len(barcoding_description_df)}")
    logger.debug(barcoding_description_df['study_description'].sample(n=3))

    # This will cope with the obvious use cases: including where genes may be in title, but not description
    barcoding_df = pd.concat([barcoding_title_df, barcoding_description_df]).drop_duplicates().reset_index(drop=True)
    logger.info(f"barcoding total = {len(barcoding_df)}")
    barcoding_df['combined_tit_des'] = barcoding_df['study_title'] + barcoding_df['study_description']
    barcoding_df['is_barcoding_experiment_probable'] = True

    barcoding_df['barcoding_genes_from_study'] = barcoding_df.combined_tit_des.apply(get_barcoding_genes)
    logger.debug(barcoding_df['barcoding_genes_from_study'].value_counts())
    print_value_count_table(barcoding_df['barcoding_genes_from_study'])

    # merge all the findings back into the main
    df = pd.merge(df, barcoding_df[['study_accession','barcoding_genes_from_study','is_barcoding_experiment_probable']], on='study_accession', how='left')
    # df[['barcoding_genes_from_study']].fillna(value=[], inplace=True)
    df.loc[df['barcoding_genes_from_study'].isnull()] = df.loc[df['barcoding_genes_from_study'].isnull()].apply(lambda x: [])

    logger.info("---The following are all whole filtered dataframe, not by study----")
    total = len(df)
    present_count, absent_count = get_presence_or_absence_col(df, 'barcoding_genes_from_study')
    logger.info(f"barcoding_genes_from_study present_count {present_count}  {present_count/total*100:.2f}%")
    logger.info(f"barcoding_genes_from_study absent_count {absent_count}   {absent_count/total*100:.2f}%")

    print_value_count_table(df['barcoding_genes_from_study'])
    df = df[['is_barcoding_experiment_probable']].fillna(value = False)
    logger.info(f"len of def being returned is {len(df)}")
    logger.info(df['is_barcoding_experiment_probable'].value_counts())
    logger.info("-------------------------------------------------------------------------------------------")
    return df
    
def add_insdc_member_receiver(df):
    logger.info("adding insdc member receiver")
    #df = df.sample(n=100)
    logger.debug(df.dtypes)
    def get_insdc_member_receiver(value):
        if value.startswith('SAMN'):
            return 'NCBI'
        elif value.startswith('SAME'):
            return 'ENA'
        elif value.startswith('SAMD'):
            return 'DDBJ'
        else:
            return None

    df['insdc_member_receiver'] = df['sample_accession'].apply(get_insdc_member_receiver)
    logger.debug("exiting add_insdc_member_receiver")
    return df


def do_geographical(df):
    """

    :param df:
    :return:
    """
    df = process_geographical_data(df)
    logger.info(f"after process_geographical_data count: {len(df)}")

    # logger.info(f"after process_geographical_data total: {df['country_clean'].value_counts()}")
    # logger.info(f"after process_geographical_data total: {df['country'].value_counts()}")
    print_value_count_table(df.country_clean)


    print_value_count_table(df.continent)

    tmp_df = df[df['ocean'] != 'not ocean']
    logger.info(f"after process_geographical_data count: {len(tmp_df)}")
    print("Oceans Count and Percentage")
    print_value_count_table(tmp_df.ocean)

    path_list = ['continent', 'country_clean']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plot_df = plot_df.sort_values(by=['record_count'], ascending=False)
    logger.info(f"after process_geographical_data count: {len(plot_df)}")
    plotfile = "../images/geography_sunburst.png"
    logger.info(f"plotting\n{plotfile}")
    plot_sunburst(plot_df, 'Figure: ENA Aquatic "Environmental" readrun records, by country', path_list,
                  'record_count', plotfile)

    tmp_df = plot_df[['country_clean', 'record_count']]
    logger.info(f"\n{tmp_df.head(20).to_string(index=False)}")
    #print_value_count_table(df.country_clean)
    country_record_count_dict = dict(zip(plot_df.country_clean, plot_df.record_count))


    plot_countries(country_record_count_dict, 'europe', "Reported eDNA related ALL readrun in Europe Frequencies",
               "../images/ena_european_countries.png")


    #for key in country_record_count_dict.keys():
    US_KEY = "United States of America"
    if US_KEY in country_record_count_dict:
        # logger.info(f"GREAT: -->{US_KEY}<-- found")
        # country_record_count_dict["USA"] = country_record_count_dict[US_KEY]
        country_record_count_dict["United States"] = country_record_count_dict[US_KEY] # by trial and error found this "std" is expected

    plot_countries(country_record_count_dict, 'all', "Reported ENA Aquatic eDNA related ALL readrun in World Frequencies",
                   "../images/ena_all_countries.png")

    path_list = ['ocean']
    plot_df = df.groupby(path_list).size().to_frame('record_count').reset_index()
    plot_df = plot_df[plot_df['ocean'] != 'not ocean']
    plotfile = "../images/ocean_sunburst.png"
    logger.info(f"plotting {plotfile}")
    plot_sunburst(plot_df, 'Figure: ENA Aquatic "Environmental" readrun records, by ocean', path_list,
                  'record_count', plotfile)


    sys.exit()
    return df


def collection_date_year(value):
    if value == "":
        return ""
    elif re.search("^missing|^not", value):
        return ""
    elif re.search("^[0-9]{4}$", value):
        return value
    elif re.search("^[0-9]{4}[-/]", value):
        return value[0:4]
    elif re.search("^[0-9]{2}/[0-9]{2}/[0-9]{4}", value):
        return value.split("/")[2]
    elif re.search("[0-9]{4}$", value):
        return value[:-4]
    elif re.search("^[0-9]{4}$", value):
        return re.findall("^[0-9]{4}", value)[0]
    elif re.search("[0-2][0-9]$", value):
        extract_value = int(value[-2:])
        if extract_value > 50:
            return '19' + str(extract_value)
        else:
            return '20' + str(extract_value)
    else:
        #logger.info(f"no year match for {value}")  # e,g,  f"no year match for {value}": 'no year match for restricted access'
        return ""

def create_year_bins(value):
    """
    trying to bin years in 5 year
    :param value:
    :return:
    """
    min=1950
    max=2025
    if isinstance(value, int):
        if value <= min:
            return str(min) + "-pre"
        for x in range(min, max, 5):
            # 2023 far more likely than min so could try reversing the order
            # logger.info(value)
            if value <= x:
               return f"{str(x)}-{str(x+5)}"
    return None

def detailed_environmental_analysis(df):
    """
    uses the tags to predict the environment, is rather rough and ready
    assuming is all terrestrial with a low confidence
    :param df:
    :return: df        with the addition of ['env_prediction']  ['env_prediction_hl']  ['env_confidence']
    """
    logger.info(len(df))
    def process_env_tags(value):
        my_tag_list = value.split(';')
        my_env_tags = [s for s in my_tag_list if "env_" in s]
        return my_env_tags

    print_value_count_table(df.tag)
    # logger.info(df.tag.head(50))
    df['env_tag'] = df['tag'].apply(process_env_tags)
    df['env_tag_string'] = df['env_tag'].apply(lambda x: ';'.join(x))
    # logger.info(df['env_tag'].value_counts().head(5))
    cp_df = df.copy()
    def is_w_env_tags(value_list):
        if len(value_list) == 0:
            return False
        return True

    # tmp_df = cp_df[len(cp_df.env_tag)> 0]
    df['is_env_tags'] = df['env_tag'].apply(is_w_env_tags)
    logger.debug(f"{df['env_tag'].value_counts().head()}")
    logger.info(f"{df.columns}")
    tmp_df = df[df['is_env_tags'] == True]
    # print_value_count_table(tmp_df.env_tag)
    logger.debug(tmp_df['env_tag'].value_counts().head(5))
    logger.debug(tmp_df['env_tag'].explode().unique())
    # tmp_df['env_tag_string'] = tmp_df['env_tag'].apply(lambda x: ';'.join(x))
    # tmp_df['env_tag_string'] = tmp_df['env_tag'].str.join(';')
    # logger.info(tmp_df['env_tag_string'].unique())
    # logger.info(my_env_lists['env_tag'])
    #  for tag in tmp_df['env_tag'].unique():
    #      logger.info(tag)
    logger.info(f"starting len={len(df)} filtered len={len(tmp_df)}")

    tag_string_assignment = {}
    # f = tmp_df['env_tag_string'].str.contains("env_geo",na=False)
    # sys.exit()

    logger.info("++++++++++++++++++++++++++++++++++++++++++++++++")
    not_assigned = []
    multiples = []
    aquatic_tag_set = ['env_geo:marine', 'env_geo:freshwater', 'env_geo:brackish', 'env_geo:coastal', 'env_tax:marine',
                        'env_tax:freshwater', 'env_tax:brackish', 'env_tax:coastal']
    terrestrial_tag_set = ['env_geo:terrestrial', 'env_tax:terrestrial']
    for tags in tmp_df['env_tag_string'].unique():
        logger.debug(tags)
        tag_list = tags.split(';')

        if 'env_geo' in tags:
            # logger.info(f"----------------------{tags}")
            matches = re.findall(r'env_geo[^;]*', tags)
            # logger.info(matches)
            if len(matches) > 1:
                msg = f"WARNING, multiple GEO matches={matches}, tags={tags} THAT IS NOT YET HANDLED"
                if 'env_geo:coastal' in matches and 'env_geo:marine' in matches:
                    if len(tag_list) == 2:
                        tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'medium'}
                    elif ('env_tax:marine' in tags or 'env_tax:coastal' or 'env_tax:brackish' in tags):
                        tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'high'}
                    else:
                        logger.debug(msg)
                        multiples.append(msg)
                elif 'env_geo:terrestrial' in tags:
                    if 'env_geo:freshwater' in tags:
                        tag_string_assignment[tags] = {'prediction': 'freshwater', 'confidence': 'low'}
                    elif 'env_geo:coastal' in tags:
                        tag_string_assignment[tags] = {'prediction': 'terrestrial', 'confidence': 'medium'}
                    else:
                        multiples.append(msg)
                elif 'env_geo:marine' in tags:
                        if 'env_tax:marine' in tags:
                            tag_string_assignment[tags] = {'prediction': 'marine', 'confidence': 'medium'}
                        elif 'env_geo:freshwater' in tags and 'env_tax:freshwater' in tags:
                            tag_string_assignment[tags] = {'prediction': 'freshwater', 'confidence': 'medium'}
                        elif 'env_geo:freshwater' in tags:
                            tag_string_assignment[tags] = {'prediction': 'brackish', 'confidence': 'low'}
                        else:
                            multiples.append(msg)
                else:
                    logger.debug(matches)
                    multiples.append(msg)
            else:  # ie. one match
                if matches[0] == 'env_geo:marine' and 'env_tax:marine' in tags:
                    tag_string_assignment[tags] = {'prediction': 'marine', 'confidence': 'high'}
                elif matches[0] == 'env_geo:freshwater' and 'env_geo:freshwater' in tags:
                    tag_string_assignment[tags] = {'prediction': 'freshwater', 'confidence': 'high'}
                elif matches[0] == 'env_geo:coastal' and 'env_geo:coastal' in tags:
                    tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'high'}
                elif matches[0] == 'env_geo:brackish' and 'env_geo:brackish' in tags:
                    tag_string_assignment[tags] = {'prediction': 'brackish', 'confidence': 'high'}
                elif matches[0] == 'env_geo:terrestrial' and 'env_geo:terrestrial' in tags:
                    tag_string_assignment[tags] = {'prediction': 'terrestrial', 'confidence': 'high'}
                elif len(tag_list) == 2 and 'env_geo:terrestrial' not in tags:
                    if tag_list[0] in aquatic_tag_set and tag_list[1] in aquatic_tag_set:
                        tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'medium'}
                    elif (tag_list[0] in terrestrial_tag_set and tag_list[1] in aquatic_tag_set) or (tag_list[1] in terrestrial_tag_set and tag_list[0] in aquatic_tag_set):
                            tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
                elif len(tag_list) == 3 and 'env_geo:terrestrial' not in tags:
                    if tag_list[0] in aquatic_tag_set and (tag_list[1] in aquatic_tag_set or tag_list[2] in aquatic_tag_set):
                        tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'medium'}
                    else:
                        tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
                else:
                    logger.debug("________________________________________________________")
                    logger.debug(matches[0])
                    if len(tag_list) == 1:
                        value = re.findall(r'env_geo:(.*)', matches[0])[0]
                        tag_string_assignment[tags] = {'prediction': value, 'confidence': 'medium'}
                    elif matches[0] == 'env_geo:coastal' and "brackish" in tags:
                        tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'medium'}
                    elif matches[0] == 'env_geo:marine' and ("brackish" in tags or "coastal" in tags):
                        tag_string_assignment[tags] = {'prediction': 'coastal', 'confidence': 'medium'}
                    elif matches[0] == 'env_geo:marine' and ("terrestrial" in tags):
                        tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
                    else:
                        if re.match(r'^(env_tax:freshwater;env_geo:marine|env_tax:freshwater;env_tax:terrestrial;env_geo:marine)$',tags):
                            not_assigned.append(tags)
                        else:
                            logger.error(f"Not assigned--->{tags} len_tags={len(tag_list)}")
                            sys.exit()

        # the following are where there are no env_geo: tgs
        elif len(tag_list) == 1:
            value = re.findall(r'env_tax:(.*)', tag_list[0])[0]
            tag_string_assignment[tags] = {'prediction': value, 'confidence': 'medium'}
        elif len(tag_list) == 2:
            if tag_list[0] in aquatic_tag_set and tag_list[1] in aquatic_tag_set:
                tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'medium'}
            elif tag_list[0] in aquatic_tag_set and tag_list[1] in aquatic_tag_set:
                tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
            elif tag_list[0] in aquatic_tag_set and tag_list[1] in terrestrial_tag_set:
                tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
            elif ((tag_list[0] in terrestrial_tag_set and tag_list[1] in aquatic_tag_set) or
                  (tag_list[1] in terrestrial_tag_set and tag_list[0] in aquatic_tag_set)):
                tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
            else:
                not_assigned.append(tags)
        elif len(tag_list) == 3:
                if tag_list[0] in aquatic_tag_set and (
                        tag_list[1] in aquatic_tag_set or tag_list[2] in aquatic_tag_set):
                    tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'low'}
                elif tag_list[1] in aquatic_tag_set and (
                        tag_list[2] in aquatic_tag_set):
                    tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'low'}
                elif tag_list[0] in terrestrial_tag_set and (
                            tag_list[1] in aquatic_tag_set and tag_list[2] in aquatic_tag_set):
                    tag_string_assignment[tags] = {'prediction': 'mixed', 'confidence': 'low'}
                else:
                    not_assigned.append(tags)
        elif len(tag_list) == 4:
                if (tag_list[0] in aquatic_tag_set or tag_list[1] in aquatic_tag_set) and (
                        tag_list[2] in aquatic_tag_set or tag_list[3] in aquatic_tag_set):
                    tag_string_assignment[tags] = {'prediction': 'mixed_aquatic', 'confidence': 'low'}
                else:
                    not_assigned.append(tags)
        else:
            not_assigned.append(tags)
            logger.debug(f"Not assigned--->{tags} len_tags={len(tag_list)}")
    # END OF FOR
    logger.info("finished big for loop")

    # logger.info(tag_string_assignment)
    if len(multiples) > 0:
        logger.error("Apologies: you need to address these cases before proceeding")
        logger.error(f"multiples:{multiples}")
        logger.error(f"not_assigned: {not_assigned}")
        sys.exit()
    elif len(not_assigned) > 0:
        logger.error("Apologies: you need to address these cases before proceeding")
        logger.error(f"not_assigned: {not_assigned}")
        sys.exit()

    # logger.info('env_tax:freshwater;env_tax:terrestrial;env_geo:marine')
    # tmp_df = df[df['env_tags'].str.contains('env_tax:freshwater;env_tax:terrestrial;env_geo:marine')]
    # logger.info(tmp_df['sample_accession'].unique())
    logger.info("about to do a bunch of assignments")

    def actually_assign_env_info_pred(value):
        # logger.info(value)
        if len(value) > 1:
            # return tag_string_assignment[value]['prediction'], tag_string_assignment[value]['confidence']
            return tag_string_assignment[value]['prediction']
        return "terrestrial_assumed"

    def actually_assign_env_info_conf(value):
        # logger.info(value)
        if len(value) > 1:
            # return tag_string_assignment[value]['prediction'], tag_string_assignment[value]['confidence']
            return tag_string_assignment[value]['confidence']
        return "low"

    def add_ocean_evidence(vec):
        env_prediction = vec[0]
        ocean_evidence = vec[1]
        if ocean_evidence != "not ocean" and env_prediction in ['terrestrial', 'mixed']:
            logger.debug(f"ocean_evidence: {ocean_evidence}")
            return "marine"
        return env_prediction

    aquatic_set = ('marine', 'brackish', 'coastal', 'freshwater', 'mixed_aquatic')
    logger.info(f"aquatic_set: {aquatic_set}")

    def actually_assign_env_info_pred_hl(value):
        # logger.info(value)
        if value != "terrestrial_assumed" and value != None:
            if value == "terrestrial":
                   return value
            elif value in aquatic_set:
                    return "aquatic"
            else:
                   return "mixed"
            return "terrestrial_assumed"
        return "terrestrial_assumed"

        #, tag_string_assignment[value]['confidence']
    logger.info(len(df))

    df['env_prediction'] = df['env_tags'].apply(actually_assign_env_info_pred)
    df['env_confidence'] = df['env_tags'].apply(actually_assign_env_info_conf)
    df['env_prediction'] = df[['env_prediction', 'ocean']].apply(add_ocean_evidence, axis=1)


    df['env_prediction_hl'] = df['env_prediction'].apply(actually_assign_env_info_pred_hl)
    print()
    logger.info("\n" + df.groupby(['env_prediction', 'env_confidence']).size().to_frame().to_string())
    print_value_count_table(df['env_prediction_hl'])

    #


    path = ['env_prediction_hl', 'env_prediction', 'env_confidence','ocean']
    value_field = 'record_count'
    plot_df = df.groupby(path).size().to_frame('record_count').reset_index()
    plotfile = "../images/env_predictions.png"
    plot_sunburst(plot_df, "Figure: ENA readrun Aquatic environmental predictions using species and lat/lons (Sunburst Plot)", path, value_field, plotfile)

    logger.info("finished All the analysis for the environmental predictions<-------------------")
    return df




def analyse_readrun_detail(df):
    logger.info("in analyse_readrun_detail")

    # doing some testing .... delete these when done

    # count = 0
    # for record in env_readrun_detail:
    #
    #     logger.info(record)
    #     count = count + 1
    #     if count > 3:
    #         break


    # ['sample_accession', 'run_accession', 'library_strategy',
    #                        'library_source', 'instrument_platform', 'lat', 'lon', 'country',
    #                        'broad_scale_environmental_context', 'tax_id', 'checklist',
    #                        'collection_date', 'ncbi_reporting_standard', 'target_gene', 'tag']
    # dtype = 'object')

    # df = df.sample(n=100000)
    # df['sample_accession'] = df['sample_accession'].to_string()
    logger.info("cols:{}".format(df.columns))
    logger.info(df['sample_accession'])
    df = add_insdc_member_receiver(df)
    print_value_count_table(df.insdc_member_receiver)

    # outfile = all_sample_accessions.tsv"
    # logger.info(outfile)
    # df.sample_accession.to_csv(outfile)

    # uncomment when running for real
    # target_gene_analysis(df)

    print('NCBI "checklists":')
    print_value_count_table(df.ncbi_reporting_standard)
    print('ENA "checklists":')
    print_value_count_table(df.checklist)

    df = clean_dates_in_df(df)

    df['lat'] = pd.to_numeric(df['lat'], errors = 'coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors = 'coerce')

    print_value_count_table(df.collection_year)
    print_value_count_table(df.collection_year_bin)
    logger.info(f"before experimental_analysis_inc_filtering filtered: rownum={len(df)}")
    df = experimental_analysis_inc_filtering(df)
    logger.info(f"after experimental_analysis_inc_filtering filtered: rownum={len(df)}")


    logger.info("-------------about to do geographical------------------------")
    df = do_geographical(df)
    sys.exit("PREMATURE")
    logger.info("-------------about to do taxonomic_analysis------------------------")
    df = taxonomic_analysis(df)
    # logger.info(df)
    # logger.info(df.dtypes)
    logger.info("-------------about to do detailed_environmental_analysis------------------------")
    df = detailed_environmental_analysis(df)
    logger.info("-------------end of analyse_readrun_detail------------------------")
    


def main():
    # df_all_study_details = analyse_barcode_study_details(get_all_study_details())
    # logger.info(len(df_all_study_details))
    #
    # sample_ids = get_env_sample_ids()
    # logger.info(len(sample_ids))
    # readrun_ids = get_env_readrun_ids()
    # logger.info(len(readrun_ids))

    # get_all_study_details()
    # sys.exit()

    # df_aquatic_env_readrun_detail_pickle = "df_aquatic_env_readrun_detail.pickle"
    # env_readrun_detail = get_env_readrun_detail(10000)
    # df_env_readrun_detail = filter_for_aquatlogger.info(env_readrun_detail)
    # pickle_data_structure(df_env_readrun_detail, df_aquatic_env_readrun_detail_pickle)
    # logger.info("WTF")
    # sys.exit()
    pickle_file = 'df_aquatic_env_readrun_detail.pickle-keep'
    pickle_file = 'df_aquatic_env_readrun_detail.pickle'
    df_aquatic_env_readrun_detail = pd.read_pickle(pickle_file)
    logger.info(f"unpickled from {pickle_file} row total={len(df_aquatic_env_readrun_detail)}")
    logger.info(f"columns={df_aquatic_env_readrun_detail.columns}")
    #
    #
    # This is what used to be run!
    # readrun_ids_set = set(df_env_readrun_detail['run_accession'])
    # logging.info(f"readrun_ids_set={len(readrun_ids_set)}")
    # sample_ids_set = set(df_env_readrun_detail['sample_accession'])
    # logging.info(f"sample_ids_set={len(sample_ids_set)}")
    #
    analyse_readrun_detail(df_aquatic_env_readrun_detail)

    
    

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)

    coloredlogs.install(logger = logger)
    logger.propagate = False
    ch = logging.StreamHandler(stream = sys.stdout)
    ch.setFormatter(fmt = my_coloredFormatter)
    logger.addHandler(hdlr = ch)
    logger.setLevel(level = logging.INFO)

    # Read arguments from command line
    prog_des = "Script to query ENA(INSDC) resources, but mainly to analyse the eDNA metadata from the different work"

    parser = argparse.ArgumentParser(description = prog_des)

    # Adding optional argument, n.b. in debugging mode in IDE, had to turn required to false.
    parser.add_argument("-d", "--debug_status",
                        help = "Debug status i.e.True if selected, is verbose",
                        required = False, action = "store_true")

    parser.parse_args()
    args = parser.parse_args()

    if args.debug_status:
        ic.enable()
        logger.setLevel(level = logging.DEBUG)
    else:
        ic.disable()
    logger.info(prog_des)

    main()
