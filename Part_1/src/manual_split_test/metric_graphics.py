# metric_graphics.py
# JMA Nov 2019
# Bokeh plots of confusion matrix and prec-recal charts
import os, sys
from pathlib import Path
import time

import numpy as np
import pandas as pd
from bokeh.io import output_file, save, show
from bokeh.models import  BasicTicker, ColorBar, LinearColorMapper, ColumnDataSource, FixedTicker, PrintfTickFormatter, Text
from bokeh.plotting import figure
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from bokeh.transform import transform
from bokeh.palettes import brewer
from bokeh.layouts import row

### config constants 
VERBOSE = False
ROOT_DIR = Path('C:/Users/joagosta/OneDrive - Microsoft/data/20news')

########################################################################
# Input - any matrix with labeled rows and cols as a pd.DataFrame
def summary_accuracy(the_trends):
    s = figure(plot_width=700, plot_height=700, background_fill_color="#fafafa", title="Train - Test Accuracies")
    the_trends.reset_index(inplace=True)
    source = ColumnDataSource(the_trends)

    #glyph_1 = l.line('Date','RPI',source=source, legend='RPI', color='red')
    s.line('index','Train_acc',source=source , line_width = 3,color='blue')
    s.line('index','Train_pr',source=source, line_dash=[10,10], line_width = 3, color='blue')
    s.line('index','Train_rcl',source=source , line_dash=[5,3], line_width = 3,color='blue')
    s.line('index','Test_pr',source=source, line_width = 3,color='darkorange')
    s.line('index','Test_acc',source=source , line_dash=[10,10], line_width = 3,color='darkorange')
    s.line('index','Test_rcl',source=source, line_dash=[5,3], line_width = 3,color='darkorange')
    return s

########################################################################
# Input - any matrix with labeled rows and cols as a pd.DataFrame
def matrix_heatmap(the_matrix):
    'Create a bokeh graphic with matrix cells colored by value. Or use bokeh "heatmap".'
    # pandas 'stack' is equivalent to R reshape gather, or melt from reshape2, from wide to long format. 
    # Prepare data.frame in the right format
    # the_matrix.drop(['F', 'sup'], axis=1, inplace=True)
    # the_matrix.columns=  the_matrix.index
    df = the_matrix.stack().rename("value").reset_index()

    #  The plot output:
    # output_file(ROOT_DIR / "cmPlot.html")

    # You can use your own palette here
    colors = brewer['YlGnBu'][9][1:9]

    # Had a specific mapper to map color with value
    mapper = LinearColorMapper(
        palette=colors, low=df.value.min(), high=df.value.max())
    # Define a figure
    p = figure(
        plot_width=800,
        plot_height=700,
        title="20 Newsgroups Confusion Matrix",
        y_range=list(df.level_0.drop_duplicates()),
        x_range=list(df.level_1.drop_duplicates()),
        toolbar_location=None,
        tools="",
        x_axis_location="above")

    df['cnt'] = df['value'].apply(str)
    cds = ColumnDataSource(df)
    # Create rectangle for heatmap
    p.rect(
        y="level_0",
        x="level_1",
        alpha = 0.4,
        width=1,
        height=1,
        source=cds,
        line_color=None,
        fill_color=transform('value', mapper))
    glyph = Text(y="level_0", x="level_1", text="cnt", x_offset= -10.0, y_offset=10.0, text_color="black")
    p.add_glyph(cds, glyph)

    #Add legend
    color_bar = ColorBar(
        color_mapper=mapper,
        location=(0,0),
        ticker=BasicTicker(desired_num_ticks=len(colors)))
    p.add_layout(color_bar, 'right')

    return p

###############################################################################
def main(input_dir):
    cm = pd.read_csv(ROOT_DIR / 'cm.csv', header = 0, index_col=0)
    p = matrix_heatmap(cm)
    sum = pd.read_csv(ROOT_DIR / 'summary.csv', header = 0, index_col=0)
    s = summary_accuracy(sum)
    show(row(p, s))

########################################################################
if __name__ == '__main__':

    if '-v' in sys.argv:
        k = sys.argv.index('-v')
        VERBOSE = True
    np.set_printoptions(linewidth=100)
    main(ROOT_DIR)
    print(sys.argv, "\nDone in ", '%5.3f' % time.process_time(), " secs! At UTC: ", time.asctime(time.gmtime()), file=sys.stderr)

#EOF