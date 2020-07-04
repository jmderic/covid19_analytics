# Copyright J. Mark Deric, 2020.  All rights reserved

from pathlib import Path

import pandas as pd

def date_reorg(str):
    mdy = str.split('/')
    return f'20{int(mdy[2]):02}-{int(mdy[0]):02}-{int(mdy[1]):02}'

class Reformatter:
    def __init__(self, cl_args):
        cwd = Path.cwd()
        data_dir = cwd / cl_args.working_data
        self.wrk_dir = data_dir.resolve()
        #print(f'Working directory: {self.wrk_dir}')

    def create_input_data(self):
        files = { 'cases' : 'results_confirmed.csv',
                  'deaths' : 'results_deaths.csv' }
        df_dict = {}
        for datum in ('cases', 'deaths'):
            df_raw = pd.read_csv(self.wrk_dir / files[datum])
            #print(df_raw)
            df = df_raw.transpose()
            df = df.reset_index()
            df = df.rename(columns={"index" : "Date", 0 : datum})
            first_day = df.Date.eq("1/22/20").idxmax()
            df = df.drop(list(range(0,first_day)))
            df[datum] = df[datum].diff()
            diff_nan = df.Date.isna().idxmax()
            df = df.drop([diff_nan])
            df['Date'] = [date_reorg(x) for x in df['Date']]
            df['Date'] = df['Date'].astype('datetime64[D]')
            df[datum] = df[datum].astype('int32')
            df = df.sort_values(by=['Date'])
            df = df.set_index('Date')
            df_dict[datum] = df
            #print(df.info())
            #print(df)
        df_both = df_dict['cases'].join(df_dict['deaths'], how='inner')
        print(df_both)
