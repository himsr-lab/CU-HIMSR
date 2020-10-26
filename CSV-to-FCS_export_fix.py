#!/usr/bin/env python3

"""
    Name:       CSV-to-FCS_export_fix
    Version:    1.0 (2020-08-31)
    Author:     Christian Rickert
    Group:      Human Immune Monitoring Shared Resource (HIMSR)
                University of Colorado, Anschutz Medical Campus
    Comment:    Removes non-numeric data from inForm export data
                and reverses the consolidation process
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

def get_column_indices(path='/home/user/'):
    """ Returns the indices of columns containing numerical data in a file. """
    indices = []
    with open(path, 'r') as textfile:

        for line, content in enumerate(textfile):
            if line == 1:  # ignore header
                data = content.split("\t")
            elif line > 1:  # stop iteration
                break

    for index, chunk in enumerate(data):
        try:
            float(chunk)
            indices.append(index)
        except ValueError:  # not a number
            pass

    return indices

def get_column_headers(in_path='/home/user/', indices=None):
    """ Returns a list containing the column headers for the indices specified. """
    headers = []
    with open(in_path, 'r') as textfile:

        for line, content in enumerate(textfile):
            if line == 0:  # header only
                chunks = content.split("\t")
            elif line > 0:  # stop iteration
                break

    for index, chunk in enumerate(chunks):  # populate list with header entries
        if index in indices:
            headers.append(chunk)

    return headers

def fix_csv_data(in_path='/home/user/', out_path='export', indices=None, headers=None):
    """ Imports data from an inForm csv file and writes out all columns that contain
        numerical data ony: non-numerical data is discarded. Furthermore, data is
        exported on a per-file basis using the first column's data for labeling. """
    with open(in_path, 'r') as in_file:
        base = os.path.basename(file)
        name = os.path.splitext(base)[0]
        previous_id = ""

        for line, content in enumerate(in_file):
            chunks = content.split("\t")
            entries = []

            for index, chunk in enumerate(chunks):  # populate list with numerical entries
                if index in indices:
                    entries.append(chunk)

            length = len(entries)
            current_id = chunks[0]

            with open(out_path + os.path.sep + name + " - " + current_id + ".csv", 'a') as out_file:
                if current_id != previous_id:

                    for index, header in enumerate(headers):
                        out_file.write(header)
                        if index < (length - 1):
                            out_file.write("\t")  # tab separation
                        else:
                            out_file.write("\n")  # end of line

                    previous_id = current_id

                for index, entry in enumerate(entries):
                    out_file.write(entry)
                    if index < (length - 1):
                        out_file.write("\t")
                    else:
                        out_file.write("\n")

#  constants & variables

# IMPORT_FOLDER = r".\import"
IMPORT_FOLDER = r"C:\Users\himsr\Desktop\Chris\test data\csv-fix"
EXPORT_FOLDER = IMPORT_FOLDER + os.path.sep + r"csv"
# FILE_TARGET = "_cell_seg_data.txt"
FILE_TARGET = "Consolidated_data.txt"

# The folder structure, i.e. the name of the channel and batch folders needs to be
# consistent across the project.

println(os.linesep)
println("Fixing files in folder:")
println("-----------------------")
println("FILE: \"*" + FILE_TARGET + "\"")
FILE_COUNT = 0

if not os.path.exists(EXPORT_FOLDER):
    os.mkdir(EXPORT_FOLDER)

for file in get_files(IMPORT_FOLDER, FILE_TARGET):
    println("\tFILE: \"" + file)
    indices = get_column_indices(file)
    headers = get_column_headers(file, indices)
    fix_csv_data(in_path=file, out_path=EXPORT_FOLDER, indices=indices, headers=headers)
    FILE_COUNT += 1

print("FIXED FILES: " + str(FILE_COUNT) + ".")
println(os.linesep)


WAIT = input("Press ENTER to end this program.")
