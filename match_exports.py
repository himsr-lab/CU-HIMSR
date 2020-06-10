#!/usr/bin/env python3

"""
    Removes unmatched regions in phenoptrReports exports
    Version:    1.1 (2020-06-09)
    Author:     Christian Rickert
    Group:      Human Immune Monitoring Shared Resource (HIMSR)
                University of Colorado, Anschutz Medical Campus
"""

#  imports

import csv
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
EXPORT_FOLDER = r"C:\Users\Christian Rickert\Desktop\export"
#EXPORT_FOLDER = r"C:\Users\Christian Rickert\Documents\GitHub\phenoptr-fixes\export"
#EXPORT_FOLDER = r"\\Micro-LS7.ucdenver.pvt\HI3-Microscope\Data\Vectra3\SentiBio\Panel  63-2 EXPORT"
CHANNELS = []
BATCHES = []

# retrieve unique channel and batch folder names
println(os.linesep)
println("Retrieving folder lists (1/6):")
println("------------------------------")
println("EXPORT: \"" + EXPORT_FOLDER.rsplit('\\', 1)[1] + "\"")
for channel_folder in get_folders(EXPORT_FOLDER):
    println("\tCHANNEL: \"" + channel_folder + "\"")
    channel = channel_folder.rsplit('\\', 1)[1]
    if channel not in CHANNELS:  # unique names only
        CHANNELS.append(channel) 

    for batch_folder in get_folders(channel_folder):
        batch = batch_folder.rsplit('\\', 1)[1]
        println("\t\tBATCH: \"" + batch + "\"")
        if batch not in BATCHES:  # unique names only
            BATCHES.append(batch)

CHANNELS.sort()
BATCHES.sort()
println("CHANNELS: " + str(len(CHANNELS)) + ", BATCHES: " + str(len(BATCHES)) + ".")
println(os.linesep)

# count unique file names in batch folders across channels
println("Counting unique file names (2/6):")
println("---------------------------------")
FILE_TARGET = "_seg_data.txt"
println("FILE: \"" + FILE_TARGET + "\"")
UNIQUE = 0
BATCH_FILE_COUNTS = {}  # file counts by batch
for batch in BATCHES:
    println("\tBATCH: \"" + batch + "\"")

    FILE_COUNTS = {}  # file counts by channel
    for channel in CHANNELS:
        println("\t\tCHANNEL: \"" + channel + "\"")

        for fileobject in get_files(os.path.join(EXPORT_FOLDER, channel, batch), FILE_TARGET):
            file = fileobject.rsplit('\\', 1)[1]
            if file in FILE_COUNTS:
                FILE_COUNTS[file] += 1  # increment key value
            else:  # file not in list
                FILE_COUNTS[file] = 1  # add key: value pair
            UNIQUE += 1

    BATCH_FILE_COUNTS[batch] = FILE_COUNTS
print("UNIQUE: " + str(UNIQUE) + ".")

println(os.linesep)

# move files to a subfolder, if they don't exist in batch folders across channels
println("Moving unmatched files to folder (3/6):")
println("---------------------------------------")
UNMATCHED = 0
CHANNEL_COUNT = len(CHANNELS)
FOLDER_TARGET = "unmatched"
println("FOLDER: \"" + FOLDER_TARGET + "\"")
for channel in CHANNELS:
    println("\tCHANNEL: \"" + channel + "\"")

    for batch in BATCHES:
        println("\t\tBATCH: \"" + batch + "\"")

        for file, counts in BATCH_FILE_COUNTS[batch].items():
            if counts < CHANNEL_COUNT:  # file does not exist in all batch folders
                cwd_path = os.path.join(EXPORT_FOLDER, channel, batch)
                unm_path = os.path.join(cwd_path + os.sep + FOLDER_TARGET)
                if not os.path.exists(unm_path):
                    os.mkdir(unm_path)
                try:
                    shutil.move(os.path.join(cwd_path, file), os.path.join(unm_path, file))
                    UNMATCHED += 1  # only count moved files
                except FileNotFoundError:
                    pass
                pass

println("UNMATCHED: " + str(UNMATCHED) + ".")
println(os.linesep)

# count lines numbers in unique file names in batch folders across channels
println("Checking line counts in unique files (4/6):")
println("-------------------------------------------")
CHECKED = 0
BATCH_FILE_MINS = {}  # file line (minimum) counts by batch
BATCH_CHANNEL_FILE_LINES = {}  # file line (actual) counts by batch and channel
println("FILE: \"" + FILE_TARGET + "\"")
for batch in BATCHES:
    println("\tBATCH: \"" + batch + "\"")

    CHANNEL_FILE_LINES = {}  # file line (absolute) count by channel
    for channel in CHANNELS:
        println("\t\tCHANNEL: \"" + channel + "\"")


        FILE_MINS = {}  # file line (minimum) count within channel
        FILE_LINES = {}  # file line (absolute) count within channel
        for fileobject in get_files(os.path.join(EXPORT_FOLDER, channel, batch), FILE_TARGET):
            file = fileobject.rsplit('\\', 1)[1]
            line_count = 0
            with open(fileobject, 'r') as textfile:

                for lines, line in enumerate(textfile):
                    line_count = lines
            
            line_count += 1 
            if file in FILE_MINS:
                FILE_MINS[file] = line_count if line_count < FILE_MINS[file] else FILE_MINS[file]
            else:  # file not in list
                FILE_MINS[file] = line_count
            FILE_LINES[file] = line_count
            CHECKED += 1
        CHANNEL_FILE_LINES[channel] = FILE_LINES
   
    BATCH_FILE_MINS[batch] = FILE_MINS
    BATCH_CHANNEL_FILE_LINES[batch] = CHANNEL_FILE_LINES
'''
BATCH_CHANNEL_PAIRED_DIFF = {}  # these file serve as a reference
BATCH_CHANNEL_UNPAIRED_DIFF = {}  # these files need to be checked
for batch in BATCHES:

    CHANNEL_PAIRED_DIFF = {}
    CHANNEL_UNPAIRED_DIFF = {}
    for channel in CHANNELS:

        PAIRED_DIFF = {}
        UNPAIRED_DIFF = {}
        for file, lines in BATCH_CHANNEL_FILE_LINES[batch][channel].items():

            diff = lines - BATCH_FILE_MINS[batch][file]
            if not diff :
                PAIRED_DIFF[file] = diff
            else:  # diff
                UNPAIRED_DIFF[file] = diff
            CHECKED += 1

        CHANNEL_PAIRED_DIFF[channel] = PAIRED_DIFF
        CHANNEL_UNPAIRED_DIFF[channel] = UNPAIRED_DIFF

    BATCH_CHANNEL_PAIRED_DIFF[batch] = CHANNEL_PAIRED_DIFF
    BATCH_CHANNEL_UNPAIRED_DIFF[batch] = CHANNEL_UNPAIRED_DIFF
'''
print("DONE.")
println(os.linesep)

# move files to a subfolder, if their line counts don't match in batch folders across channels
println("Moving files with unpaired lines to folder (5/6):")
println("-------------------------------------------------")
UNPAIRED = 0
FOLDER_TARGET = "unpaired"
println("FOLDER: \"" + FOLDER_TARGET + "\"")
for batch in BATCHES:
    println("\tBATCH: \"" + batch + "\"")

    for channel in CHANNELS:
        println("\t\tCHANNEL: \"" + channel + "\"")

        for file, lines in BATCH_CHANNEL_FILE_LINES[batch][channel].items():
            if lines > BATCH_FILE_MINS[batch][file]:
                cwd_path = os.path.join(EXPORT_FOLDER, channel, batch)
                unp_path = os.path.join(cwd_path + os.sep + FOLDER_TARGET)
                if not os.path.exists(unp_path):
                    os.mkdir(unp_path)
                try:
                    #shutil.move(os.path.join(cwd_path, unpaired_diff), os.path.join(unp_path, file))
                    UNPAIRED += 1  # only count moved files
                except FileNotFoundError:
                    pass
println("UNPAIRED: " + str(UNPAIRED) + ".")
println(os.linesep)

# Compare unique cell IDs and remove unpaired lines
println("Removing unpaired lines in unique files (6/6):")
println("----------------------------------------------")
REMOVED = 0
FOLDER_TARGET = "unpaired"
println("FOLDER: \"" + FOLDER_TARGET + "\"")

for batch in BATCHES:
    println("\tBATCH: \"" + batch + "\"")

    for channel in CHANNELS:
        println("\t\tCHANNEL: \"" + channel + "\"")

        for file, lines in BATCH_CHANNEL_FILE_LINES[batch][channel].items():
            if lines > BATCH_FILE_MINS[batch][file]:
                
                for temp_channel, temp_file_lines in BATCH_CHANNEL_FILE_LINES[batch].items():

                    for temp_file, temp_lines in temp_file_lines.items():

                        if lines == BATCH_FILE_MINS[batch][temp_file]:
                            par_channel = temp_channel
                            print(par_channel)
                            break

                    break

                with open(os.path.join(EXPORT_FOLDER, par_channel, batch, file), 'r') as par:  # reference file
                    par_ids = [0 for x in range(BATCH_CHANNEL_FILE_LINES[batch][unp_channel][unp_file])]  # contains cell IDs
                    for index, line in enumerate(par):
                        par_ids[index] = line.split("\t")[4]

                with open(os.path.join(EXPORT_FOLDER, unp_channel, batch, FOLDER_TARGET, unp_file), 'r') as unp:  # unpaired file
                    print(os.path.join(EXPORT_FOLDER, unp_channel, batch, FOLDER_TARGET, unp_file))
                    with open(os.path.join(EXPORT_FOLDER, unp_channel, batch, unp_file), 'w') as fix:  # fixed file
                        print(os.path.join(EXPORT_FOLDER, unp_channel, batch, unp_file))
                        offset = 0  #  offset for fixed file, if lines were ignored
                        for index, line in enumerate(unp):
                            try:
                                unp_id = line.split("\t")[4]
                            except IndexError:  # empty line
                                pass
                            if unp_id == par_ids[index + offset]:
                                fix.write(line)
                            else:
                                REMOVED += 1
                                offset = -REMOVED

println("REMOVED: " + str(REMOVED) + ".")
println(os.linesep)


WAIT = input("Press ENTER to end this program.")
