# Copyright J. Mark Deric, 2020.  All rights reserved

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import common

#from matplotlib.ticker import ScalarFormatter

class ActiveCases:
    def __init__(self, csv_filename, wrk_dir, recover_delay):
        tup = common.get_wrkcsv_paths(csv_filename, wrk_dir)
        self.wrk_dir, self.csv_file = tup
        self.recover_delay = recover_delay

        print(f'Max Rows {pd.get_option("display.max_rows")}')
        pd.set_option("display.min_rows", 40)

        self.type_spec = { 'Cases' : np.int32, 'Deaths' : np.int32 }

    def create_active_plots(self):
        df = self.get_active_df()
        # 2nd arg: log-lin plot, True; lin-lin plot, False
        plot_active(df, self.wrk_dir, False)
        plot_active(df, self.wrk_dir, True)

    def get_active_df(self):
        df = self.get_alldate_csv(self.csv_file)
        df['MaxRec'] = df['CumCases'].shift(self.recover_delay,
                                            fill_value=0).astype('int32')
        df['CumRec'] = df['MaxRec'] - df['CumDeaths']
        df['CumActive'] = df['CumCases'] - df['MaxRec']
        data = ('Cases', 'Deaths', 'Rec', 'Active', )
        for datum in data:
            add_daily_col(df, datum)
        print(df)
        print(df.info())
        return df

    def get_alldate_csv(self, csv_file):
        type_spec = { 'CumCases' : np.int32, 'CumDeaths' : np.int32 }
        df = pd.read_csv(self.csv_file, parse_dates=['Date'], index_col='Date',
                         dtype=type_spec)
        idx = pd.date_range(min(df.index), max(df.index))
        df = df.reindex(idx, fill_value=0)
        #print(df)
        #print(df.info())
        return df

def add_daily_col(df, datum):
    cum_name = f'Cum{datum}'
    df[datum] = df[cum_name].diff()
    #df[datum][0] = df[cum_name][0]
    # view vs copy; above changed to below; detail in commit 6a69792e0
    row_index = df.index[0]
    df.loc[row_index, datum] = df[cum_name][0]
    # end: view vs copy
    df[datum] = df[datum].astype('int32')

def plot_active(df, output_dir, Log10):
    # dataframe pruning
    #unwanted_cols = ['MaxRec', 'Cases', 'Deaths', 'Rec', 'Active',]
    #df1 = df.drop(unwanted_cols, axis=1)
    df1 = df[['CumCases', 'CumDeaths', 'CumRec', 'CumActive',]]
    if True : # was Log10
        unwanted = df1[(df1['CumCases']==0) | (df1['CumDeaths']==0)
                       | (df1['CumRec']==0) | (df1['CumActive']==0)]
    else: 
        unwanted = df1[(df1['CumCases']<=10) & (df1['CumDeaths']<=10)
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
    plt.legend(loc='best', labels=['Cases', 'Deaths', 'Recovered', 'Active'])
    plt.grid(which='both', axis='both')
    #plt.show()
    plt.savefig(output_dir / f'plot{plot_name_crumb}.svg')
    plt.savefig(output_dir / f'plot{plot_name_crumb}.png')
