#!/usr/bin/env python3

"""
    Finds matching regions in SentiBio exports
    Version:    1.0 (2020-06-01)
    Author:     Christian Rickert
    Group:  Human Immune Monitoring Shared Resource (HIMSR)
            University of Colorado, Anschutz Medical Campus
"""

#  imports

import os
import shutil

#  functions

# from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
def flatten(deep_list=[]):
    """ Returns a flattened list with elements from (deep) lists or tuples """
    flat_list = []
    for item in deep_list:
        if isinstance(item, (list, tuple)):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list

def get_files(path='/home/user/', pattern='', recursive=False):
    """ Returns all files in path matching the pattern. """
    files = []
    realpath = os.path.realpath(path)
    with os.scandir(realpath) as file_iterator:
        for fileobject in file_iterator:
            if fileobject.is_file() and fileobject.name.endswith(pattern):  # simple file match
                files.append(fileobject.path)
            elif recursive and not os.path.islink(fileobject.path) and not fileobject.name.startswith(".") and fileobject.is_dir():  # recursive folder search
                files.append(get_files(path=fileobject.path, pattern=pattern, recursive=recursive))
    return flatten(files)

def get_folders(path='/home/user/', pattern='', recursive=False):
    """ Returns all folders in path matching the pattern. """
    folders = []
    realpath = os.path.realpath(path)
    with os.scandir(realpath) as file_iterator:
        for fileobject in file_iterator:
            if not os.path.islink(fileobject.path) and not fileobject.name.startswith(".") and fileobject.is_dir():  # simple folder match
                folders.append(fileobject.path)
                if recursive:  # traverse into subfolder
                    folders.append(get_folders(path=os.path.join(realpath, foldertarget), pattern=pattern, recursive=recursive))
    return flatten(folders)

#  constants & variables

''' assuming: export > channel > batch > file '''
export_folder = r"C:\Users\Christian Rickert\Documents\GitHub\phenoptr-fixes\export"
#export_folder = r"\\Micro-LS7.ucdenver.pvt\HI3-Microscope\Data\Vectra3\SentiBio\Panel  63-2 EXPORT"
channel_folders = []
batch_folders = []
batch_names = []

''' retrieve unique batch folder names and store folder locations '''
print("Retrieving folder lists (1/3):")
print("------------------------------")
print("EXPORT: \"" + export_folder.rsplit('\\', 1)[1] + "\"")
for channel_folder in get_folders(export_folder):
    channel_name = channel_folder.rsplit('\\', 1)[1]
    print("\tCHANNEL: \"" + channel_name + "\"")
    channel_folders.append(channel_folder)

    for batch_folder in get_folders(channel_folder):
        batch_name = batch_folder.rsplit('\\', 1)[1]
        print("\t\t\tBATCH: \"" + batch_name + "\"")
        batch_folders.append(batch_folder)
        if batch_name not in batch_names:  # unique names only
            batch_names.append(batch_name)
print(os.linesep)

''' count unique file names in batch folders '''
print("Counting unique file names (2/3):")
print("---------------------------------")
for batch_name in batch_names:
    print("BATCH: \"" + batch_name + "\"")
    
    name_count = {}
    for channel_folder in channel_folders:
        print("\tCHANNEL: \"" + channel_folder + "\"")

        for file in get_files(os.path.join(channel_folder, batch_name), ".txt"):
            file_name = file.rsplit('\\', 1)[1]
            if file_name in name_count:
                name_count[file_name] += 1  # increment key value
            else:  # file not in list
                name_count[file_name] = 1  # add key: value pair
print(os.linesep)

''' move files to a subfolder, if they don't exist in all batch folders '''
print("Moving suplus files to folder (2/3):")
print("------------------------------------")
max_channels = len(channel_folders)
for channel_folder in channel_folders:
    print("CHANNEL: \"" + channel_folder + "\"")

    for batch_name in batch_names:
        print("\tBATCH: \"" + batch_name + "\"")

        cwd_path = os.path.join(channel_folder, batch_name)
        tmp_path = os.path.join(cwd_path + os.sep + "surplus")
        for name, count in name_count.items():
            if count < max_channels:
                # if not os.path.exists(tmp_path):
                #     os.mkdir(tmp_path)
                # shutil.move(os.path.join(cwd_path, name), os.path.join(tmp_path, name))  # try to preserve metadata
                print("\t\t" + os.path.join(cwd_path, name))
print(os.linesep)
