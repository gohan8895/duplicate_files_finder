#!/usr/bin/env python3
import os
import argparse
import hashlib
from datetime import datetime
from time import time


#############################################################################
#  Function Section                                                         #
#############################################################################

def parser_input():
    """
    Parser for command-line options
    """
    parser = argparse.ArgumentParser(usage="./lgit.py <command> [<args>]")
    subparsers = parser.add_subparsers(dest="option")
    init_parser = subparsers.add_parser("init")
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("filenames", nargs="+", type=str)
    remove_parser = subparsers.add_parser("rm")
    remove_parser.add_argument("filenames", nargs="+", type=str)
    commit_parser = subparsers.add_parser("commit")
    commit_parser.add_argument("-m", dest="message", nargs=1, required=True)
    log_parser = subparsers.add_parser("log")
    config_parser = subparsers.add_parser("config")
    config_parser.add_argument("--author", nargs=1, required=True)
    list_files_parser = subparsers.add_parser("ls-files")
    status_parser = subparsers.add_parser("status")
    return parser.parse_args()


def get_file_by_dir(directory):
    """
    Description: Get all file in working directory
    Input argument:
        * directory: the path of directory to get
    Output:
        * list: all_file
    """
    all_file = []
    for root, dirs, files in os.walk(directory, topdown=True):
        all_file.extend([os.path.join(root, name) for name in files
                        if ".lgit" not in os.path.join(root, name)])
    return all_file


def calculate_hashes(fname):
    """
    Description: Calculate sha1 of file
    Input argument:
        * fname: the file name to get sha1
    Output:
        * hash_sha1
    """
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 20), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


def check_exist():
    """
    Description: To check of '.lgit' is exist at working directory
    Input argument: None
    Output:
        * True if exist
        * False if not exist
    """
    if get_path() is not "":
        return True
    else:
        return False


def copy_content(file_1, file_2):
    """
    Description: To create file 2 copy content of file 1 to file 2
    Input argument:
        * file_1: the file name want to copy
        * file_2: the file name after copy
    Output:
        * file_2
    """
    try:
        with open(file_2, 'wb+') as output, open(file_1, 'rb') as input:
            while True:
                data = input.read(4096)
                if not data:  # end of file reached
                    break
                output.write(data)
    except (PermissionError, FileExistsError):
        pass


def get_time(current_path):
    """
    Description: Get the time of last modification of path
    Input argument:
        * current_path: the path to get time
    Output:
        * datetime
    """
    timestamp = datetime.fromtimestamp(os.path.getmtime(current_path))
    return datetime.strftime(timestamp, "%Y%m%d%H%M%S")


def get_author(isFile=False):
    """
    Description: Get author from config file or argument
    Input argument:
        * isFile: If isFile is true, get author from config file
    Output:
        * author
    """
    if isFile:
        try:
            with open(config_path, "r") as config:
                return config.read().strip('\n')
        except (PermissionError, FileNotFoundError):
            pass
    else:
        argv = parser_input()
        if argv.option == "config":
            return argv.author[0]


def validate_input(files):
    """
    Description: To check and return file if vallid
    Input argument:
        * files: list of path from user config
    Output:
        * List of file
    """
    if '.' in files or '*' in files:
        return sorted([file[2:] for file in get_file_by_dir('.')])
    list_file = []
    for file in files:
        if os.path.isfile(file) and '.lgit/' not in file:
            list_file.append(file)
        elif os.path.isdir(file):
            list_file += get_file_by_dir(file)
        else:
            message(3)
    return sorted(list_file)


def get_path():
    """
    Description: To find directory refer which contain '.lgit'
    Input argument: None
    Output: Path of dicrectory
    """
    path = os.getcwd()
    while path != '/':
        if os.path.isdir(path + '/.lgit'):
            return path + '/'
        path = os.path.dirname(path)
    return ""


#############################################################################
#  Mapname Section                                                          #
#############################################################################

"""
Mapping string to using
"""
break_line = '\n'
config_path = get_path() + ".lgit/config"
index_path = get_path() + ".lgit/index"
commit_path = get_path() + ".lgit/commits"
snapshot_path = get_path() + ".lgit/snapshots"
objects_path = get_path() + ".lgit/objects"
