#!/usr/bin/env python3
"""Script of eDNA_utilities.py contains commonyl used functions

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2024-06-14
__docformat___ = 'reStructuredText'

"""
import pickle
import logging
import coloredlogs
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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


def pickle_data_structure(data_structure, filename):
    try:
        with open(filename, "wb") as f:
            pickle.dump(data_structure, f, protocol = pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)


def unpickle_data_structure(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)





def run_webservice(url):
    """

    :param url:
    :return:
    """
    r = requests.get(url)
    logger.info(url)

    if r.status_code == 200:
        return r.text
    else:
        ic.enable()
        logger.info(r.status_code)
        logger.info(f"for url={r.url}")
        logger.info("retrying in 5 seconds, once")
        time.sleep(5)
        if r.status_code == 200:
            ic.disable()
            return r.text
        else:
            logger.info(f"Still {r.status_code} so exiting")
        sys.exit(1)


def get_shorter_list(record_list, k):
        """
        shortens a list of records randomly, if k =0 it returns all records
        :param record_list: list of records
        :param k: number of records to return
        :return: randomly chosen shorter record_list
        """
        if k == 0:
            return record_list
        elif len(record_list) < k:
            logger.warning(f"in shorten_list k={k}, len(record_list)={len(record_list)}, so returning full list")
            return record_list

        shortened_list = random.sample(record_list, k)
        logger.info(f"shortened_list to {k} from {len(record_list)}")
        return shortened_list


def get_percentage_list(gene_list):
    """
    Takes
    :param gene_list:
    :return:
    """
    # logger.info(Counter(gene_list))
    c = Counter(gene_list)
    out = sorted([(i, c[i], str(round(c[i] / len(gene_list) * 100.0, 2)) + "%") for i in c])
    logger.info(out)
    return out

    
def print_value_count_table(df_var):
    counts = df_var.value_counts()
    percs = df_var.value_counts(normalize = True)
    tmp_df = pd.concat([counts, percs], axis = 1, keys = ['count', 'percentage'])
    tmp_df['percentage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in tmp_df['percentage']], index = tmp_df.index)
    logger.info(tmp_df)


    
def generate_sankey_chart_data(df, columns: list, sankey_link_weight: str):

    column_values = [df[col] for col in columns]
    logger.info(column_values)

    # this generates the labels for the sankey by taking all the unique values
    labels = sum([list(node_values.unique()) for node_values in column_values], [])
    logger.info(labels)

    # initializes a dict of dicts (one dict per tier)
    link_mappings = {col: {} for col in columns}

    # each dict maps a node to unique number value (same node in different tiers
    # will have different number values
    i = 0
    for col, nodes in zip(columns, column_values):
        for node in nodes.unique():
            link_mappings[col][node] = i
            i = i + 1

    # specifying which columns are serving as sources and which as sources
    # ie: given 3 df columns (col1 is a source to col2, col2 is target to col1 and
    # a source to col 3 and col3 is a target to col2
    source_nodes = column_values[: len(columns) - 1]
    target_nodes = column_values[1:]
    source_cols = columns[: len(columns) - 1]
    target_cols = columns[1:]
    links = []

    # loop to create a list of links in the format [((src,tgt),wt),(),()...]
    for source, target, source_col, target_col in zip(source_nodes, target_nodes, source_cols, target_cols):
        for val1, val2, link_weight in zip(source, target, df[sankey_link_weight]):
            links.append(
                (
                    (
                        link_mappings[source_col][val1],
                        link_mappings[target_col][val2]
                    ),
                    link_weight,
                )
            )

    # creating a dataframe with 2 columns: for the links (src, tgt) and weights
    df_links = pd.DataFrame(links, columns = ["link", "weight"])

    # aggregating the same links into a single link (by weight)
    df_links = df_links.groupby(by = ["link"], as_index = False).agg({"weight": sum})

    # generating three lists needed for the sankey visual
    sources = [val[0] for val in df_links["link"]]
    targets = [val[1] for val in df_links["link"]]
    weights = df_links["weight"]

    logger.info(labels, sources, targets, weights)
    return labels, sources, targets, weights

def plot_sankey(df, sankey_link_weight, columns, title, plotfile):

    # list of list: each list are the set of nodes in each tier/column

    (labels, sources, targets, weights) = generate_sankey_chart_data(df, columns, sankey_link_weight)

    color_link = ['#000000', '#FFFF00', '#1CE6FF', '#FF34FF', '#FF4A46',
                  '#008941', '#006FA6', '#A30059', '#FFDBE5', '#7A4900',
                  '#0000A6', '#63FFAC', '#B79762', '#004D43', '#8FB0FF',
                  '#997D87', '#5A0007', '#809693', '#FEFFE6', '#1B4400',
                  '#4FC601', '#3B5DFF', '#4A3B53', '#FF2F80', '#61615A',
                  '#BA0900', '#6B7900', '#00C2A0', '#FFAA92', '#FF90C9',
                  '#B903AA', '#D16100', '#DDEFFF', '#000035', '#7B4F4B',
                  '#A1C299', '#300018', '#0AA6D8', '#013349', '#00846F',
                  '#372101', '#FFB500', '#C2FFED', '#A079BF', '#CC0744',
                  '#C0B9B2', '#C2FF99', '#001E09', '#00489C', '#6F0062',
                  '#0CBD66', '#EEC3FF', '#456D75', '#B77B68', '#7A87A1',
                  '#788D66', '#885578', '#FAD09F', '#FF8A9A', '#D157A0',
                  '#BEC459', '#456648', '#0086ED', '#886F4C', '#34362D',
                  '#B4A8BD', '#00A6AA', '#452C2C', '#636375', '#A3C8C9',
                  '#FF913F', '#938A81', '#575329', '#00FECF', '#B05B6F',
                  '#8CD0FF', '#3B9700', '#04F757', '#C8A1A1', '#1E6E00',
                  '#7900D7', '#A77500', '#6367A9', '#A05837', '#6B002C',
                  '#772600', '#D790FF', '#9B9700', '#549E79', '#FFF69F',
                  '#201625', '#72418F', '#BC23FF', '#99ADC0', '#3A2465',
                  '#922329', '#5B4534', '#FDE8DC', '#404E55', '#0089A3',
                  '#CB7E98', '#A4E804', '#324E72', '#6A3A4C'
                  ]


    #---------------------------------
    fig = go.Figure(data = [go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            #label = ["A1", "A2", "B1", "B2", "C1", "C2"],
            label = labels,
            color = "blue"
        ),
        link = dict(
            # source = [0, 1, 0, 2, 3, 3],  # indices correspond to labels, eg A1, A2, A1, B1, ...
            # target = [2, 3, 3, 4, 4, 5],
            # value = [8, 4, 2, 8, 4, 2]
            source = sources,
            target = targets,
            value = weights,
            color=color_link
        ))])


    fig.update_layout(title_text = title, font_size = 10)
    if plotfile == "plot":
            fig.show()
    else:
            logger.info(f"Sankey plot to {plotfile}")
            fig.write_image(plotfile)
