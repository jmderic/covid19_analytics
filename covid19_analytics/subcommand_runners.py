# -*- coding: utf-8 -*-
# Copyright J. Mark Deric, 2020.  All rights reserved

# Important concept of this file, missed in prior commits.  This file
# translates cl_args to the values needed to construct the impl
# object.  That way, the impl object can be called in interactive
# testing with real parameters, no need to map into a cl_args object.

from importlib import import_module

csv_filename = 'covid_oc.csv'

class FindActive:
    def __init__(self, cl_args):
        impl = import_module('.active_case_analysis',
                             'covid19_analytics')
        file_stub = cl_args.file_stub
        wrk_dir = cl_args.wrk_dir
        recover_delay = cl_args.recover_delay
        self.ac = impl.ActiveCases(file_stub, wrk_dir, recover_delay)

    def run(self):
        self.ac.create_active_plots()

class Jhu2Csv:
    def __init__(self, cl_args):
        impl = import_module('.scrub_jhu', 'covid19_analytics')
        wrk_dir = cl_args.wrk_dir
        self.rf = impl.Reformatter(csv_filename, wrk_dir)

    def run(self):
        self.rf.create_input_data()

class PlotData:
    def __init__(self, cl_args):
        impl = import_module('.active_case_analysis',
                             'covid19_analytics')
        file_stub = cl_args.file_stub
        wrk_dir = cl_args.wrk_dir
        # so far recover_delay is a don't care for this subcommand
        self.ac = impl.ActiveCases(file_stub, wrk_dir, recover_delay=14)

    def run(self):
        self.ac.create_daily_plots()

class GetJhuData:
    def __init__(self, cl_args):
        impl = import_module('.get_jhu',
                             'covid19_analytics')
        wrk_dir = cl_args.wrk_dir
        jhu_repo = cl_args.jhu_repo
        json_data_list = cl_args.json_data_list
        self.jdg = impl.JhuDataGrabber(wrk_dir, jhu_repo, json_data_list)

    def run(self):
        self.jdg.run()

class CreatePlots:
    def __init__(self, cl_args):
        impl = import_module('.active_case_analysis',
                             'covid19_analytics')
        wrk_dir = cl_args.wrk_dir
        recover_delay = cl_args.recover_delay
        self.use_json = cl_args.use_json
        if self.use_json:
            self.impl = impl
            self.wrk_dir = wrk_dir
            self.recover_delay = recover_delay
        else:
            file_stub = cl_args.file_stub
            self.ac = impl.ActiveCases(file_stub, wrk_dir, recover_delay)

    def run(self):
        if self.use_json:
            json = import_module('json')
            pathlib = import_module('pathlib')
            wrk_dir = pathlib.Path(self.wrk_dir)
            with open(wrk_dir / 'state.json') as f:
                jhu_data = json.load(f)
            ts = jhu_data["timestamp"]
            locs = jhu_data["locations"]
            for loc in locs:
                file_stub = f'{ts}_{loc}'
                print(f'Plot timestamp/location {file_stub}')
                ac = self.impl.ActiveCases(file_stub, self.wrk_dir,
                                           self.recover_delay)
                ac.set_location(loc)
                ac.create_active_plots()
                ac.create_daily_plots()
        else:
            self.ac.create_active_plots()
            self.ac.create_daily_plots()
