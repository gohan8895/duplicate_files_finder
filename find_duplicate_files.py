#!/usr/bin/env python3

# from hashlib import md5
import hashlib
from os import path, walk
from argparse import ArgumentParser
from json import dumps


# def get_parser():
#     """
#     parse input
#     :return: arguments from console
#     """
#     parser = ArgumentParser()
#     # Way_point 1:
#     parser.add_argument('-p', '--path', type=str, required=True,
#                         help='accepts one mandatory argument that '
#                              'identifies the root directory to start '
#                              'scanning for duplicate files')
#     # Way_point 8:
#     parser.add_argument('-b', '--bonus', type=bool,
#                         help='another method to find duplicate files that '
#                              'would be much faster than using hash algorithm')
#     args = parser.parse_args()
#     if not path.isdir(args.path):
#         parser.print_help()
#         exit(1)
#     return args

def read_args():
    finder = ArgumentParser()
    finder.add_argument('-p', '--path',
                        help="directory want to find duplicate",)
    return finder.parse_args()


def scan_files(directory):
    '''
	Description: Scan through a directory, return all of the files inside
				 and files inside subfolders,
	Input:
		directory: a directory path
	Output:
		all_files: a list of file names
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
				that containing files with the same size
	Input:
		file_path_names: a list of path file names
	Output:
		groups: a list of list
	'''
	file_size_dict = dict()
	groups = list()
	for file_name in file_path_names:
		file_size = path.getsize(file_name)
		if file_size == 0:
			continue
		elif file_size in file_size_dict.keys():
			file_size_dict[file_size].append(file_name)
		else:
			file_size_dict[file_size] = [file_name]
	for x in file_size_dict.keys():
		if len(file_size_dict[x]) > 1:
			groups.append(file_size_dict[x])
	return groups


def get_file_checksum(file_path_name):
    """
    Description: Calculate md5 of file
    Input argument:
        * file_path_name: the file name to get md5
    Output:
        * hash_md5: md5 value of the file
    """
    hash_md5 = hashlib.md5()
    with open(file_path_name, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 12), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def group_files_by_checksum(file_path_names):
	# must use get_file_checksum
	group_duplicate_checksum = list()
	duplicate_checksum_dict = dict()
	for file_name in file_path_names:
		check_sum = get_file_checksum(file_name)
		if check_sum is None:
			continue
		elif check_sum in duplicate_checksum_dict.keys():
			duplicate_checksum_dict[check_sum].append(file_name)
		else:
			duplicate_checksum_dict[check_sum] = [file_name]
	for group in duplicate_checksum_dict.values():
		if len(group) > 1:
			group_duplicate_checksum.append(group)
	return group_duplicate_checksum


def group_duplicate_files(file_path_names):
	# group_files_by_size
	# group_files_by_checksum
    groups_dup_files = []
    for gr_by_size in group_files_by_size(file_path_names):
        groups_dup_files += group_files_by_checksum(gr_by_size)
    return [gr for gr in groups_dup_files if len(gr) > 1]


def main():
    args = read_args()
    if args.path and not path.isdir(args.path):
        print("Invalid path")
        exit(1)
    files = scan_files(args.path or ".")
    duplicates = find_duplicate_files(files)
    print(dumps(duplicates, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()

