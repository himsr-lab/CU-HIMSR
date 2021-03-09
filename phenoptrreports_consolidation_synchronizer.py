#!/usr/bin/env python3

"""
Copyright 2021 The Regents of the University of Colorado

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Author:     Christian Rickert <christian.rickert@cuanschutz.edu>
Group:      Human Immune Monitoring Shared Resource (HIMSR)
            University of Colorado, Anschutz Medical Campus

Title:      phenoptrreports_consolidation_synchronizer
Summary:    Removes unmatched regions (files) and cells (lines)
            from inForm export data and merge files.
Version:    1.0 (2021-03-08)

URL:        https://github.com/christianrickert/CU-HIMSR/

Description:

inForm's export data as well as the corresponding merge files
can contain individual cells (lines) that have been identified
by the segmentation algorithm in one channel, but might be missing
in other channels (folders). In this case, the consolidation fails
and phenoptrReports throws an error that the line counts do not
match. To work around this issue, we ensure that the export data
contains only files from consensus regions, i.e. files that are
present in all channel folders. In addition, we scan the merge
files for missing cell IDs and remove surplus lines from the merge
files of other channels, respectively.
Please organize your data in the following file system structure:

/export
    ./channel a
        ./batch 1
            ./*_cell_seg_data.txt
            ./Merge_cell_seg_data.txt
        ./batch 2
        ./batch 3
    ./channel b
        ./batch 1
            ./*_cell_seg_data.txt
            ./Merge_cell_seg_data.txt
        ./batch 2
        ./batch 3
    ./channel c
        ./batch 1
            ./*_cell_seg_data.txt
            ./Merge_cell_seg_data.txt
        ./batch 2
        ./batch 3
    ./Stroma (ignored)
    ./Tumor (ignored)

The top-most folders in the export folder are the channel folders,
which can have any name, but should not contain "Stroma" or "Tumor".
The folders contained in the channel folders need to be named
identical across channels, e.g. "batch" or "data" to be able to
identify consensus regions for different batches.
Both unmatched (non-consensus) channel files as well as unbalanced
merge files with surplus lines are moved into subfolders of their
corresponding batch folders.
"""

#  imports

import os
import shutil
import sys

#  functions

def flatten(deep_list=None):
    """ Returns a flattened list with elements from (deep) lists or tuples """
    flat_list = []
    for item in deep_list:
        if isinstance(item, (list, tuple)):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list

def get_cell_ids(path='/home/user/', length=None):
    """ Returns the cell IDs of a file as a list with given length. """
    with open(path, 'r') as par:
        match_ids = [0 for x in range(length)]
        try:
            for index, line in enumerate(par):
                match_ids[index] = line.split("\t")[4]
        except IndexError:
            pass
    return match_ids

def get_files(path='/home/user/', pattern='', recursive=False):
    """ Returns all files in path matching the pattern. """
    files = []
    realpath = os.path.realpath(path)
    with os.scandir(realpath) as fileobject_iterator:
        for fileobject in fileobject_iterator:
            if not os.path.islink(fileobject.path):
                if fileobject.is_file() and pattern in fileobject.name:  # match pattern
                    files.append(fileobject.path)
                elif recursive and fileobject.is_dir():
                    files.append( \
                        get_files(path=fileobject.path, pattern=pattern, recursive=recursive))
    return flatten(files)

def get_folders(path='/home/user/', pattern='', exclusions='', recursive=False):
    """ Returns all folders in path matching the pattern, but excluding the antipattern. """
    folders = []
    realpath = os.path.realpath(path)
    with os.scandir(realpath) as fileobject_iterator:
        for fileobject in fileobject_iterator:
            if not os.path.islink(fileobject.path):
                if fileobject.is_dir() and \
                bool(True not in [(antipattern in fileobject.name) for antipattern in exclusions]):
                    folders.append(fileobject.path)
                    if recursive:  # traverse into subfolder
                        folders.append(get_folders(path=fileobject.path, pattern=pattern, \
                                                   exclusions=exclusions, recursive=recursive))
    return flatten(folders)

def get_line_counts(path='/home/user/'):
    """ Returns the number of lines counted in a file. """
    with open(path, 'r') as text_file:
        count = 0

        for line, _content in enumerate(text_file):
            count = line

    count += 1
    return count

def println(string=""):
    """ Prints a string and forces immediate output. """
    print(string)
    sys.stdout.flush()

def sync_cell_ids(in_path='/home/user/', match_ids=None, out_path='/home/user/'):
    """ Synchronizes the lines of a file based on the list of cell IDs from a reference
        and writes the synchronized content to a file. Returns the number of removed lines. """
    with open(in_path, 'r') as in_file:  # non-synchronized file
        with open(out_path, 'w') as out_file:  # synchronized file
            offset = 0  #  offset to synced file, if lines were skipped

            for index, line in enumerate(in_file):
                try:
                    check_id = line.split("\t")[4]
                except IndexError:
                    pass  # empty line or list too short
                finally:
                    if check_id == match_ids[index - offset]:
                        out_file.write(line)
                    else:
                        offset += 1

    return offset

#  constants & variables

EXPORT_FOLDER = r".\export"
FILE_TARGET = "_cell_seg_data"  # data and summaries required for consolidation
FOLDER_EXCLUSION = ["Stroma", "Tumor"]  # exclude folders with scoring information
MERGE_FILE = "Merge_cell_seg_data.txt"
CHANNELS = []
BATCHES = []

# The folder structure, i.e. the name of the channel and batch folders needs to be
# consistent across the project.

println(os.linesep)
println("Retrieving folder lists (1/6):")
println("------------------------------")
println("EXPORT: \"" + EXPORT_FOLDER.rsplit('\\', 1)[1] + "\"")

for channel_folder in get_folders(EXPORT_FOLDER, '', FOLDER_EXCLUSION):
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

# We are expecting to find the same files matching the file target pattern, see below,
# in each of the channel and batch folders, respectively.

println("Counting matching file names (2/6):")
println("---------------------------------")
println("FILE: \"*" + FILE_TARGET + "*\"")
MATCHING_NAMES = 0
BATCH_FILE_COUNTS = {}  # file counts by batch
CHANNEL_COUNT = len(CHANNELS)

for batch in BATCHES:
    println("\tBATCH: \"" + batch + "\"")

    FILE_COUNTS = {}  # file counts by channel
    for channel in CHANNELS:
        println("\t\tCHANNEL: \"" + channel + "\"")

        for match in get_files(os.path.join(EXPORT_FOLDER, channel, batch), FILE_TARGET):
            file = match.rsplit('\\', 1)[1]
            if file in FILE_COUNTS:
                FILE_COUNTS[file] += 1  # increment key value
            else:  # file not in list
                FILE_COUNTS[file] = 1  # add key: value pair

    BATCH_FILE_COUNTS[batch] = FILE_COUNTS

    for file, counts in BATCH_FILE_COUNTS[batch].items():
        if counts == CHANNEL_COUNT:
            MATCHING_NAMES += 1

print("MATCHING NAMES: " + str(MATCHING_NAMES) + ".")
println(os.linesep)

# Files that match the pattern, but are not consistent across the folder structure,
# are moved into a subfolder within the batch folder of a given channnel.

println("Moving unmatched files to folder (3/6):")
println("---------------------------------------")
UNMATCHED_FILES = 0
FOLDER_TARGET = "unmatched"
println("FOLDER: \"" + FOLDER_TARGET + "\"")

for channel in CHANNELS:
    println("\tCHANNEL: \"" + channel + "\"")

    for batch in BATCHES:
        println("\t\tBATCH: \"" + batch + "\"")

        for file, counts in BATCH_FILE_COUNTS[batch].items():
            if counts < CHANNEL_COUNT:  # file does not exist in all batch folders
                mat_path = os.path.join(EXPORT_FOLDER, channel, batch)
                mat_file = os.path.join(mat_path, file)
                if os.path.exists(mat_file):
                    unm_path = os.path.join(mat_path + os.sep + FOLDER_TARGET)
                    if not os.path.exists(unm_path):
                        os.mkdir(unm_path)
                    try:
                        shutil.move(os.path.join(mat_path, file), os.path.join(unm_path, file))
                    except FileNotFoundError:
                        pass
                    else:  # success
                        print("\t\t\tFILE: \"" + os.path.join(mat_path, file) + "\"")
                        UNMATCHED_FILES += 1  # only count moved files

println("UNMATCHED FILES: " + str(UNMATCHED_FILES) + ".")
println(os.linesep)

# We are checking the merge files for the minimum number of lines present throughout batches and
# channels, respectively. Counting lines is faster than comparing lines.

println("Checking line counts in merge files (4/6):")
println("------------------------------------------")
FILE_TARGET = MERGE_FILE
println("FILE: \"*" + FILE_TARGET + "*\"")
CHECKED_FILES = 0
BATCH_FILE_MINS = {}  # file line (minimum) counts by batch
BATCH_CHANNEL_FILE_LINES = {}  # file line (actual) counts by batch and channel

for batch in BATCHES:
    println("\tBATCH: \"" + batch + "\"")

    FILE_MINS = {}  # file line (minimum) count by batch
    CHANNEL_FILE_LINES = {}  # file line (absolute) count by channel
    for channel in CHANNELS:
        println("\t\tCHANNEL: \"" + channel + "\"")

        FILE_LINES = {}  # file line (absolute) count within channel
        for match in get_files(os.path.join(EXPORT_FOLDER, channel, batch), FILE_TARGET):
            LINE_COUNT = 0
            file = match.rsplit('\\', 1)[1]
            LINE_COUNT = get_line_counts(match)
            FILE_LINES[file] = LINE_COUNT
            if file in FILE_MINS:
                FILE_MINS[file] = LINE_COUNT if LINE_COUNT < FILE_MINS[file] else FILE_MINS[file]
            else:  # file not in list
                FILE_MINS[file] = LINE_COUNT
            CHECKED_FILES += 1

        CHANNEL_FILE_LINES[channel] = FILE_LINES

    BATCH_FILE_MINS[batch] = FILE_MINS
    BATCH_CHANNEL_FILE_LINES[batch] = CHANNEL_FILE_LINES

print("CHECKED FILES: " + str(CHECKED_FILES) + ".")
println(os.linesep)

# We can now identify merge files which have more lines than the consensus (minimum) line count.
# Let's also backup those merge files in a subfolder within the batch folder of a given channnel.

println("Moving merge files with unbalanced lines to folder (5/6):")
println("---------------------------------------------------------")
UNBALANCED_FILES = 0
FOLDER_TARGET = "unbalanced"
println("FOLDER: \"" + FOLDER_TARGET + "\"")

for batch in BATCHES:
    println("\tBATCH: \"" + batch + "\"")

    for channel in CHANNELS:
        println("\t\tCHANNEL: \"" + channel + "\"")

        for file, lines in BATCH_CHANNEL_FILE_LINES[batch][channel].items():
            try:  # avoid exception, when unmatched files are not removed (test run)
                mins = BATCH_FILE_MINS[batch][file]
            except KeyError:
                pass
            if lines > mins:
                bal_path = os.path.join(EXPORT_FOLDER, channel, batch)
                unb_path = os.path.join(bal_path + os.sep + FOLDER_TARGET)
                if not os.path.exists(unb_path):
                    os.mkdir(unb_path)
                try:
                    shutil.move(os.path.join(bal_path, file), os.path.join(unb_path, file))
                except FileNotFoundError:
                    pass
                else:
                    print("\t\t\tFILE: \"" + os.path.join(bal_path, file) + "\"")
                    UNBALANCED_FILES += 1  # only count moved files

println("UNBALANCED FILES: " + str(UNBALANCED_FILES) + ".")
println(os.linesep)

# We can now remove surplus lines from the backup files by comparing their Cell IDs with the
# corresponding consensus Cell IDs. However, we only compare against a single reference file.

println("Removing unbalanced lines in merge files (6/6):")
println("------------------------------------------------")
UNBALANCED_LINES = 0
println("FOLDER: \"" + FOLDER_TARGET + "\"")

for batch in BATCHES:
    println("\tBATCH: \"" + batch + "\"")

    for channel in CHANNELS:
        println("\t\tCHANNEL: \"" + channel + "\"")

        # loop: get all files with unbalanced lines to fix
        for unb_file, unb_lines in BATCH_CHANNEL_FILE_LINES[batch][channel].items():
            try:  # avoid exception, when unmatched files are not removed (test run)
                bal_lines = BATCH_FILE_MINS[batch][unb_file]
            except KeyError:
                bal_lines = float("inf")
            REF_CHANNEL = ""
            REF_FILE = ""
            REF_LINES = 0
            if unb_lines > bal_lines:

                # loop: get the first reference file with paired lines to synchronize with
                for REF_CHANNEL, ref_file_lines in BATCH_CHANNEL_FILE_LINES[batch].items():

                    for REF_FILE, REF_LINES in ref_file_lines.items():
                        if REF_LINES == bal_lines:
                            break  # break out of the inner reference loop

                    if REF_LINES == bal_lines:  # redundant, but required to force second break
                        break  # break out of the outer reference loop

                # target for balanced file
                bal_path = os.path.join(EXPORT_FOLDER, channel, batch, unb_file)
                # reference for balanced file
                ref_path = os.path.join(EXPORT_FOLDER, REF_CHANNEL, batch, REF_FILE)
                # cell IDs to compare from reference
                cell_ids = get_cell_ids(path=ref_path, length=unb_lines)
                # source for unbalanced file
                unb_path = os.path.join(EXPORT_FOLDER, channel, batch, FOLDER_TARGET, unb_file)
                # remove unbalanced lines and write balanced file
                UNBALANCED_LINES += sync_cell_ids(in_path=unb_path, match_ids=cell_ids,
                                                  out_path=bal_path)
                print("\t\t\tFILE: \"" + bal_path + "\"")

println("UNBALANCED LINES: " + str(UNBALANCED_LINES) + ".")
println(os.linesep)

WAIT = input("Press ENTER to exit this program.")
