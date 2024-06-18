#!/usr/bin/env python3
"""Script of mine_bioinfomatics_eval.py is to mine the bioinfomatics evaluation spreadsheet file

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2024-06-18
__docformat___ = 'reStructuredText'

"""


import pandas as pd
import sys
import logging
from eDNA_utilities import logger,  my_coloredFormatter, coloredlogs

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def mine_bioinfomatics_eval():
    """"""
    ss_url = r'https://docs.google.com/spreadsheets/d/1yppKMagcIakPDY4RpeOkwYW1EYJ28t0LqRrj37x6oss/edit?usp=sharing'
    sheet_name = 'eDNA'
    sheet_id = '1yppKMagcIakPDY4RpeOkwYW1EYJ28t0LqRrj37x6oss'
    ss_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

    logger.info(f'Mined bioinfomatics evaluation spreadsheet, sheet=eDNA file: {ss_url}')
    df = pd.read_csv(ss_url)
    logger.info(f"\n{df.head()}")



def main():
    print("FFS")
    mine_bioinfomatics_eval()

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)

    coloredlogs.install(logger = logger)
    logger.propagate = False
    ch = logging.StreamHandler(stream = sys.stdout)
    ch.setFormatter(fmt = my_coloredFormatter)
    logger.addHandler(hdlr = ch)
    logger.setLevel(level = logging.INFO)


    main()
