#!/usr/bin/env python3

import sys
import os
from git_utilities import *
from git_helper import *
from message_helper import *


def git_init():
    '''
    Description: initialises version control in the current directory
    '''
    if not check_exist():
        os.mkdir(".lgit", 0o775)
        os.mkdir(".lgit/commits", 0o775)
        os.mkdir(".lgit/objects", 0o775)
        os.mkdir(".lgit/snapshots", 0o775)
        logname = str.encode(os.getenv('LOGNAME'))
        config = os.open(".lgit/config", os.O_CREAT | os.O_RDWR)
        os.write(config, logname)
        os.close(config)
        index = os.open(".lgit/index", os.O_CREAT | os.O_RDWR)
        os.close(index)
    else:
        message(1)


def git_add(files):
    '''
    Description: stages changes, add inputed files for commit
    '''
    index_data = get_index_information()
    for file in validate_input(files):
        hashValue = calculate_hashes(file)
        dirName = objects_path + "/" + hashValue[:2]
        fileNameHash = dirName + "/" + hashValue[2:]
        try:
            os.mkdir(dirName, 0o775)
            copy_content(file, fileNameHash)
        except FileExistsError:
            pass
        if file not in index_data.keys():
            index_data[file] = set_index_value(file, '', " "*40)
        else:
            value = index_data[file]
            index_data[file] = set_index_value(file, '', value[97:137])
    write_index(index_data)


def git_remove(files):
    '''
    Description: removes a file from the working directory and the index
    '''
    index_data = get_index_information()
    for file in files:
        if os.path.isdir(file):
            message(2, file)
        elif os.path.isfile(file) and file in index_data.keys():
            os.unlink(file)
            del index_data[file]
        else:
            message(3, file)
    write_index(index_data)


def git_config():
    '''
    Description: sets a user for authoring the commits
    '''
    user_name = get_author()
    try:
        with open(config_path, 'w+') as file:
            file.write(user_name + break_line)
    except PermissionError:
        pass


def git_commit(message):
    '''
    Description: creates a commit with the changes currently staged
    '''
    index_data = get_index_information()
    present_time = datetime.fromtimestamp(time())
    init_commit(message, present_time)
    init_snap_file(index_data, present_time)
    write_index(index_data)


def git_status():
    '''
    Description: updates the index with the content of the working directory
    and displays the status of tracked/untracked files
    '''
    branch_output()
    (to_be_committed, not_staged_for_commit) = get_list_status()
    committed_output(to_be_committed)
    not_staged_commit_output(not_staged_for_commit)
    untracked_output()


def git_lsfile():
    '''
    Description: lists all the files currently tracked in the index,
    relative to the current directory
    '''
    list_all_file = [file[2:] for file in get_file_by_dir('.')]
    tracked = get_index_information().keys()
    ls_file = []
    for file in list_all_file:
        for track_file in tracked:
            if track_file.endswith(file):
                ls_file.append(file)
    ls_file.sort()
    for file in ls_file:
        print(file)


def git_log():
    '''
    Description: shows the commit history
    '''
    committed = sorted(os.listdir(commit_path), reverse=True)
    for file in committed:
        commit_history(file)
        if file != committed[-1]:
            print(break_line)


def main():
    '''
    Description: perform a light version of git
    '''
    args = parser_input()
    if args.option == "init":
        git_init()
    elif check_exist():
        if args.option == "add":
            git_add(args.filenames)
        elif args.option == "rm":
            git_remove(args.filenames)
        elif args.option == "config":
            git_config()
        elif args.option == "commit":
            git_commit(args.message[0])
        elif args.option == "status":
            git_status()
        elif args.option == "log":
            git_log()
        elif args.option == "ls-files":
            git_lsfile()
    else:
        message(6)


if __name__ == '__main__':
    main()
