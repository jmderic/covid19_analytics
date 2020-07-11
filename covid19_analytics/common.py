# Copyright J. Mark Deric, 2020.  All rights reserved

from pathlib import Path

def get_wrkcsv_paths(csv_filename, relative_wrkdir):
    cwd = Path.cwd()
    data_dir = cwd / relative_wrkdir
    wrk_dir = data_dir.resolve()
    #print(f'Working directory: {wrk_dir}')
    return (wrk_dir, wrk_dir / csv_filename, )
