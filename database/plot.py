import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def generate_colours(df, column, cmap_name):
    # TODO: they get generated a little different than what pandas does automatically
    labels = np.sort(df[column].unique())
    cmap = plt.get_cmap(cmap_name)
    colours = cmap(np.linspace(0,1,len(labels)+1))
    colour_dict = dict(zip(labels,colours))
    return colour_dict


def populate_plot_options(kind, alpha, cmap_name, df=pd.DataFrame(),
                          index=False, legend=False, stacked=True):
    plot_options = dict()
    plot_options['kind'] = kind
    plot_options['alpha'] = alpha

    if not df.empty:
        colour_dict = generate_colours(df, legend, cmap_name)
        label = df.loc[index,legend]
        plot_options['c'] = colour_dict[label]
        plot_options['label'] = str(label)
    else:
        plot_options['colormap'] = cmap_name

    if kind == 'line':
        plot_options['linewidth'] = 2
        # plot_options['marker'] = '.'
        # plot_options['markersize'] = 12
        # TODO: move default marker size to MatplotlibSettings.py

    elif kind == 'scatter':
        plot_options['edgecolors'] = 'face'
        plot_options['s'] = 12

    elif 'bar' in kind:
        plot_options['stacked'] = stacked
        plot_options['edgecolor'] = 'none'

    return plot_options