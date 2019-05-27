#!/usr/bin/env python3


import hashlib
from os import path, walk
from argparse import ArgumentParser
from json import dumps


def get_parser():
    """
    Description: Parse user input
    Input: no input
    Output:
        args: arguments from user's inputs
    """
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True,
                        help='accepts one mandatory argument that '
                             'identifies the root directory to start '
                             'scanning for duplicate files')
    args = parser.parse_args()
    return args


def scan_files(directory):
    '''
    Description: Scan through a directory, return all of the files inside
                 and files inside subfolders,
    Input:
        directory: a directory path
    Output:
        all_files: a list of file path names
    '''
    base_path = path.abspath(directory)
    all_files = []
    for root, dirs, files in walk(base_path):
        for name in files:
            path_name = path.join(root, name)
            if not path.islink(path_name):
                all_files.append(path_name)
    return all_files


def group_files_by_size(file_path_names):
    '''
    Description: loop through a list of path names, return list of groups
                that containing path file names with the same size
    Input:
        file_path_names: a list of path file path names
    Output:
        @return: a list of lists of file path names that have the same size
    '''
    file_size_dict = dict()
    for file_name in file_path_names:
        file_size = path.getsize(file_name)
        if file_size == 0:
            continue
        elif file_size in file_size_dict.keys():
            file_size_dict[file_size].append(file_name)
        else:
            file_size_dict[file_size] = [file_name]
    return [group for group in file_size_dict.values()
            if len(group) > 1]


def get_file_checksum(file_path_name):
    """
    Description: Calculate md5 of file
    Input argument:
        file_path_name: the file path name to get md5
    Output:
        @return: md5 value of the file
    """
    hash_md5 = hashlib.md5()
    with open(file_path_name, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 12), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def group_files_by_checksum(file_path_names):
    '''
    Description: loop through a list of path names, return list of groups
                that containing files that have same md5 values
    Input:
        file_path_names: a list of path file path names
    Output:
        @retun: a list of lists of file path names
                                that have the same md5 value
    '''
    duplicate_checksum_dict = dict()
    for file_name in file_path_names:
        check_sum = get_file_checksum(file_name)
        if check_sum is None:
            continue
        elif check_sum in duplicate_checksum_dict.keys():
            duplicate_checksum_dict[check_sum].append(file_name)
        else:
            duplicate_checksum_dict[check_sum] = [file_name]
    return [group for group in duplicate_checksum_dict.values()
            if len(group) > 1]


def group_duplicate_files(file_path_names):
    '''
    Description: given a list of file path names, return groups
                of file path names that are actually copy of each other.
    Input:
        file_path_names:  list of path file path names
    Output:
        @return: a list of lits of file path names
    '''
    groups_dup_files = []
    for gr_by_size in group_files_by_size(file_path_names):
        groups_dup_files += group_files_by_checksum(gr_by_size)
    return [gr for gr in groups_dup_files if len(gr) > 1]


def main():
    args = get_parser()
    if args.path and not path.isdir(args.path):
        print("Invalid path")
        exit(1)
    file_path_names = scan_files(args.path)
    duplicate_files = group_duplicate_files(file_path_names)
    print(dumps(duplicate_files, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
