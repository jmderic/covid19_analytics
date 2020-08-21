# -*- coding: utf-8 -*-
# Copyright J. Mark Deric, 2020.  All rights reserved

from pathlib import Path

def get_wrkcsv_paths(csv_filename, relative_wrkdir):
    cwd = Path.cwd()
    data_dir = cwd / relative_wrkdir
    wrk_dir = data_dir.resolve()
    #print(f'Working directory: {wrk_dir}')
    return (wrk_dir, wrk_dir / csv_filename, )

import subprocess

def run_cmd(c, input=None, verbose=False):
    if verbose:
        print(f'Running {c}')
    input_pipe = subprocess.PIPE if input else None
    expand = isinstance(c,str)
    p = subprocess.Popen(c, stdin=input_pipe, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=expand)
    (out, err) = p.communicate(input)
    return (p.returncode, out, err)

from contextlib import contextmanager
import os

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

import datetime

def get_ts_fm_dt(dt) :
    return dt.strftime('%Y%m%d_%H%M%S')

def get_timestamp() :
    dt_now = datetime.datetime.now()
    return get_ts_fm_dt(dt_now)

# not used, yet
def get_dt_fm_ts(ts) :
    return datetime.datetime(int(ts[0:4]), int(ts[4:6]), int(ts[6:8]),
                             int(ts[9:11]), int(ts[11:13]), int(ts[13:]))
