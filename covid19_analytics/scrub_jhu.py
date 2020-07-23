# -*- coding: utf-8 -*-
# Copyright J. Mark Deric, 2020.  All rights reserved

import pandas as pd

import common

def date_reorg(str):
    mdy = str.split('/')
    return f'20{int(mdy[2]):02}-{int(mdy[0]):02}-{int(mdy[1]):02}'

class Reformatter:
    def __init__(self, csv_filename, wrk_dir):
        tup = common.get_wrkcsv_paths(csv_filename, wrk_dir)
        self.wrk_dir, self.csv_file = tup

    def create_input_data(self):
        files = { 'Cases' : 'results_confirmed.csv',
                  'Deaths' : 'results_deaths.csv' }
        df_dict = {}
        for datum in files:
            df_raw = pd.read_csv(self.wrk_dir / files[datum])
            df = df_raw.transpose()
            df = df.reset_index()
            col_name = f'Cum{datum}'
            df = df.rename(columns={"index" : "Date", 0 : col_name})
            first_day = df.Date.eq("1/22/20").idxmax() # FIXME: maybe regexp?
            df = df.drop(list(range(0,first_day)))

            df['Date'] = [date_reorg(x) for x in df['Date']]
            df['Date'] = df['Date'].astype('datetime64[D]')
            df[col_name] = df[col_name].astype('int32')
            df = df.sort_values(by=['Date'])
            df = df.set_index('Date')
            df_dict[datum] = df
            #print(df.info())
            #print(df)
        df_both = df_dict['Cases'].join(df_dict['Deaths'], how='inner')
        
        df_both.to_csv(self.csv_file)
        print(df_both)
        print(df_both.info())
