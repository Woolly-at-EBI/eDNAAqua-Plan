#!/usr/bin/env python3
"""Script: run_ena_get_filter_analysis.py is to get, filter and analyse aquatic eDNA from ENA

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2024-06-14
__docformat___ = 'reStructuredText'

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
from get_environmental_info import get_env_readrun_detail, logger
from eDNA_utilities import unpickle_data_structure
from analyse_environmental_info import analyse_readrun_detail


pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)
logger = logging.getLogger(name = 'mylogger')


my_coloredFormatter = coloredlogs.ColoredFormatter(
    fmt='[%(name)s] %(asctime)s %(funcName)s %(lineno)-3d  %(message)s',
    level_styles=dict(
        debug=dict(color='white'),
        info=dict(color='green'),
        warning=dict(color='yellow', bright=True),
        error=dict(color='red', bold=True, bright=True),
        critical=dict(color='black', bold=True, background='red'),
    ),
    field_styles=dict(
        name=dict(color='white'),
        asctime=dict(color='white'),
        funcName=dict(color='white'),
        lineno=dict(color='white'),
    )
)




def main():
    logger.info("get&filter, then analyse")
    restrict_record_total = 1000
    # env_readrun_detail = get_env_readrun_detail(restrict_record_total)
    # df_env_readrun_detail = filter_for_aquatic(env_readrun_detail)
    pickle_file = 'df_aquatic_env_readrun_detail.pickle-keep'
    df_aquatic_env_readrun_detail = unpickle_data_structure(pickle_file)
    logger.info(f"About to do the analysis for {len(df_aquatic_env_readrun_detail)} records")
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
    prog_des = "Script to query ENA(INSDC) resources fpr eDNA metadata "

    parser = argparse.ArgumentParser(description = prog_des)

    # Adding optional argument, n.b. in debugging mode in IDE, had to turn required to false.
    parser.add_argument("-d", "--debug_status",
                        help = "Debug status i.e.True if selected, is verbose",
                        required = False, action = "store_true")

    parser.parse_args()
    args = parser.parse_args()

    if args.debug_status:
        logger.setLevel(level = logging.DEBUG)
    else:
        logger.setLevel(level = logging.INFO)
    logger.info(prog_des)

    main()
