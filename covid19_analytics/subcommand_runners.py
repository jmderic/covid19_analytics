
from covid19_analytics.active_case_analysis import compute_active, plot_active

class FindActive:
    def __init__(self, cl_args):
        self.cl_args = cl_args
        self.csv_file = cl_args.csv_file
        self.death_delay = cl_args.death_delay
        self.recover_delay = cl_args.recover_delay
        self.log_plot = cl_args.log_plot

    def run(self):
        df = compute_active(self.csv_file, self.death_delay, self.recover_delay)
        plot_active(df, self.log_plot)
