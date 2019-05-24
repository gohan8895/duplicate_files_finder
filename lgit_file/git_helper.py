#!/usr/bin/env python3
import os
from git_utilities import *
from message_helper import *


#############################################################################
#  Index Helper Section                                                     #
#############################################################################

def get_index_information():
    """
    Description: Get the value of index file
    Input argument: None
    Output:
        * Dictionary: index
            + Key: the file pathname
            + value: All fields of the file
    """
    index = {}
    try:
        with open(index_path, "r") as file:
            for line in file:
                index[line[:-1].split()[-1]] = line
    except PermissionError:
        pass
    return index


def set_index_value(file, hash_add, hash_commit):
    """
    Description: Change the value of index file through dictionary
    Input argument:
        * file: the path/file name is working
        * hash_add: the SHA1 of the content in the working directory
        * hash_commit: the SHA1 of the file content after commit'ed
    Output:
        * dictionary: index_value
    """
    time = get_time(file)
    hash_file = calculate_hashes(file)
    if not hash_add:
        hash_add = hash_file
    index_value = ' '.join([
                            time,
                            hash_file,
                            hash_add,
                            hash_commit,
                            file
                            ]) + break_line
    return index_value


def write_index(data):
    """
    Description: Writing data into index file
    Input argument:
        * data: dictionary return by Call get_index_information() function
    Output:
        * file: .lgit/index
    """
    index_data = ''.join(data.values())
    with open(index_path, 'w+') as index:
        index.write(index_data)


#############################################################################
#  Commit Helper                                                            #
#############################################################################

def init_commit(message, present_time):
    """
    Description: Initialize the file with the message content
    Input argument:
        * message: The content of message to commit
        * present_time: The present time to commnit
    Output:
        * file in commnit folder
    """
    user_name = get_author(True)
    if not user_name:
        sys.exit()
    file_name = commit_path + "/" + present_time.strftime('%Y%m%d%H%M%S.%f')
    try:
        commit = os.open(file_name, os.O_CREAT | os.O_RDWR)
        os.write(commit, user_name.encode())
        os.write(commit, break_line.encode())
        os.write(commit, present_time.strftime('%Y%m%d%H%M%S').encode())
        os.write(commit, break_line.encode())
        os.write(commit, break_line.encode())
        os.write(commit, message.encode())
        os.write(commit, break_line.encode())
        os.close(commit)
    except (PermissionError):
        pass


def init_snap_file(index_data, present_time):
    """
    Description: Update the index file when commit and create snapshot file
    Input argument:
        * index_data: dictionary of index file
        * present_time: The present time to commnit
    Output:
        * dictionary: index_data
        * file in snapshots folder
    """
    for file in index_data.keys():
        value = index_data[file]
        index_data[file] = set_index_value(file, value[56:96], value[56:96])
        file_name = snapshot_path + "/" + \
            present_time.strftime('%Y%m%d%H%M%S.%f')
        try:
            snapshot = os.open(file_name, os.O_CREAT | os.O_RDWR)
            os.write(snapshot, (value[56:96] +
                                ' ' + file + break_line).encode())
            os.close(snapshot)
        except PermissionError:
            pass


#############################################################################
#  Status Helper                                                            #
#############################################################################

def get_list_status():
    """
    Description: get a list of files that have been added but not committed
                 and a list of files that have not been added for commit
    Input argument: None
    Out put: a tuple of two list
    """
    index_data = get_index_information()
    to_be_committed = []
    not_staged_for_commit = []
    for file in index_data.keys():
        value = index_data[file]
        index_data[file] = set_index_value(file, value[56:96], value[97:137])
        if value[56:96] != value[97:137]:
            to_be_committed.append(file)
        if value[56:96] != calculate_hashes(file):
            not_staged_for_commit.append(file)
    write_index(index_data)
    return (to_be_committed, not_staged_for_commit)


def get_untracked_files():
    '''
    Description: get a list of untracked files
    Input: None
    Out put: a list of untracked files
    '''
    untracked_files = []
    tracked_files = get_index_dict().keys()
    for path in sorted([file[2:] for file in get_all_files('.')]):
        if path not in tracked_files:
            untracked_files.append(path)
    return untracked_files


def branch_output():
    '''
    Description: always print "On branch master" at top
    '''
    message(4, continue_if_print=True)
    if len(os.listdir(commit_path)) == 0:
        message(5, continue_if_print=True)


def untracked_output():
    '''
    Description: print untracked files
    '''
    untracked = []
    index_data = get_index_information()
    tracked = index_data.keys()
    list_all_file = sorted([file[2:] for file in get_file_by_dir('.')])
    untracked.extend([file for file in list_all_file if file not in tracked])
    if len(untracked) > 0:
        print('Untracked files:')
        print('  (use "./lgit.py add <file>..." to '
              'include in what will be committed)')
        print('\n\t%s\n' % '\n\t'.join(untracked))
        print('nothing added to commit but untracked files '
              'present (use "./lgit.py add" to track)')


def not_staged_commit_output(files):
    '''
    Description: print files not added for commit
    '''
    if len(files) > 0:
        print('Changes not staged for commit:')
        print('  (use "./lgit.py add ..." to update what will be committed)')
        print('  (use "./lgit.py checkout -- ..." to '
              'discard changes in working directory)')
        print('\n\t modified: %s\n' % '\n\t modified: '.join(files))


def committed_output(files):
    '''
    Description: print files added but not commit
    '''
    if len(files) > 0:
        print('Changes to be committed:')
        print('  (use "./lgit.py reset HEAD ..." to unstage)')
        print('\n\t modified: %s\n' % '\n\t modified: '.join(files))


#############################################################################
#  Log Helper                                                               #
#############################################################################

def get_datetime(filename):
    '''
    Description: convert datetime of a file to readable format
    '''
    dt = datetime(
        year=int(filename[0:4]),
        month=int(filename[4:6]),
        day=int(filename[6:8]),
        hour=int(filename[8:10]),
        minute=int(filename[10:12]),
        second=int(filename[12:14]))
    return dt.strftime('%a %b %d %H:%M:%S %Y')


def commit_history(filename):
    '''
    Description: print information needed for lgit log
    '''
    try:
        with open(commit_path + '/' + filename, 'r') as file:
            content = file.readlines()
            if len(content) > 0:
                print('commit ' + filename)
                print('Author: ' + content[0].strip('\n'))
                print('Date: ' + get_datetime(filename))
                print('\n\t' + content[-1].strip('\n'))
    except (PermissionError, FileNotFoundError):
        pass
