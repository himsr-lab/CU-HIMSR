#!/usr/bin/env python3

"""
    Name:       TXT-to-CSV_export_fix
    Version:    1.0 (2021-01-14)
    Author:     Christian Rickert
    Group:      Human Immune Monitoring Shared Resource (HIMSR)
                University of Colorado, Anschutz Medical Campus
    Comment:    Removes non-numeric columns from inForm exports
                in preparation for a CSV-to-FCS export
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

def get_column_indices(path='/home/user/'):
    """ Returns the indices of columns in a single line of a file containing numerical data. """
    indices = []
    with open(path, 'r') as textfile:

        for line_index, line in enumerate(textfile):
            if line_index == 1:  # second line olny, ignore header
                columns = line.split("\t")
            elif line_index > 1:  # stop iteration
                break

    for index, column in enumerate(columns):  # check for columns with numerical data
        try:
            float(column)
            indices.append(index)
        except ValueError:  # not a number
            pass

    return indices

def txt_to_csv(in_path='/home/user/', out_path='export', indices=None):
    """ Imports data from an inForm csv file and writes out all columns that contain
        numerical data: columns with non-numerical data are discarded. """
    with open(in_path, 'r') as in_file:
        base = os.path.basename(in_path)
        name = os.path.splitext(base)[0]
        with open(out_path + os.path.sep + name + ".csv", 'w') as out_file:
            count = 0
            last_index = indices[-1]

            for count, line in enumerate(in_file):
                out_array = []  # avoid immutable strings to improve performance

                for index, data in enumerate(line.split("\t")):
                    if index in indices:  # numerical data
                        out_array.append(data)
                        if index < last_index:  # line incomplete, add tabulator
                            out_array.append("\t")
                        else:  # line complete, add line feed and write line
                            out_array.append("\n")
                            out_file.write("".join(out_array))
                            break  # proceed to next line

    return count

#  constants & variables

IMPORT_FOLDER = r".\import"
EXPORT_FOLDER = r".\export"
FILE_TARGET = "_cell_seg_data.txt"

#  main program

println(os.linesep)
println("Preparing files for export:")
println("---------------------------")
println("FILE: \"*" + FILE_TARGET + "\"")
FILE_COUNT = 0

if not os.path.exists(EXPORT_FOLDER):
    os.mkdir(EXPORT_FOLDER)

for file in get_files(IMPORT_FOLDER, FILE_TARGET):
    println("\tFILE: \"" + file)
    column_indices = get_column_indices(file)
    println("\t\tCOLUMNS: " + str(len(column_indices)))
    line_count = txt_to_csv(in_path=file, out_path=EXPORT_FOLDER, indices=column_indices)
    println("\t\tLINES: " + str(line_count))
    FILE_COUNT += 1

print("PREPARED FILES: " + str(FILE_COUNT) + ".")
println(os.linesep)


WAIT = input("Press ENTER to end this program.")
