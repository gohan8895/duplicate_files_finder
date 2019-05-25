#!/usr/bin/env python3

from hashlib import md5
from os import path, walk
from argparse import ArgumentParser
from json import dumps


def get_parser():
	pass


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
	# must use module hashlib
	pass


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

  
def group_files_by_checksum(file_path_names):
	# must use get_file_checksum
	pass


def group_duplicate_files(file_path_names):
	# group_files_by_size
	# group_files_by_checksum
	pass


def main():
	list_path_names = scan_files('test')
	for x in list_path_names:
		print(x)
	file_size_dict = group_files_by_size(list_path_names)
	for x in file_size_dict:
		print(x)

if __name__ == '__main__':
	main()

