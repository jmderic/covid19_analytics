#!/usr/bin/python3
# -*- Mode: Python; fill-column: 80 -*-

# Note: this is the newer app preamble
import os.path, sys
this_dir = os.path.dirname((lambda x:x).func_code.co_filename)
# jmd_python_dir = this_dir + '/..'
sys.path.append(this_dir)
# import test_startup
from argparse import ArgumentParser
# end: preamble

import SEFileAppRunner

def call_runner(cl_args) :
    os.umask(0o002)
    impl = cl_args.run_class(cl_args)
    return impl.run()

if __name__ == '__main__':
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    # parser for the start_idea subcommand
    p_start_idea = subparsers.add_parser('start_idea')
    p_start_idea.set_defaults(run_class=SEFileAppRunner.SENodeStart_Ideaer)
    p_start_idea.add_argument('directories', nargs=2, help='Directories to be compared')
    p_start_idea.add_argument('-o', '--output-stub', help='Output stub (dir/preamble)', required=True)
    p_start_idea.add_argument('-f', '--follow-symlinks', help='Follow symbolic links', action='store_true')
