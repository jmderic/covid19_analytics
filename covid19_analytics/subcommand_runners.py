# Copyright J. Mark Deric, 2020.  All rights reserved

from importlib import import_module

csv_filename = 'covid_oc.csv'

class FindActive:
    def __init__(self, cl_args):
        impl = import_module('.active_case_analysis',
                             'covid19_analytics')
        self.ac = impl.ActiveCases(csv_filename, cl_args)

    def run(self):
        self.ac.create_active_plots()

class Jhu2Csv:
    def __init__(self, cl_args):
        impl = import_module('.scrub_jhu', 'covid19_analytics')
        self.rf = impl.Reformatter(csv_filename, cl_args)

    def run(self):
        self.rf.create_input_data()
