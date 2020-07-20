# Copyright J. Mark Deric, 2020.  All rights reserved

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#from matplotlib.ticker import ScalarFormatter
from covid19_analytics import common

class ActiveCases:
    def __init__(self, csv_filename, wrk_dir, recover_delay):
        tup = common.get_wrkcsv_paths(csv_filename, wrk_dir)
        self.wrk_dir, self.csv_file = tup
        self.recover_delay = recover_delay

        self.disp_max_rows = pd.get_option("display.max_rows")
        print(f'Max Rows {self.disp_max_rows}')
        pd.set_option("display.min_rows", 40)

        self.type_spec = { 'Cases' : np.int32, 'Deaths' : np.int32 }

    def create_active_plots(self):
        df = self.get_active_df()
        df = prune_dates(df)
        plot_active(df, self.wrk_dir)

    def create_daily_plots(self):
        df = self.get_active_df()
        tau = 9
        data = ('Deaths', 'Cases',)
        for datum in data:
            add_smoothed_col(df, datum, tau)
        df = prune_dates(df)
        for datum in data:
            plot_datum(df, self.wrk_dir, datum)

    def get_active_df(self, print_df=False):
        df = self.get_alldate_csv(self.csv_file)
        df['MaxRec'] = df['CumCases'].shift(self.recover_delay,
                                            fill_value=0).astype('int32')
        df['CumRec'] = df['MaxRec'] - df['CumDeaths']
        # the above can generate negative CumRec values; following
        # fixes with a little fudge (adding 1) not to unduly delay the
        # first shown datapoint on the log graph
        df['CumRec'] = df['CumRec'].apply(lambda x: 1 if x <= 0 else x)
        df['CumActive'] = df['CumCases'] - df['MaxRec']
        data = ('Cases', 'Deaths', 'Rec', 'Active', )
        for datum in data:
            add_daily_col(df, datum)
        if print_df:
            pd.set_option("display.max_rows", 999)
            print(df)
            print(df.info())
            pd.set_option("display.max_rows", self.disp_max_rows)
        return df

    def get_alldate_csv(self, csv_file):
        type_spec = { 'CumCases' : np.int32, 'CumDeaths' : np.int32 }
        df = pd.read_csv(self.csv_file, parse_dates=['Date'], index_col='Date',
                         dtype=type_spec)
        idx = pd.date_range(min(df.index), max(df.index))
        df = df.reindex(idx, fill_value=0)
        return df

def prune_dates(df):
    if True : # was Log10
        unwanted = df[(df['CumCases']==0) | (df['CumDeaths']==0)
                       | (df['CumRec']==0) | (df['CumActive']==0)]
    else: 
        unwanted = df[(df['CumCases']<=10) & (df['CumDeaths']<=10)
                       & (df['CumRec']<=10) & (df['CumActive']<=10)]
    df1 = df.drop(unwanted.index)
    print(df1)
    print(df1.info())
    return df1

def add_daily_col(df, datum):
    cum_name = f'Cum{datum}'
    df[datum] = df[cum_name].diff()
    #df[datum][0] = df[cum_name][0]
    # view vs copy; above changed to below; detail in commit 6a69792e0
    row_index = df.index[0]
    df.loc[row_index, datum] = df[cum_name][0]
    # end: view vs copy
    df[datum] = df[datum].astype('int32')

class Smoother:
    def __init__(self, tau_periods):
        self.alpha = 1 / (tau_periods + 1)
        self.smoothed = None

    def __call__(self, value):
        if self.smoothed == None:
            self.smoothed = value
            return value
        self.smoothed = self.alpha * value + (1 - self.alpha) * self.smoothed
        return self.smoothed

def add_smoothed_col(df, datum, tau_periods):
    """tau is the time constant for the first order filter.  For the
    analog systemn in response to a 100% step change in the input, the
    output will go to 63.% in one time constant; 86.5 in 2 tau; 95.0%
    in 3 tau; 99.8% in 6 tau.  The discrete time system appears to
    yield slightly lower values.
    """
    sm_name = f'Sm{datum}'
    sm = Smoother(tau_periods)
    df[sm_name] = df[datum].apply(sm)

def plot_active(df, output_dir):
    df1 = df[['CumCases', 'CumDeaths', 'CumRec', 'CumActive',]]
    # do the plotting
    fig, axs = plt.subplots(2, 1, sharex='col', figsize=(8,10))
    for ax in axs:
        ax.plot(df1.index, df1.values)
        ax.grid(which='both', axis='both')
    axs[0].set_title('Wuhan Coronavirus\nCumulative Totals')
    axs[0].legend(loc='best', labels=['Cases', 'Deaths', 'Recovered', 'Active'])
    axs[1].set_yscale('log')
    axs[1].xaxis.set_major_locator(mdates.MonthLocator())
    axs[1].xaxis.set_minor_locator(mdates.WeekdayLocator(0)) # 0, Monday
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('\n%b'))
    axs[1].xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    plt.subplots_adjust(hspace=0, bottom=.10, top=.92)
    fig.savefig(output_dir / f'plot_both.svg')

def plot_datum(df, output_dir, datum):
    sm_name = f'Sm{datum}'
    df1 = df[[datum, sm_name,]]
    #fig = plt.figure()
    #ax = fig.gca()
    fig, ax = plt.subplots()
    xs = df1.index.values
    print(f'x-axis type {type(xs)} element type {type(xs[0])}')
    ys_sm = df1[sm_name].values
    ys = df1[datum].values
    ax.bar(xs, ys)
    ax.plot(xs, ys_sm, 'r')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(0)) # 0, Monday
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.grid(which='both', axis='x')
    ax.legend(loc='best', labels=['10 day tau', datum])
    ax.grid(which='both', axis='y')
    plt.subplots_adjust(bottom=.10, top=.92)
    fig.savefig(output_dir / f'plot_{datum}.svg')
