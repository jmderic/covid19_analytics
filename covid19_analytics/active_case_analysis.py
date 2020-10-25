# -*- coding: utf-8 -*-
# Copyright J. Mark Deric, 2020.  All rights reserved

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from covid19_analytics import common
from pathlib import Path
import json, re

class ActiveCases:
    def __init__(self, file_stub, wrk_dir, recover_delay):
        self.wrk_dir = Path(wrk_dir).expanduser().resolve()
        self.file_stub = file_stub
        self.recover_delay = recover_delay
        self.disp_max_rows = pd.get_option("display.max_rows")
        print(f'Max Rows {self.disp_max_rows}')
        pd.set_option("display.min_rows", 40)
        self.location = None

    def set_location(self, loc):
        self.location = loc

    def create_active_plots(self, print_df=False):
        df = self.get_alldate_csv()
        df['MaxRec'] = df['CumCases'].shift(self.recover_delay,
                                            fill_value=0).astype('int32')
        df['CumRecovered'] = df['MaxRec'] - df['CumDeaths']
        # the above can generate negative CumRecovered values; following
        # fixes with a little fudge (adding 1) not to unduly delay the
        # first shown datapoint on the log graph
        df['CumRecovered'] = df['CumRecovered'].apply(lambda x: 1 if x <= 0
                                                      else x).astype('int32')
        df['CumActive'] = df['CumCases'] - df['MaxRec']
        data = ('Cases', 'Deaths', 'Recovered', 'Active', )
        add_daily_columns(df, data)
        if print_df:
            pd.set_option("display.max_rows", 999)
            print(df)
            print(df.info())
            pd.set_option("display.max_rows", self.disp_max_rows)
        df = prune_dates(df, data)
        if self.location:
            update_json(df, self.location, self.wrk_dir)
        plot_active(df, self.wrk_dir, self.file_stub, data)

    def create_daily_plots(self):
        df = self.get_alldate_csv()
        tau = 8; days = 7
        col_calcs = ( ExpMovAvg(tau), BkwrdAvg(days), )
        data = ('Cases', 'Deaths',)
        add_daily_columns(df, data)
        for datum in data:
            for calc in col_calcs:
                new_col = f'{calc.prefix}{datum}'
                df[new_col] = df[datum].apply(calc)
        df = prune_dates(df, data)
        if self.location:
            update_json(df, self.location, self.wrk_dir)
        for datum in data:
            plot_datum(df, self.wrk_dir, self.file_stub, datum, col_calcs)

    def get_alldate_csv(self):
        type_spec = { 'CumCases' : np.int32, 'CumDeaths' : np.int32 }
        csv_file = self.wrk_dir / f'{self.file_stub}.csv'
        df = pd.read_csv(csv_file, parse_dates=['Date'], index_col='Date',
                         dtype=type_spec)
        idx = pd.date_range(min(df.index), max(df.index))
        df = df.reindex(idx, fill_value=0)
        for col_name in type_spec:
            if not df[col_name].is_monotonic:
                print(f'Scrubbing column {col_name}; '+
                      'not monotonically increasing')
                fix_non_monotonic(df, col_name)
        return df

def prune_dates(df, data):
    # prune date when any cumulative is still zero
    if len(data) < 1:
        return df
    unwanted = df[f'Cum{data[0]}']==0
    for datum in data[1:]:
        unwanted = unwanted | (df[f'Cum{datum}']==0)
    df1 = df.drop(unwanted[unwanted].index)
    print(df1)
    print(df1.info())
    return df1

def add_daily_columns(df, data):
    for datum in data:
        cum_name = f'Cum{datum}'
        df[datum] = df[cum_name].diff()
        df.loc[df.index[0], datum] = df[cum_name][0]
        df[datum] = df[datum].astype('int32')

class ExpMovAvg:
    """tau is the time constant for the first order filter.  For the
    analog system in response to a 100% step change in the input, the
    output will go to 63.% in one time constant; 86.5 in 2 tau; 95.0%
    in 3 tau; 99.8% in 6 tau.  FIXME: The discrete time system appears
    to yield slightly lower values.
    """
    def __init__(self, tau_periods):
        tau_int = int(tau_periods) if tau_periods >= 1 else 1
        self.alpha = 1 / (tau_int + 1)
        self.avg = None
        self.prefix = f'Ema{tau_int}'
        self.label = f'Exp. Moving Avg. (EMA); τ = {tau_int} days'

    def __call__(self, value):
        if self.avg == None:
            self.avg = value
            return value
        self.avg = self.alpha * value + (1 - self.alpha) * self.avg
        return self.avg

class BkwrdAvg:
    """Average of backward looking N periods
    """
    def __init__(self, periods):
        per_int = int(periods) if periods >= 1 else 1
        self.periods = per_int
        self.window = np.ndarray(0, dtype=np.int32) # int32 array, no values
        self.prefix = f'Abk{per_int}'
        self.label = f'{per_int}-day Moving Avg'

    def __call__(self, value):
        if self.window.size == self.periods:
            self.window = self.window[1:]
        self.window = np.append(self.window, value)
        return self.window.mean()

def plot_active(df, output_dir, file_stub, data):
    df1 = df[[f'Cum{x}' for x in data]]
    fig, axs = plt.subplots(2, 1, sharex='col', figsize=(8,10))
    for ax in axs:
        ax.plot(df1.index, df1.values)
        ax.grid(which='both', axis='both')
    axs[0].set_title('Cumulative Totals')
    axs[0].legend(loc='best', labels=data)
    axs[1].set_yscale('log')
    axs[1].xaxis.set_major_locator(mdates.MonthLocator())
    #every other Monday
    min_loc = mdates.WeekdayLocator(mdates.MO, interval=2)
    axs[1].xaxis.set_minor_locator(min_loc)
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('\n%b'))
    axs[1].xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    plt.subplots_adjust(hspace=0, bottom=.10, top=.92)
    fig.savefig(output_dir / f'{file_stub}_Active.svg')

def plot_datum(df, output_dir, file_stub, datum, col_calcs):
    fig, ax = plt.subplots(figsize=(11,8))
    xs = df.index.values
    print(f'x-axis type {type(xs)} element type {type(xs[0])}')
    ys = df[datum].values
    ax.bar(xs, ys)
    label_list = []
    colors = ('r', 'k',)
    for i, calc in enumerate(col_calcs):
        new_col = f'{calc.prefix}{datum}'
        ys = df[new_col].values
        ax.plot(xs, ys, colors[i])
        label_list.append(calc.label)
    label_list.append(datum)
    ax.grid(which='both', axis='both')
    ax.set_title(f'Daily {datum}')
    ax.legend(loc='best', labels=label_list)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    #every other Monday
    min_loc = mdates.WeekdayLocator(mdates.MO, interval=2)
    ax.xaxis.set_minor_locator(min_loc)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('\n%b'))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    plt.subplots_adjust(bottom=.10, top=.92)
    fig.savefig(output_dir / f'{file_stub}_{datum}.svg')

def fix_non_monotonic(df, col_name):
    max = df[col_name][-1]
    for idx in df.index.values[::-1]:
        test_val = df.loc[idx, col_name]
        if test_val > max:
            print(f'Adjust {test_val} to {max} at {np.datetime64(idx, "D")}')
            df.loc[idx, col_name] = max
        max = df.loc[idx, col_name]

def update_json(df, location, wrk_dir):
    # open json file
    with open(wrk_dir / 'state.json') as f:
        state = json.load(f)
    json_file = wrk_dir / f'{state["timestamp"]}_state.json'
    with open(json_file) as f:
        state = json.load(f)
    # JMD_TODO: combine next 3 lines
    last_row = df.iloc[-1:]
    date_last_row = last_row.index[0]
    asof_date = date_last_row.strftime("%b %d")
    if 'asof_date' not in state:
        state['asof_date'] = asof_date
        state['asof_long'] = date_last_row.strftime("%m/%d/%y")
    else:
        if state['asof_date'] != asof_date:
            m = f'asof_date mismatch: new {asof_date} != {state["asof_date"]}'
            raise Exception(m)
    if 'data' not in state["locations"][location]:
        state["locations"][location]['data'] = {}
    loc_data = state["locations"][location]['data']
    if 'CumActive' in df.columns:
        update_active_data(df, loc_data)
    else:
        update_daily_data(df, loc_data)
    # save json file
    with open(json_file, 'w') as f:
        json.dump(state, f, sort_keys=True, indent=4)

def update_active_data(df, loc_data):
    last_row = df.iloc[-1:]
    print(f'last_row:\n{last_row}')
    date_last_row = last_row.index[0]
    print(f'date_last_row: {date_last_row}\n'
          f'type(date_last_row): {type(date_last_row)}\n'
          f'str: {date_last_row.strftime("%m/%d/%y")}')
    date_peak = df["CumActive"].idxmax()
    print(f'date_peak:\n{date_peak}')
    val_peak = df.loc[date_peak, 'CumActive']
    x = 'val_peak'
    tx = f'type({x})'
    print(f'{x}:\n{eval(x)}\ntype {eval(tx)}')
    x = 'last_row.CumCases'
    tx = f'type({x})'
    print(f'{x}:\n{eval(x)}\ntype {eval(tx)}')
    x = 'last_row["CumCases"]'
    tx = f'type({x})'
    print(f'{x}:\n{eval(x)}\ntype {eval(tx)}')
    d = {
        'case_tot' : int(last_row["CumCases"].iloc[0]),
        'death_tot' : int(last_row["CumDeaths"].iloc[0]),
        'active_now' : int(last_row["CumActive"].iloc[0]),
        'active_peak' : {
            'val' : int(val_peak),
            'date' : date_peak.strftime("%m/%d/%y"),
        },
    }
    print(d)
    loc_data.update(d)

def update_daily_data(df, loc_data):
    last_row = df.iloc[-1:]
    print(f'last_row:\n{last_row}')
    x = 'list(df.columns)'
    tx = f'type({x})'
    print(f'{x}:\n{eval(x)}\ntype {eval(tx)}')
    cols = list(df.columns)
    p = re.compile(r'^(Cum|Ema|Abk)*(\d+)*(Case|Death)s')
    for col in cols:
        print(col)
        m = p.match(col)
        if m.group(1) == 'Cum':
            continue
        if m.group(1) == None:
            base = f'{m.group(3).lower()}'
            param = None
        else:
            base = f'{m.group(3).lower()}_{m.group(1).lower()}'
            param = int(m.group(2))
        type_op = 'int'
        if param:
            type_op = 'float'
            loc_data[f'{base}_param'] = param
        now_name = f'{base}_now'
        now_arg = 'last_row[col].iloc[0]'
        loc_data[now_name] = eval(f'{type_op}({now_arg})')
        peak_name = f'{base}_peak'
        date_peak = df[col].idxmax()
        print(f'date_peak:\n{date_peak}')
        val_peak = df.loc[date_peak, col]
        print(f'val_peak:\n{val_peak}')
        loc_data[peak_name] = {
            'val' : eval(f'{type_op}({val_peak})'),
            'date' : date_peak.strftime("%m/%d/%y"),
        }
