import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

mpl.rc('font', **{'family': 'sans-serif', 'sans-serif': [u'Arial', u'Liberation Sans']})
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['xtick.labelsize'] = 16
mpl.rcParams['ytick.labelsize'] = 16
mpl.rcParams['axes.titlesize'] = 18
mpl.rcParams['legend.fontsize'] = 20
mpl.rcParams['grid.color'] = '777777'  # grid color
mpl.rcParams['xtick.major.pad'] = 2  # padding of tick labels: default = 4
mpl.rcParams['ytick.major.pad'] = 1  # padding of tick labels: default = 4


plt.rc('font', size=14)          # controls default text size
plt.rc('axes', titlesize=24)     # fontsize of the axes title
plt.rc('axes', labelsize=24)     # fontsize of the x and y labels
plt.rc('xtick', labelsize=16)    # fontsize of the tick labels
plt.rc('ytick', labelsize=16)    # fontsize of the tick labels

expt_markers = {
    'lp_results':'s',
    'ilp_results':'*',
    'milp_results':'H',
    'flow_networkx_results':'h',
    'flow_lp_results':'p',
    'flow_tuple_linearization_networkx_results':'^',
    'flow_tuple_linearization_lp_results':'<',
    'flow_witness_linearization_networkx_results':'v',
    'flow_witness_linearization_lp_results':'>',
    'ilp_results_600':'+',
    'ilp_results_60':'_',
    'ilp_results_10':'|',
    'lp_results: approximation': 'x'
}
expt_colors = {
    'lp_results':'tab:blue',
    'ilp_results':'tab:orange',
    'milp_results':'tab:red',
    'flow_lp_results':'tab:green',
    'flow_tuple_linearization_lp_results':'greenyellow',
    'flow_witness_linearization_lp_results':'tab:olive',
    'ilp_results_10':'tab:purple',
    'lp_results: approximation': 'tab:gray',
    'flow_networkx_results':'steelblue',
    'flow_tuple_linearization_networkx_results':'tab:cyan',
    'flow_witness_linearization_networkx_results':'skyblue',
    'ilp_results_600':'orchid',
    'ilp_results_60':'pink'   
}
expt_colors_light = {
    'lp_results':'tab:blue',
    'ilp_results':'tab:orange',
    'milp_results':'tab:red',
    'flow_lp_results':'tab:green',
    'flow_tuple_linearization_lp_results':'greenyellow',
    'flow_witness_linearization_lp_results':'tab:olive',
    'ilp_results_10':'tab:purple',
    'lp_results: approximation': 'tab:gray',
    'flow_networkx_results':'steelblue',
    'flow_tuple_linearization_networkx_results':'tab:cyan',
    'flow_witness_linearization_networkx_results':'skyblue',
    'ilp_results_600':'orchid',
    'ilp_results_60':'pink'
}
expt_labels = {
    'lp_results':'LP',
    'ilp_results':'ILP',
    'milp_results':'MILP',
    'flow_networkx_results':'Flow-NX',
    'flow_lp_results':'Flow',
    'flow_tuple_linearization_networkx_results':'Flow-TL-NX',
    'flow_tuple_linearization_lp_results':'Flow-CTL',
    'flow_witness_linearization_networkx_results':'Flow-WL-NX',
    'flow_witness_linearization_lp_results':'Flow-CWL',
    'ilp_results_600':'ILP(600)',
    'ilp_results_60':'ILP(60)',
    'ilp_results_10':'ILP(10)',
    'lp_results: approximation': 'LP-UB'
}

timing_lines = ['lp_results', 'milp_results','ilp_results','flow_lp_results', 
    'flow_tuple_linearization_lp_results','flow_witness_linearization_lp_results']
res_lines = ['lp_results','milp_results','ilp_results','ilp_results_10','flow_lp_results', 'flow_tuple_linearization_lp_results',
     'flow_witness_linearization_lp_results', 'lp_results: approximation'
    ]

def plot_resilience_expt(case_no, EXPT_DATA_FILE = 'data/synthetic_expt/expt-data-case-{}.csv', PLOT_OUTPUT_FILE = 'data/synthetic_expt/plots/expt-data-case-{}.pdf', expt_type="Resilience", BUCKET_SIZE_DENOMINATOR = 4, DATA_ALPHA = 0.1, xmax = 1e4, xmin = 1,g00_ymax = 1e3, g01_ymax = 1e5, g10_ymax= 1e5, g11_ymax = 4, hide_top_plots = False, hide_bottom_plots = False, plot_legend = True, g00_ymin = 1e-2, g00_arrow_point = None):
    """
    Generate and save a plot from the data available for a synthetic expt case

    Args:
        case_no (int): Experiment case number
        BUCKET_SIZE_DENOMINATOR(int): the size of buckets from which we plot median. Size 4 implies that buckets are of size 10^(1/4)
        DATA_ALPHA (float): alpha value of all points that are not the median
    """

    # Read the data
    expt_data = pd.read_csv(EXPT_DATA_FILE.format(case_no))

    # Pre-process: rename column
    if expt_type == "Resilience":
        expt_data['lp_results: approximation: Resilience'] = expt_data['lp_results: resilience lp approximation']
    # Accentuate data with deltas:
    for expt in timing_lines:
        if expt+': Solve Time' in expt_data.columns:
            expt_data[expt+': Solve Time'+': Delta'] = expt_data[expt+': Solve Time']/expt_data['lp_results: Solve Time']
    for expt in res_lines:
        if expt+': '+expt_type in expt_data.columns:
            expt_data[expt+': '+expt_type+': Delta'] = expt_data[expt+': '+expt_type]/expt_data['ilp_results: '+expt_type]
    
    fig, axes = plt.subplots(1,2, figsize=(9,4))
    plt.subplots_adjust(wspace=-1, hspace=-1)

    # Add line for linear scalability
    linear_delta = 0.9999*2
    linear_x = np.linspace(2,1e9,2)
    linear_y = linear_x - linear_delta 
    axes[0].plot(linear_x, linear_y, linestyle='dashed',color='black')

    # Plot 1: Timing - Actual Values
    for expt in timing_lines:
        if expt+': Solve Time' in expt_data.columns:
            axes[0].scatter(expt_data['ilp_results: number of witnesses'], expt_data[expt+': Solve Time'], marker = expt_markers[expt], color = lighten_color(expt_colors[expt]), alpha = DATA_ALPHA )
    

    # Plot 2: RES - Actual Values
    for expt in res_lines:
        if expt+': '+expt_type in expt_data.columns:
            axes[1].scatter(expt_data['ilp_results: number of witnesses'], expt_data[expt+': '+expt_type], marker = expt_markers[expt], color = lighten_color(expt_colors[expt]), alpha = DATA_ALPHA )

    # Plot median points
    
    # Bucket and find the median of values
    labels = [(10**(1/BUCKET_SIZE_DENOMINATOR))**i for i in range(100)]
    bins = [0]+[(labels[i]+labels[i+1])/2 for i in range(len(labels)-1)]+[10**math.ceil(math.log(labels[-1],10))]
    expt_data['binned_witnesses'] = pd.cut(expt_data['ilp_results: number of witnesses'], bins=bins, labels= labels)
    expt_data_bin = pd.DataFrame()
    for col in expt_data.columns:
        if is_numeric_dtype(expt_data[col]):
            expt_data_bin[col] = expt_data.groupby(['binned_witnesses'], observed=False)[col].agg('median').values
    expt_data_bin['ilp_results: number of witnesses'] = labels

    for expt in timing_lines:
        if expt+': Solve Time' in expt_data_bin.columns:
            axes[0].plot(expt_data_bin['ilp_results: number of witnesses'], expt_data_bin[expt+': Solve Time'], label = expt_labels[expt], marker = expt_markers[expt], color = expt_colors[expt], markerfacecolor='none')
    # Plot 2: RES - Actual Values
    for expt in res_lines:
        if expt+': '+expt_type in expt_data.columns:
            axes[1].plot(expt_data_bin['ilp_results: number of witnesses'], expt_data_bin[expt+': '+expt_type], label = expt_labels[expt], marker = expt_markers[expt], color = expt_colors[expt], markerfacecolor='none')
    # plot_title = expt_data['query'][0]
    # if 'domain size' in expt_data.columns:
    #     plot_title += ', domain size='+str(expt_data['domain size'][0])
    # if 'resp table' in expt_data.columns:
    #     plot_title += ', resp table='+str(expt_data['resp table'][0])
    # if expt_data['bag semantics'][0]:
    #     plot_title += ', max bag size='+str(expt_data['max bag size'][0])
    # fig.suptitle(plot_title)

    # Draw an arrow between last median points
    # axes[0].arrow(expt_data_bin['ilp_results: number of witnesses'].iloc[13], 10, 0, 1e2, head_width= 1e6, head_length = 2*1e1, shape ='full')

    xMinorLocator = LogLocator(base=10, subs=[0.1 * n for n in range(1, 10)], numticks = 40)   
    yMinorLocator = LogLocator(base=10, subs=[0.1 * n for n in range(1, 10)], numticks = 40)   
    for i in [0,1]:
        axes[i].set_xscale('log')
        axes[i].set_yscale('log')
        axes[i].xaxis.set_minor_locator(xMinorLocator)
        axes[i].yaxis.set_minor_locator(yMinorLocator)
        axes[i].grid(True, which='both', axis='both', alpha=0.05, linestyle='-',linewidth=1, zorder=1)  # linestyle='dashed', which='minor', axis='y',
        axes[i].set_xticks([10**i for i in range(int(math.log(xmax,10)))])
        axes[i].set_xlim(xmax=xmax)    
        axes[i].set_xlim(xmin=xmin)    


    axes[0].set_ylim(ymin=g00_ymin)    
    axes[0].set_ylim(ymax=g00_ymax)    
    axes[1].set_ylim(ymin=1)    
    axes[1].set_ylim(ymax=g01_ymax) 

    axes[0].set_ylabel('Solve Time')
    axes[1].set_ylabel(expt_type)
    axes[0].set_xlabel('Number of witnesses')
    axes[1].set_xlabel('Number of witnesses')
    

    handles, labels = axes[1].get_legend_handles_labels()
    if plot_legend:
        axes[1].legend(handles, labels, loc= 'lower right',
                            handlelength=1.5,
                            labelspacing=0,             # distance between label entries
                            handletextpad=0.3,          # distance between label and the line representation
                            borderaxespad=0.1,        # distance between legend and the outer axes
                            borderpad=0.1,                # padding inside legend box
                            numpoints=1,)
        
        handles, labels = axes[0].get_legend_handles_labels()
        axes[0].legend(handles, labels, loc= 'upper left',
                            handlelength=1.5,
                            labelspacing=0,             # distance between label entries
                            handletextpad=0.3,          # distance between label and the line representation
                            borderaxespad=0.1,        # distance between legend and the outer axes
                            borderpad=0.1,                # padding inside legend box
                            numpoints=1,)
    fig.tight_layout()
    
    if g00_arrow_point is not None:
        if 'flow_lp_results'+': Solve Time' in expt_data_bin.columns:
            expt1 = 'lp_results'
            expt2 = 'flow_lp_results'
        if 'flow_witness_linearization_lp_results'+': Solve Time' in expt_data_bin.columns:
            expt1 = 'ilp_results'
            expt2 = 'flow_witness_linearization_lp_results'
    
        median_x = expt_data_bin['ilp_results: number of witnesses'].iloc[g00_arrow_point]
        median_ymin = expt_data_bin[expt1+': Solve Time'].iloc[g00_arrow_point]
        median_ymax = expt_data_bin[expt2+': Solve Time'].iloc[g00_arrow_point]
        median_ymid = math.sqrt(median_ymax*median_ymin)
        axes[0].annotate("", xy=(median_x, median_ymin), 
                        xytext=(median_x, median_ymax), 
                        arrowprops=dict(arrowstyle="<->"))
        axes[0].annotate(str(round(median_ymax / median_ymin, 1))+'x', 
                        xy=(median_x, median_ymin), 
                        xytext=(median_x*1.1, median_ymid), 
                        )
    if PLOT_OUTPUT_FILE == None:
        plt.show()
    else:
        print('Saving plot to '+PLOT_OUTPUT_FILE.format(case_no))
        plt.savefig(PLOT_OUTPUT_FILE.format(case_no), bbox_inches="tight")
        # allows to automatically show the PDF. Can be commented out if it gets too annoying
        # Does not work on Windows
        # os.system("open " + PLOT_OUTPUT_FILE.format(case_no))            


def plot_resilience_expt_with_deltas(case_no, EXPT_DATA_FILE = 'data/synthetic_expt/expt-data-case-{}.csv', PLOT_OUTPUT_FILE = 'data/synthetic_expt/plots/expt-data-case-{}.pdf', expt_type="Resilience", BUCKET_SIZE_DENOMINATOR = 4, DATA_ALPHA = 0.1, xmin = 0, xmax = 1e4, g00_ymax = 1e3, g01_ymax = 1e5, g10_ymax= 1e5, g11_ymax = 4, g11_ymin = 0.1, hide_top_plots = False, hide_bottom_plots = False, g00_arrow_point = None, g11_arrow_points = None):
    """
    Generate and save a plot from the data available for a synthetic expt case

    Args:
        case_no (int): Experiment case number
        BUCKET_SIZE_DENOMINATOR(int): the size of buckets from which we plot median. Size 4 implies that buckets are of size 10^(1/4)
        DATA_ALPHA (float): alpha value of all points that are not the median
    """

    # Read the data
    expt_data = pd.read_csv(EXPT_DATA_FILE.format(case_no))

    # Pre-process: rename column
    if expt_type == "Resilience":
        expt_data['lp_results: approximation: Resilience'] = expt_data['lp_results: resilience lp approximation']
    # Accentuate data with deltas:
    for expt in timing_lines:
        if expt+': Solve Time' in expt_data.columns:
            expt_data[expt+': Solve Time'+': Delta'] = expt_data[expt+': Solve Time']/expt_data['lp_results: Solve Time']
    for expt in res_lines:
        if expt+': '+expt_type in expt_data.columns:
            expt_data[expt+': '+expt_type+': Delta'] = expt_data[expt+': '+expt_type]/expt_data['ilp_results: '+expt_type]
    
    fig, axes = plt.subplots(2, 2, figsize=(5*2,4*2))


    # Add line for linear scalability
    linear_delta = 0.99*2
    linear_x = np.linspace(2,1e9,2)
    linear_y = linear_x - linear_delta 
    axes[0][0].plot(linear_x, linear_y, linestyle='dashed',color='black')

    # Plot 1: Timing - Actual Values
    for expt in timing_lines:
        if expt+': Solve Time' in expt_data.columns:
            axes[0][0].scatter(expt_data['ilp_results: number of witnesses'], expt_data[expt+': Solve Time'], marker = expt_markers[expt], color = lighten_color(expt_colors[expt]), alpha = DATA_ALPHA )
    # Plot 2: RES - Actual Values
    for expt in res_lines:
        if expt+': '+expt_type in expt_data.columns:
            axes[0][1].scatter(expt_data['ilp_results: number of witnesses'], expt_data[expt+': '+expt_type], marker = expt_markers[expt], color = lighten_color(expt_colors[expt]), alpha = DATA_ALPHA )

    if not hide_bottom_plots:
        # Plot 3: Timing - Relative Values
        for expt in timing_lines:
            if expt+': Solve Time' in expt_data.columns and expt != 'lp_results':
                axes[1][0].scatter(expt_data['ilp_results: number of witnesses'], expt_data[expt+': Solve Time: Delta'], marker = expt_markers[expt], color = lighten_color(expt_colors[expt]), alpha = DATA_ALPHA )
        # Plot 4: RES - Relative Values 
        for expt in res_lines:
            if expt+': '+expt_type in expt_data.columns and expt != 'ilp_results':
                axes[1][1].scatter(expt_data['ilp_results: number of witnesses'], expt_data[expt+': '+expt_type+': Delta'], marker = expt_markers[expt], color = lighten_color(expt_colors[expt]), alpha = DATA_ALPHA)


    # Plot median points
    
    # Bucket and find the median of values
    labels = [(10**(1/BUCKET_SIZE_DENOMINATOR))**i for i in range(100)]
    bins = [0]+[(labels[i]+labels[i+1])/2 for i in range(len(labels)-1)]+[10**math.ceil(math.log(labels[-1],10))]
    expt_data['binned_witnesses'] = pd.cut(expt_data['ilp_results: number of witnesses'], bins=bins, labels= labels)
    expt_data_bin = pd.DataFrame()
    for col in expt_data.columns:
        if is_numeric_dtype(expt_data[col]):
            expt_data_bin[col] = expt_data.groupby(['binned_witnesses'], observed = False)[col].agg('median').values
    expt_data_bin['ilp_results: number of witnesses'] = labels

    for expt in timing_lines:
        if expt+': Solve Time' in expt_data_bin.columns:
            axes[0][0].plot(expt_data_bin['ilp_results: number of witnesses'], expt_data_bin[expt+': Solve Time'], label = expt_labels[expt], marker = expt_markers[expt], color = expt_colors[expt], markerfacecolor='none')
    # Plot 2: RES - Actual Values
    for expt in res_lines:
        if expt+': '+expt_type in expt_data.columns:
            axes[0][1].plot(expt_data_bin['ilp_results: number of witnesses'], expt_data_bin[expt+': '+expt_type], label = expt_labels[expt], marker = expt_markers[expt], color = expt_colors[expt], markerfacecolor='none')
    if not hide_bottom_plots:
        # Plot 3: Timing - Relative Values
        axes[1][0].axhline(y = 1, marker = expt_markers['lp_results'], color = expt_colors['lp_results'],)
        for expt in timing_lines:
            if expt+': Solve Time' in expt_data_bin.columns and expt != 'lp_results':
                axes[1][0].plot(expt_data_bin['ilp_results: number of witnesses'], expt_data_bin[expt+': Solve Time: Delta'], label = expt_labels[expt], marker = expt_markers[expt], color = expt_colors[expt], markerfacecolor='none')
        # Plot 4: RES - Relative Values
        for expt in res_lines:
            if expt+': '+expt_type in expt_data.columns and expt != 'ilp_results':
                axes[1][1].plot(expt_data_bin['ilp_results: number of witnesses'], expt_data_bin[expt+': '+expt_type+': Delta'], label = expt_labels[expt], marker = expt_markers[expt], color = expt_colors[expt], markerfacecolor='none')

    # plot_title = expt_data['query'][0]
    # if 'domain size' in expt_data.columns:
    #     plot_title += ', domain size='+str(expt_data['domain size'][0])
    # if 'resp table' in expt_data.columns:
    #     plot_title += ', resp table='+str(expt_data['resp table'][0])
    # if expt_data['bag semantics'][0]:
    #     plot_title += ', max bag size='+str(expt_data['max bag size'][0])
    # fig.suptitle(plot_title)

    xMinorLocator = LogLocator(base=10, subs=[0.1 * n for n in range(1, 10)], numticks = 40)   
    yMinorLocator = LogLocator(base=10, subs=[0.1 * n for n in range(1, 10)], numticks = 40)   
    for i,j in [[0,0],[0,1],[1,0]]:
        axes[i][j].set_xscale('log')
        axes[i][j].set_yscale('log')
        axes[i][j].xaxis.set_minor_locator(xMinorLocator)
        axes[i][j].yaxis.set_minor_locator(yMinorLocator)
        axes[i][j].grid(True, which='both', axis='both', alpha=0.05, linestyle='-',linewidth=1, zorder=1)  # linestyle='dashed', which='minor', axis='y',
        axes[i][j].set_xticks([10**i for i in range(int(math.log(xmax,10)))])
        axes[i][j].set_xlim(xmax=xmax)    
        axes[i][j].set_xlim(xmin=xmin)    

    axes[1][1].set_xscale('log')
    axes[1][1].xaxis.set_minor_locator(xMinorLocator)
    axes[1][1].set_xticks([10**i for i in range(int(math.log(xmax,10)))])
    axes[1][1].set_xlim(xmax=xmax)    
    axes[1][1].set_xlim(xmin=xmin)    
    axes[1][1].grid(True, which='both', axis='both', alpha=0.05, linestyle='-',linewidth=1, zorder=1)  # linestyle='dashed', which='minor', axis='y',


    axes[0][0].set_ylim(ymin=1e-2)    
    axes[0][0].set_ylim(ymax=g00_ymax)    
    axes[0][1].set_ylim(ymin=1)    
    axes[0][1].set_ylim(ymax=g01_ymax)    
    axes[1][0].set_ylim(ymax=g10_ymax)    
    
    axes[1][1].set_ylim(ymin=g11_ymin)    
    axes[1][1].set_ylim(ymax=g11_ymax)    

    axes[0][0].set_ylabel('Solve Time')
    axes[0][1].set_ylabel(expt_type)
    axes[1][0].set_ylabel('Δ Solve Time')
    axes[1][1].set_ylabel('Δ'+expt_type)
    axes[1][0].set_xlabel('Number of witnesses')
    axes[1][1].set_xlabel('Number of witnesses')

    

    handles, labels = axes[0][1].get_legend_handles_labels()
    axes[0][1].legend(handles, labels, loc= 'lower right',
                            handlelength=1.5,
                            labelspacing=0,             # distance between label entries
                            handletextpad=0.3,          # distance between label and the line representation
                            borderaxespad=0.1,        # distance between legend and the outer axes
                            borderpad=0.1,                # padding inside legend box
                            numpoints=1,)

    if g00_arrow_point is not None:  
        expt1 = 'lp_results'
        expt2 = 'ilp_results'
    
        median_x = expt_data_bin['ilp_results: number of witnesses'].iloc[g00_arrow_point]
        median_ymin = expt_data_bin[expt1+': Solve Time'].iloc[g00_arrow_point]
        median_ymax = expt_data_bin[expt2+': Solve Time'].iloc[g00_arrow_point]
        median_ymid = math.sqrt(median_ymax*median_ymin)
        axes[0][0].annotate("", xy=(median_x, median_ymin), 
                        xytext=(median_x, median_ymax), 
                        arrowprops=dict(arrowstyle="<->"))
        axes[0][0].annotate(str(round(median_ymax / median_ymin))+'x', 
                        xy=(median_x, median_ymin), 
                        xytext=(median_x*1.1, median_ymid), 
                        )
    
    if g11_arrow_points is not None:
        for (arrow_point, expt1, expt2) in g11_arrow_points:
            median_x = expt_data_bin['ilp_results: number of witnesses'].iloc[arrow_point]
            median_ymin = expt_data_bin[expt1+': '+expt_type+': Delta'].iloc[arrow_point]
            median_ymax = expt_data_bin[expt2+': '+expt_type+': Delta'].iloc[arrow_point]
            median_ymid = math.sqrt(median_ymax*median_ymin)
            axes[1][1].annotate("", xy=(median_x, median_ymin), 
                            xytext=(median_x, median_ymax), 
                            arrowprops=dict(arrowstyle="<->"))
            axes[1][1].annotate(str(round(median_ymax / median_ymin,1))+'x', 
                            xy=(median_x, median_ymin), 
                            xytext=(median_x*1.1, median_ymid), 
                            )

    fig.tight_layout()
    if PLOT_OUTPUT_FILE == None:
        plt.show()
    else:
        print('Saving plot to '+PLOT_OUTPUT_FILE.format(case_no))
        plt.savefig(PLOT_OUTPUT_FILE.format(case_no), bbox_inches="tight")
        # allows to automatically show the PDF. Can be commented out if it gets too annoying
        # Does not work on Windows
        # os.system("open " + PLOT_OUTPUT_FILE.format(case_no))            

def lighten_color(color, amount=0.3):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.
    
    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = np.array(colorsys.rgb_to_hls(*mc.to_rgb(c)))
    return colorsys.hls_to_rgb(c[0],1-amount * (1-c[1]),c[2])

if __name__ == '__main__':
    for i in range(31, 140):
        try:
            plot_resilience_expt(i)
        except:
            pass