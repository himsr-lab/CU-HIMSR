#!/usr/bin/env python3

"""
    Removes unmatched regions in phenoptrReports exports
    Version:    1.0 (2020-06-03)
    Author:     Christian Rickert
    Group:  Human Immune Monitoring Shared Resource (HIMSR)
            University of Colorado, Anschutz Medical Campus
"""

#  imports

import os
import shutil
import sys

#  functions

# from: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
def flatten(deep_list=None):
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
    with os.scandir(realpath) as fileobject_iterator:
        for fileobject in fileobject_iterator:
            if not os.path.islink(fileobject.path):
                if fileobject.is_file() and fileobject.name.endswith(pattern):  # simple file match
                    files.append(fileobject.path)
                elif recursive and fileobject.is_dir():
                    files.append( \
                        get_files(path=fileobject.path, pattern=pattern, recursive=recursive))
    return flatten(files)

def get_folders(path='/home/user/', pattern='', recursive=False):
    """ Returns all folders in path matching the pattern. """
    folders = []
    realpath = os.path.realpath(path)
    with os.scandir(realpath) as fileobject_iterator:
        for fileobject in fileobject_iterator:
            if not os.path.islink(fileobject.path):
                if fileobject.is_dir():  # simple folder match
                    folders.append(fileobject.path)
                    if recursive:  # traverse into subfolder
                        folders.append( \
                            get_folders(path=fileobject.path, pattern=pattern, recursive=recursive))
    return flatten(folders)

def println(string=""):
    ''' Prints a string and forces immediate output. '''
    print(string)
    sys.stdout.flush()

#  constants & variables

# assuming: export > channel > batch > file
EXPORT_FOLDER = r"C:\Users\Christian Rickert\Documents\GitHub\phenoptr-fixes\export"
#EXPORT_FOLDER = r"\\Micro-LS7.ucdenver.pvt\HI3-Microscope\Data\Vectra3\SentiBio\Panel  63-2 EXPORT"
CHANNEL_FOLDERS = []
BATCH_NAMES = []

# retrieve unique batch folder names and store folder locations
println(os.linesep)
println("Retrieving folder lists (1/3):")
println("------------------------------")
println("EXPORT: \"" + EXPORT_FOLDER.rsplit('\\', 1)[1] + "\"\n")
for channel_folder in get_folders(EXPORT_FOLDER):
    channel_name = channel_folder.rsplit('\\', 1)[1]
    println("\tCHANNEL: \"" + channel_name + "\"")
    CHANNEL_FOLDERS.append(channel_folder)

    for batch_folder in get_folders(channel_folder):
        batch_name = batch_folder.rsplit('\\', 1)[1]
        println("\t\tBATCH: \"" + batch_name + "\"")
        if batch_name not in BATCH_NAMES:  # unique names only
            BATCH_NAMES.append(batch_name)
CHANNEL_FOLDERS.sort()
BATCH_NAMES.sort()
println(os.linesep)

# count unique file names in batch folders
println("Counting unique file names (2/3):")
println("---------------------------------")
TOTAL = 0
LABELS = 0
UNMATCHED = 0
BATCH_LABEL_COUNTS = {}  # label counts by batch and channel
for batch_name in BATCH_NAMES:
    println("BATCH: \"" + batch_name + "\"")

    label_counts = {}  # label counts by channel
    for channel_folder in CHANNEL_FOLDERS:
        println("\tCHANNEL: \"" + channel_folder + "\"")

        for file in get_files(os.path.join(channel_folder, batch_name), ".txt"):
            file_name = file.rsplit('\\', 1)[1]
            if file_name in label_counts:
                label_counts[file_name] += 1  # increment key value
            else:  # file not in list
                label_counts[file_name] = 1  # add key: value pair
            TOTAL += 1
    BATCH_LABEL_COUNTS[batch_name] = label_counts
println(os.linesep)



# move files to a subfolder, if they don't exist in all batch folders
println("Moving unmatched files to folder (3/3):")
println("---------------------------------------")

CHANNELS = len(CHANNEL_FOLDERS)
for channel_folder in CHANNEL_FOLDERS:
    println("CHANNEL: \"" + channel_folder + "\"")

    for batch_name in BATCH_NAMES:
        println("\tBATCH: \"" + batch_name + "\"")

        for label, counts in BATCH_LABEL_COUNTS[batch_name].items():
            if counts < CHANNELS:  # label does not exist in all batch folders
                cwd_path = os.path.join(channel_folder, batch_name)
                tmp_path = os.path.join(cwd_path + os.sep + "unmatched")
                if not os.path.exists(tmp_path):
                    os.mkdir(tmp_path)
                try:
                    shutil.move(os.path.join(cwd_path, label), os.path.join(tmp_path, label))
                except FileNotFoundError:
                    pass
                UNMATCHED += 1

println(os.linesep)
println("CHANNELS: " + str(CHANNELS) + ", BATCHES: " + str(len(BATCH_NAMES)) +\
        ", TEXTFILES: " + str(TOTAL) + ", UNMATCHED: " + str(UNMATCHED))

#WAIT = input("Press ENTER to end this program.")
