#!/usr/bin/env python3

"""
    Name:       phenoptrReports_memory_fix
    Version:    1.0 (2020-10-23)
    Author:     Christian Rickert
    Group:      Human Immune Monitoring Shared Resource (HIMSR)
                University of Colorado, Anschutz Medical Campus
    Comment:    Reverse the merging process and split files
                into separate per-slide data
"""


#  imports

import os
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

def println(string=""):
    """ Prints a string and forces immediate output. """
    print(string)
    sys.stdout.flush()

def unmerge_data(in_path='/home/user/', out_path='export'):
    """ Imports data from a text file and writes out all columns on a per-file basis
        using the first column's data for labeling of individual export files. """
    labels = 0

    with open(in_path, 'r') as in_file:
        base = os.path.basename(file)
        name = os.path.splitext(base)[0]
        previous_label = ""

        for index, line in enumerate(in_file):
            if index == 0: # header
                headers = line
            else: # data
                # "Merge_cell_seg_data" needs to be removed from the file name
                # "Scan1_[1,1]_cell_seg_data.txt" needs to be the end of the file name
                current_label = line.split("\t")[1].split("_")[0]  # sample name

                with open(out_path + os.path.sep + name + " - " + current_label + ".txt", 'a') as out_file:
                    if current_label != previous_label:
                        out_file.write(headers)
                        previous_label = current_label
                        labels += 1
                    out_file.write(line)

    return labels

#  constants & variables

# IMPORT_FOLDER = r".\import"
# EXPORT_FOLDER = r".\export"
IMPORT_FOLDER = r"C:\Users\TEMP-USER\Desktop\Chris (2020-10-23)"
EXPORT_FOLDER = IMPORT_FOLDER + os.path.sep + r"unmerged"
FILE_TARGET = "Merge_cell_seg_data.txt"

# The folder structure, i.e. the name of the channel and batch folders needs to be
# consistent across the project.

println(os.linesep)
println("UNMERGING files in folder:")
println("-----------------------")
println("MATCH: \"*" + FILE_TARGET + "\"")
FILE_COUNT = 0

if not os.path.exists(EXPORT_FOLDER):
    os.mkdir(EXPORT_FOLDER)

for file in get_files(IMPORT_FOLDER, FILE_TARGET):
    LABEL_COUNT = 0
    println("\tFILE: \"" + file)
    LABEL_COUNT += unmerge_data(in_path=file, out_path=EXPORT_FOLDER)
    FILE_COUNT += 1
    print("\tLABELS: " + str(LABEL_COUNT))

print("UNMERGED FILES: " + str(FILE_COUNT) + ".")
println(os.linesep)


WAIT = input("Press ENTER to end this program.")
