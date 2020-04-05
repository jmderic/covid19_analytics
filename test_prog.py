#!/usr/bin/python3

# Note: this is the newer app preamble
import os.path, sys

# following not python3 friendly: AttributeError: 'function' object has no attribute 'func_code'
#this_dir = os.path.dirname((lambda x:x).func_code.co_filename)
# jmd_python_dir = this_dir + '/..'
#sys.path.append(this_dir)
# import test_startup
from argparse import ArgumentParser
# end: preamble

import pandas as pd
import numpy as np

def test_func(csv_file, death_delay, recover_delay):
    pd.set_option('display.width', 120)
    # pd.set_option('display.max_colwidth', 10) # does not seem to work
    type_spec = { 'Confirmed' : np.int32, 'Deaths' : np.int32 }
    df1 = pd.read_csv(csv_file, parse_dates=['Date'], dtype=type_spec)
    #df2 = df.drop([df.index[0]])
    #df1['Date'] = df1['Date'].astype(Timestamp)
    #df1['Deaths'] = df1['Deaths'].astype(int)
    #df1['Confirmed'] = df1['Confirmed'].astype(int)
    #df1 = df2.drop(['Cum C', 'Cum D'], axis=1)
    date_list = df1['Date'].tolist()
    #print(date_list)
    df1['DieLater'] = 0
    df1['DieLater'] = df1['DieLater'].astype(int)
    #print(df1)
    for i,v in df1.iterrows():
        if v["Deaths"]:
            #print(f"idx {i} val {v}")
            #dt = df1.loc[df1.index==i].index.values[0] ... also iloc
            dt1 = v['Date']
            dt2 = dt1 - pd.Timedelta(days=death_delay)
            #print(dt2)
            if dt2 in date_list:
                df1.at[df1.loc[df1['Date']==dt2].index, 'DieLater'] = v["Deaths"]
            else:
                # add row of zeros except positive value in 'DieLater'
                add_row_dict = { 'Date' : dt2, 'Confirmed' : 0, 'Deaths' : 0,
                                 'DieLater' : v["Deaths"] }
                df1 = df1.append(add_row_dict, ignore_index=True)

    #print(df1)
    df2 = df1.sort_values(by=['Date'])
    df2 = df2[['Date', 'Confirmed', 'Deaths', 'DieLater']]
    df2 = df2.reset_index(drop=True)
    #df2['CumConf'] = df2['Confirmed'].cumsum()
    df2['RecLater'] = df2['Confirmed'] - df2['DieLater']
    #df2['CumDieLater'] = df2['DieLater'].cumsum()
    #df2['CumConf'] = df2.groupby('Date')['Confirmed'].transform(pd.Series.cumsum)
    #df2['PotRec'] = df2['CumConf'] - df2['CumDieLater']
    #print(df2['Date'].iat[-1])
    end_date = df2['Date'].iat[-1]
    #print(df2)

    date_list = df2['Date'].tolist()
    #print(date_list)
    df2['Recovered'] = 0
    df2['Recovered'] = df2['Recovered'].astype(int)
    #print(df2)
    recovered_shortage = 0
    for i,v in df2.iterrows():
        recovered_net = recovered_shortage + v['RecLater']
        if recovered_net <= 0:
            recovered_shortage = recovered_net
            continue
        else:
            recovered_shortage = 0
            #print(f"idx {i} val {v}")
            dt1 = v['Date']
            dt2 = dt1 + pd.Timedelta(days=recover_delay)
            if dt2 > end_date:
                break
            #print(dt2)
            if dt2 in date_list:
                df2.at[df2.loc[df2['Date']==dt2].index, 'Recovered'] = recovered_net
            else:
                # add row of zeros except positive value in 'Recovered'
                add_row_dict = { 'Date' : dt2, 'Confirmed' : 0, 'Deaths' : 0,
                                 'DieLater' : 0,  'RecLater' : 0,
                                 'Recovered' : recovered_net }
                df2 = df2.append(add_row_dict, ignore_index=True)

    df3 = df2.sort_values(by=['Date'])
    df3 = df3[['Date', 'Confirmed', 'Deaths', 'DieLater', 'RecLater', 'Recovered']]
    df3 = df3.reset_index(drop=True)
    df3['Active'] = df3['Confirmed'] - df3['Deaths'] - df3['Recovered']
    df3['CumConf'] = df3['Confirmed'].cumsum()
    df3['CumDeaths'] = df3['Deaths'].cumsum()
    df3['CumRec'] = df3['Recovered'].cumsum()
    df3['CumActive'] = df3['Active'].cumsum()
    print(repr(df3))

class FindActive:
    def __init__(self, cl_args):
        self.cl_args = cl_args
        self.csv_file = cl_args.csv_file
        self.death_delay = cl_args.death_delay
        self.recover_delay = cl_args.recover_delay

    def run(self):
        test_func(self.csv_file, self.death_delay, self.recover_delay)

def call_runner(cl_args) :
    os.umask(0o002)
    impl = cl_args.run_class(cl_args)
    return impl.run()

if __name__ == '__main__':
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    # parser for the start_idea subcommand
    p_start_idea = subparsers.add_parser('find_active')
    p_start_idea.set_defaults(run_class=FindActive)
    p_start_idea.add_argument('-d', '--death-delay', help='Avg. days, symptomatic to death', type=int, default=17)
    p_start_idea.add_argument('-r', '--recover-delay', help='Avg. days, symptomatic to recovery', type=int, default=14)
    p_start_idea.add_argument('-i', '--csv-file', help='CSV input file', type=str, required=True)

    # generic subcommand execution call
    parsed_args = parser.parse_args()
    #print parsed_args
    exit(call_runner(parsed_args))
