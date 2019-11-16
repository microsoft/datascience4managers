# metric_graphics.py
# JMA Nov 2019
# Bokeh plots of confusion matrix and prec-recal charts
import os, sys
from pathlib import Path
import time

import numpy as np
import pandas as pd
from bokeh.io import output_file, save, show
from bokeh.models import  BasicTicker, ColorBar, LinearColorMapper, ColumnDataSource, FixedTicker, PrintfTickFormatter
from bokeh.plotting import figure
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from bokeh.transform import transform

### config constants 
VERBOSE = False
ROOT_DIR = Path('D:/OneDrive - Microsoft/data/20news')

########################################################################
# Input - any matrix with labeled rows and cols as a pd.DataFrame
def matrix_heatmap(the_matrix):
    'Create a bokeh graphic with matrix cells colored by value. Or use bokeh "heatmap".'
    # pandas 'stack' is equivalent to R reshape gather, or melt from reshape2, from wide to long format. 
    # Prepare data.frame in the right format
    the_matrix.drop(['F', 'sup'], axis=1, inplace=True)
    df = the_matrix.stack().rename("value").reset_index()

    #  The plot output:
    output_file("myPlot.html")

    # You can use your own palette here
    colors = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

    # Had a specific mapper to map color with value
    mapper = LinearColorMapper(
        palette=colors, low=df.value.min(), high=df.value.max())
    # Define a figure
    p = figure(
        plot_width=300,
        plot_height=800,
        title="My plot",
        y_range=list(df.nms.drop_duplicates()),
        x_range=list(df.level_1.drop_duplicates()),
        toolbar_location=None,
        tools="",
        x_axis_location="above")
    # Create rectangle for heatmap
    p.rect(
        y="nms",
        x="level_1",
        width=1,
        height=1,
        source=ColumnDataSource(df),
        line_color=None,
        fill_color=transform('value', mapper))
    # Add legend
    color_bar = ColorBar(
        color_mapper=mapper,
        location=(0, 0),
        ticker=BasicTicker(desired_num_ticks=len(colors)))

    p.add_layout(color_bar, 'right')
    show(p)

###############################################################################
def main(input_dir):
    pass

########################################################################
if __name__ == '__main__':

    if '-v' in sys.argv:
        k = sys.argv.index('-v')
        VERBOSE = True
    np.set_printoptions(linewidth=100)
    main(ROOT_DIR)
    print(sys.argv, "\nDone in ", '%5.3f' % time.process_time(), " secs! At UTC: ", time.asctime(time.gmtime()), file=sys.stderr)

#EOF