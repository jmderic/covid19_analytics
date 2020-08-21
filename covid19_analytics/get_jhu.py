# -*- coding: utf-8 -*-
# Copyright J. Mark Deric, 2020.  All rights reserved

import pandas as pd
import common
import json
from pathlib import Path
from io import StringIO
from copy import deepcopy
from pprint import pprint

def date_reorg(str):
    mdy = str.split('/')
    return f'20{int(mdy[2]):02}-{int(mdy[0]):02}-{int(mdy[1]):02}'

class JhuDataGrabber:
    def __init__(self, wrk_dir, jhu_repo, json_data_list):
        for p in ('wrk_dir', 'jhu_repo', 'json_data_list'):
            exec(f'self.{p} = Path({p}).expanduser().resolve()')
            print(f'self.{p} = ' + str(eval(f'self.{p}')))
        # self.start_dir = Path.cwd() # prefer with cd as below
        with common.cd(self.jhu_repo):
            # FIXME: check return values and do the right thing
            common.run_cmd(('git', 'checkout', 'master'))
            common.run_cmd(['git', 'pull'])
            self.rc_tup = common.run_cmd(['git', 'rev-parse', 'HEAD'])
        with open(self.json_data_list) as f:
            self.jhu_data = json.load(f)
        self.jhu_tmp = deepcopy(self.jhu_data)
        self.jhu_data['timestamp'] = common.get_timestamp()
        #print(self.jhu_data)
        #print(json.dumps(self.jhu_data, sort_keys=True, indent=4))

    def run(self):
        csvs = { 'Cases' : 'confirmed',
                 'Deaths' : 'deaths' }
        input_dir = Path(f'{self.jhu_repo}/csse_covid_19_data/'
                         + 'csse_covid_19_time_series')
        for csv in csvs:
            self.jhu_tmp[csv] = {}
            input_file = input_dir / f'time_series_covid19_{csvs[csv]}_US.csv'
            with open(input_file) as f:
                self.extract_data(csv, f)
                #print(f'Done file {self.jhu_tmp["locations"]}')
        pprint(self.jhu_tmp)
        loc_data = self.jhu_tmp["locations"]
        for loc_datum in loc_data:
            self.create_csv_files(loc_datum, loc_data[loc_datum])
        # save the snapshot first, state last after everything
        # succeeds
        state = json.dumps(self.jhu_data, sort_keys=True, indent=4)
        state_loc = self.jhu_data["locations"]
        for loc_datum in loc_data:
            state_loc[loc_datum]['Pop'] = loc_data[loc_datum]['Pop']
            state_loc[loc_datum]['Pop_num'] = loc_data[loc_datum]['Pop_num']
        self.jhu_data['commit_id'] = self.rc_tup[1].decode('utf-8').rstrip()
        snapshot = self.wrk_dir / f'{self.jhu_data["timestamp"]}_state.json'
        with open(snapshot, 'w') as f:
            json.dump(self.jhu_data, f, sort_keys=True, indent=4)
        with open(self.wrk_dir / 'state.json', 'w') as f:
            f.write(state)

    def extract_data(self, csv, f):
        heading = True
        for line in f:
            if heading:
                self.jhu_tmp[csv]['heading'] = line
                heading = False
                continue
            loc_data = self.jhu_tmp["locations"]
            for loc_datum in loc_data:
                loc = loc_data[loc_datum]
                if csv in loc:
                    continue
                if loc["jhu_srch"] in line:
                    loc[csv] = {}
                    loc[csv]['data'] = line
                    loc[csv]['csv'] = StringIO(self.jhu_tmp[csv]['heading']
                                               + line)
                    #print(f'self.jhu_tmp {self.jhu_tmp["locations"][loc_datum]}' )

    def create_csv_files(self, loc_datum, loc):
        print(f'create_csv_files {loc_datum}: {loc}')
        data = ('Cases', 'Deaths' )
        df_dict = {}
        for datum in data:
            df_raw = pd.read_csv(loc[datum]['csv'])
            df = df_raw.transpose()
            if datum == 'Deaths':
                popul = df.at["Population", 0]
                self.jhu_tmp["locations"][loc_datum]['Pop_num'] = popul
                self.jhu_tmp["locations"][loc_datum]['Pop'] = f'{popul:,}'
                print(f'Pop. {popul}')
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
        
        df_both.to_csv(self.wrk_dir /
                       f'{self.jhu_data["timestamp"]}_{loc_datum}.csv')
        print(df_both)
        print(df_both.info())
