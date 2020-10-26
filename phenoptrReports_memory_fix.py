#!/usr/bin/env python3

"""
    Name:       phenoptrReports_memory_fix
    Version:    1.0 (2020-10-23)
    Author:     Christian Rickert
    Group:      Human Immune Monitoring Shared Resource (HIMSR)
                University of Colorado, Anschutz Medical Campus
    Comment:    Reverse the merging process and split files
                by slide-ID (file) and channel (folder)
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
        base = os.path.basename(in_file)
        name = os.path.splitext(base)[0].replace("Merge_cell_seg_data ", "")
        previous_folder = ""  # channel
        previous_file = ""  # slide

        for index, line in enumerate(in_file):
            if index == 0: # header
                header = line
                columns = header.split("\t")
            else: # data
                current_folder = out_path + os.path.sep + columns[3][0:-1]
                current_file = columns[1].replace(".qptiff", "")  # sample name

                if current_folder != previous_folder:  # channel changed
                    if not os.path.exists(current_folder):
                        os.mkdir(current_folder)
                    previous_folder = current_folder

                with open(current_folder + os.path.sep + name + " - " + current_file + ".txt", 'a') as out_file:
                    if current_file != previous_file:  # slide changed
                        out_file.write(header)
                        previous_file = current_file
                        labels += 1
                    out_file.write(line)

    return labels

#  constants & variables

IMPORT_FOLDER = r".\import"
EXPORT_FOLDER = r".\export"
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
