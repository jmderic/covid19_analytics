#!/usr/bin/python3

# Note: this is the newer app preamble updated for python3
import os.path, sys, inspect
this_file = os.path.abspath(inspect.getsourcefile((lambda x:x)))
this_dir = os.path.dirname(this_file)
# jmd_python_dir = this_dir + '/..'
sys.path.append(this_dir)
# import test_startup
from argparse import ArgumentParser
# end: preamble

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#from matplotlib.ticker import ScalarFormatter

def compute_active(csv_file, death_delay, recover_delay):
    pd.set_option('display.width', 120)
    pd.set_option("display.max_rows", 999)
    # pd.set_option('display.max_colwidth', 10) # does not seem to work
    type_spec = { 'Confirmed' : np.int32, 'Deaths' : np.int32 }
    df1 = pd.read_csv(csv_file, parse_dates=['Date'], dtype=type_spec)
    #df1['Deaths'] = df1['Deaths'].astype(int)

    # add the DieLater and RecLater columns
    date_list = df1['Date'].tolist()
    df1['DieLater'] = 0
    df1['DieLater'] = df1['DieLater'].astype(int)
    for i,v in df1.iterrows():
        if v["Deaths"]:
            #print(f"idx {i} val {v}")
            dt1 = v['Date']
            dt2 = dt1 - pd.Timedelta(days=death_delay)
            if dt2 in date_list:
                # update value in existing row
                df1.at[df1.loc[df1['Date']==dt2].index, 'DieLater'] = v["Deaths"]
            else:
                # add row of zeros except positive value in 'DieLater'
                add_row_dict = { 'Date' : dt2, 'Confirmed' : 0, 'Deaths' : 0,
                                 'DieLater' : v["Deaths"] }
                df1 = df1.append(add_row_dict, ignore_index=True)

    df2 = df1.sort_values(by=['Date'])
    df2 = df2[['Date', 'Confirmed', 'Deaths', 'DieLater']]
    df2 = df2.reset_index(drop=True)
    df2['RecLater'] = df2['Confirmed'] - df2['DieLater']
    #df2['CumConf'] = df2.groupby('Date')['Confirmed'].transform(pd.Series.cumsum)
    end_date = df2['Date'].iat[-1]

    # add the recovered column
    date_list = df2['Date'].tolist()
    df2['Recovered'] = 0
    df2['Recovered'] = df2['Recovered'].astype(int)
    recovered_shortage = 0
    for i,v in df2.iterrows():
        recovered_net = recovered_shortage + v['RecLater']
        if recovered_net <= 0:
            recovered_shortage = recovered_net
            continue
        else:
            recovered_shortage = 0
            dt1 = v['Date']
            dt2 = dt1 + pd.Timedelta(days=recover_delay)
            if dt2 > end_date:
                break
            if dt2 in date_list:
                df2.at[df2.loc[df2['Date']==dt2].index, 'Recovered'] = recovered_net
            else:
                # add row of zeros except positive value in 'Recovered'
                add_row_dict = { 'Date' : dt2, 'Confirmed' : 0, 'Deaths' : 0,
                                 'DieLater' : 0,  'RecLater' : 0,
                                 'Recovered' : recovered_net }
                df2 = df2.append(add_row_dict, ignore_index=True)

    df3 = df2.sort_values(by=['Date'])
    df3 = df3.set_index('Date')
    df3 = df3[['Confirmed', 'Deaths', 'DieLater', 'RecLater', 'Recovered']]
    #df3 = df3.reset_index(drop=True)
    df3['Active'] = df3['Confirmed'] - df3['Deaths'] - df3['Recovered']
    # add the cumulative columns
    df3['CumConf'] = df3['Confirmed'].cumsum()
    df3['CumDeaths'] = df3['Deaths'].cumsum()
    df3['CumRec'] = df3['Recovered'].cumsum()
    df3['CumActive'] = df3['Active'].cumsum()
    print(df3)
    return df3

def plot_active(df1, Log10):
    # dataframe pruning
    unwanted_cols = ['Confirmed', 'Deaths', 'DieLater', 'RecLater',
                     'Recovered', 'Active']
    df1 = df1.drop(unwanted_cols, axis=1)
    if Log10:
        unwanted = df1[(df1['CumConf']==0) | (df1['CumDeaths']==0)
                       | (df1['CumRec']==0) | (df1['CumActive']==0)]
    else:
        unwanted = df1[(df1['CumConf']<=10) & (df1['CumDeaths']<=10)
                       & (df1['CumRec']<=10) & (df1['CumActive']<=10)]
    df1 = df1.drop(unwanted.index)
    print(df1)
    # do the plotting
    #plt.figure()
    plt.rcParams.update({'figure.autolayout' : True})
    df1.plot()
    plot_name_crumb='_linear'
    if Log10:
        plt.yscale('log')
        plot_name_crumb='_loglin'
        #plt.ticklabel_format(axis='y', style='plain')
        #fig, ax = plt.subplots()
        #ax.yaxis.set_major_formatter(ScalarFormatter())
    plt.legend(loc='best', labels=['Confirmed', 'Deaths', 'Recovered', 'Active'])
    plt.grid(which='both', axis='both')
    #plt.show()
    plt.savefig(f'plot{plot_name_crumb}.svg')
    plt.savefig(f'plot{plot_name_crumb}.png')

class FindActive:
    def __init__(self, cl_args):
        self.cl_args = cl_args
        self.csv_file = cl_args.csv_file
        self.death_delay = cl_args.death_delay
        self.recover_delay = cl_args.recover_delay
        self.log_plot = cl_args.log_plot

    def run(self):
        df = compute_active(self.csv_file, self.death_delay, self.recover_delay)
        plot_active(df, self.log_plot)

def call_runner(cl_args) :
    os.umask(0o002)
    impl = cl_args.run_class(cl_args)
    return impl.run()

if __name__ == '__main__':
    print(this_dir)
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    # parser for the start_idea subcommand
    p_start_idea = subparsers.add_parser('find_active')
    p_start_idea.set_defaults(run_class=FindActive)
    p_start_idea.add_argument('-d', '--death-delay',
                              help='Avg. days, symptomatic to death (default: 17)',
                              type=int, default=17)
    p_start_idea.add_argument('-r', '--recover-delay',
                              help='Avg. days, symptomatic to recovery (default: 14)',
                              type=int, default=14)
    p_start_idea.add_argument('-i', '--csv-file',
                              help='CSV input file', type=str, required=True)
    p_start_idea.add_argument('-l', '--log-plot',
                              help='Plot y axis as log', action='store_true')

    # generic subcommand execution call
    parsed_args = parser.parse_args()
    #print parsed_args
    exit(call_runner(parsed_args))
