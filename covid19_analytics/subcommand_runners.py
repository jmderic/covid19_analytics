# Copyright J. Mark Deric, 2020.  All rights reserved

from importlib import import_module

class FindActive:
    def __init__(self, cl_args):
        self.cl_args = cl_args
        self.csv_file = cl_args.csv_file
        self.death_delay = cl_args.death_delay
        self.recover_delay = cl_args.recover_delay
        self.log_plot = cl_args.log_plot
        self.impl = import_module('.active_case_analysis',
                                  'covid19_analytics')

    def run(self):
        df = self.impl.compute_active(self.csv_file, self.death_delay,
                                      self.recover_delay)
        self.impl.plot_active(df, self.log_plot)

class Jhu2Csv:
    def __init__(self, cl_args):
        self.impl = import_module('.scrub_jhu', 'covid19_analytics')
        self.rf = self.impl.Reformatter(cl_args)

    def run(self):
        self.rf.create_input_data()
