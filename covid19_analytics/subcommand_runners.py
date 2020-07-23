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
        wrk_dir = cl_args.wrk_dir
        recover_delay = cl_args.recover_delay
        self.ac = impl.ActiveCases(csv_filename, wrk_dir, recover_delay)

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
        wrk_dir = cl_args.wrk_dir
        # so far recover_delay is a don't care for this subcommand
        self.ac = impl.ActiveCases(csv_filename, wrk_dir, recover_delay=14)

    def run(self):
        self.ac.create_daily_plots()
