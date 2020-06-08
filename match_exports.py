#!/usr/bin/env python3

"""
    Removes unmatched regions in phenoptrReports exports
    Version:    1.1 (2020-06-07)
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
println("EXPORT: \"" + EXPORT_FOLDER.rsplit('\\', 1)[1] + "\"\n")
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
println(os.linesep)

# count unique file names in batch folders across channels
println("Counting unique file names (2/6):")
println("---------------------------------")
FILES = 0
BATCH_FILE_COUNTS = {}  # file counts by batch
for batch in BATCHES:
    println("BATCH: \"" + batch + "\"")

    FILE_COUNTS = {}  # file counts by channel
    for channel in CHANNELS:
        println("\tCHANNEL: \"" + channel + "\"")

        for fileobject in get_files(os.path.join(EXPORT_FOLDER, channel, batch), ".txt"):
            file = fileobject.rsplit('\\', 1)[1]
            if file in FILE_COUNTS:
                FILE_COUNTS[file] += 1  # increment key value
            else:  # file not in list
                FILE_COUNTS[file] = 1  # add key: value pair
            FILES += 1

    BATCH_FILE_COUNTS[batch] = FILE_COUNTS
print(BATCH_FILE_COUNTS)
println(os.linesep)

# move files to a subfolder, if they don't exist in batch folders across channels
println("Moving unmatched files to folder (3/6):")
println("---------------------------------------")
UNMATCHED = 0
CHANNEL_COUNT = len(CHANNELS)
for channel in CHANNELS:
    println("CHANNEL: \"" + channel + "\"")

    for batch in BATCHES:
        println("\tBATCH: \"" + batch + "\"")

        for file, counts in BATCH_FILE_COUNTS[batch].items():
            if counts < CHANNEL_COUNT:  # file does not exist in all batch folders
                # cwd_path = os.path.join(EXPORT_FOLDER, channel, batch)
                # tmp_path = os.path.join(cwd_path + os.sep + "unmatched")
                # if not os.path.exists(tmp_path):
                #     os.mkdir(tmp_path)
                # try:
                #     shutil.move(os.path.join(cwd_path, file), os.path.join(tmp_path, file))
                #     UNMATCHED += 1  # only count moved files
                # except FileNotFoundError:
                #     pass
                pass

println("CHANNELS: " + str(CHANNELS) + ", BATCHES: " + str(len(BATCHES)) +\
        ", TEXTFILES: " + str(FILES) + ", UNMATCHED: " + str(UNMATCHED))
println(os.linesep)

# count lines numbers in unique file names in batch folders across channels
println("Checking line numbers in unique files (4/6):")
println("--------------------------------------------")
BATCH_FILE_MINS = {}  # file line (minimum) counts by batch
BATCH_CHANNEL_FILE_LINES = {}  # file line (actual) counts by batch and channel
for batch in BATCHES:
    println("BATCH: \"" + batch + "\"")

    CHANNEL_FILE_LINES = {}  # file line (absolute) by channel
    for channel in CHANNELS:
        println("\tCHANNEL: \"" + channel + "\"")


        FILE_MINS = {}  # file line (minimum) count within channel
        FILE_LINES = {}  # file line (absolute) count within channel
        for fileobject in get_files(os.path.join(EXPORT_FOLDER, channel, batch), ".txt"):
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
        CHANNEL_FILE_LINES[channel] = FILE_LINES
   
    BATCH_FILE_MINS[batch] = FILE_MINS
    BATCH_CHANNEL_FILE_LINES[batch] = CHANNEL_FILE_LINES

BATCH_CHANNEL_FILE = {}  # these files need to be checked
for batch in BATCHES:

    for channel in CHANNELS:

        for file, lines in BATCH_CHANNEL_FILE_LINES[batch][channel].items():
            if lines > BATCH_FILE_MINS[batch][file]:
                BATCH_CHANNEL_FILE[batch] = {channel: file}

println(os.linesep)
print(BATCH_CHANNEL_FILE)

# Remove duplicate lines in unique file names in batch folders across channels
println("Removing duplicate lines in unique files (5/6):")
println("-----------------------------------------------")
for batch, channel_file in BATCH_CHANNEL_FILE.items():

    for channel, file in channel_file.items():
        fileobject = os.path.join(EXPORT_FOLDER, channel, batch, file)
        with open(fileobject, newline='') as csvfile:

            reader = csv.DictReader(csvfile, delimiter='\t')
            id_set = set()  # create an empty set (unique entries only)
            id_list = []  # create an empty list (duplicates possible)

            for row in reader:
                id_value = row['Cell ID']
                id_set.add(id_value)
                id_list.append(id_value)
            if len(id_set) < len(id_list):
                print("duplicate entry in: " + channel + ": " + batch + ": "+ file + ": ")
'''

for batch in BATCHES:

    for channel in CHANNELS:


        print(BATCH_FILE_LINES[batch][channel])

# rewrite files to their consensus line entries across all batch folders
println("Removing unmatched lines in files (6/6):")
println("----------------------------------------")



BATCH_FILE_LINES = {}  # file line counts by batch and channel
for batch in BATCHES:
    #println("BATCH: \"" + batch + "\"")

    file_lines = {}  # file line counts by channel
    for channel in CHANNELS:
        #println("\tCHANNEL: \"" + channel + "\"")


        for fileobject in get_files(os.path.join(EXPORT_FOLDER, channel, batch), ".txt"):
            file = fileobject.rsplit('\\', 1)[1]

            lines = 0
            with open(file, 'r') as textfile:
                for lines, line in enumerate(textfile):
                    lines = lines

                lines += 1
            file_lines[file] = lines

        BATCH_FILE_LINES[batch] = file_lines

print(BATCH_FILE_LINES)
println(os.linesep)

# rewrite files to their consensus line entries across all batch folders
println("Removing unmatched entries in files (5/5):")
println("------------------------------------------")

# find mimimum line entries for each file (file) in each batch folder
BATCH = {}  # minimum file line counts by channel
for channel in CHANNELS:  # get minimum line counts for all files first
    
    file_mins = {}  # minimum file line counts by batch
    for batch in BATCHES:

        for file, lines in BATCHS[batch].items():
            try:
                file_mins[file] = lines if lines < file_mins[file] else file_mins[file]
            except KeyError:  # first file, does not exist yet
                file_mins[file] = lines

        BATCH[batch] = file_mins
print(BATCH)
# find the files that contain more lines than the minimum line entries found
UNEVEN = 0
batch_file_minfile = {}  # csv data for minimum line entry files
batch_file_maxfile = {}  # csv data for maximum line entry files
for channel in CHANNELS:  # now that we know the minimum line counts, let's compare file contents
    #println("CHANNEL: \"" + channel + "\"")
    #print(channel)
    for batch in BATCHES:
        #println("\tBATCH: \"" + batch + "\"")

        #print(batch)
        for file, lines in BATCHS[batch].items():
            #if BATCHS[batch][file] > BATCH[batch][file]:
            print(BATCHS[batch][file], BATCH[batch][file])
#             if BATCHS[batch][file] > BATCH[batch][file]:
#                 batch_file_maxfile[batch] = textfile
#                 cwd_path = os.path.join(EXPORT_FOLDER, channel, batch)
#                 tmp_path = os.path.join(cwd_path + os.sep + "uneven")
#                 if not os.path.exists(tmp_path):
#                     os.mkdir(tmp_path)
#                 shutil.copy(os.path.join(cwd_path, file), os.path.join(tmp_path, file))
#             else:  # BATCHS[batch][file] <= BATCH[batch][file]
#                 batch_file_minfile[batch] = textfile
# UNEVEN = len(batch_file_maxfile)
# print(batch_file_minfile)
# print(batch_file_maxfile)
# print(UNEVEN)
        #     print(file)
        # for file, lines in BATCHS[batch].items():
        #     if lines == BATCH[batch][file]:  # file line counts are different between batch folders
        #         print("Found in:" + batch + ", File: " + file)
        #         cwd_path = os.path.join(EXPORT_FOLDER, channel, batch)
        #         tmp_path = os.path.join(cwd_path + os.sep + "uneven")
        #         if not os.path.exists(tmp_path):
        #             os.mkdir(tmp_path)
        #         shutil.copy(os.path.join(cwd_path, file), os.path.join(tmp_path, file))
        #         UNEVEN += 1
            
#println(os.linesep)

#WAIT = input("Press ENTER to end this program.")
'''