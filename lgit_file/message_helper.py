#!/usr/bin/env python3

import sys


def message(error_number, file_name="", continue_if_print=False):
    '''
    Description: To print one of the following message to user
    Input argument:
        * error_number: a key of dict: error_list below
        * file_name: name of the file
        * continue_if_print: by default set to False,
        will exit if change to True
    Output:
        * value according to each key
    '''
    error_list = {
        1: "Git repository already initialized.",
        2: "fatal: not removing '" + file_name + "' recursively",
        3: "fatal: pathspec '" + file_name + "' did not match any files",
        4: "On branch master",
        5: "No commits yet",
        6: "fatal: not a git repository (or any of the parent directories)"
    }
    print(error_list[error_number])
    if not continue_if_print:
        sys.exit()
