#!/usr/bin/env python3

"""
    Name:       TXT-to-CSV_export_fix
    Version:    1.0 (2021-03-01)
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

def matching_columns(matches='', numbers=''):
    """ Returns a list of column indices found in both the matches list
        as well as the list of columns with numerical content """
    match = [(match and numerical) for match, numerical in zip(matches, numbers)]
    return match

def matching_number(string=''):
    """ Checks if a string is numerical and returns the boolean value """
    try:
        float(string)  # cast string to float
        return True
    except ValueError:
        return False

def matching_pattern(patterns=None, antipatterns=None, string=''):
    """ Returns the matching status for a string string using
        lists of patterns and antipatterns. """
    match = bool(True in [(pattern in string) for pattern in patterns] and \
                 not True in [(antipattern in string) for antipattern in antipatterns])
    return match

def get_column_indices(path='', delimiter='', patterns=None, antipatterns=None):
    """ Returns the indices of columns in a single line of a file containing numerical data. """
    indices = []
    with open(path, 'r') as textfile:

        for line_index, line in enumerate(textfile):
            if line_index == 0:  # read header for pattern matching
                headers = line.split(delimiter)
            elif line_index == 1:  # read data to check for numerical input
                data = line.split(delimiter)
            elif line_index > 1:  # stop iteration afterwards
                break

    matches = [matching_pattern(patterns, antipatterns, header) for header in headers]
    numbers = [matching_number(datum) for datum in data]

    for index, valid in enumerate(matching_columns(matches, numbers)):
        if valid:
            indices.append(index)

    return indices

def txt_to_csv(in_path='', delimiter_in='', out_path='', delimiter_out=',', indices=None):
    """ Imports data from an inForm csv file and writes out all columns that contain
        numerical data and match a pattern, while not matching the antipattern. """
    with open(in_path, 'r') as in_file:
        base = os.path.basename(in_path)
        name = os.path.splitext(base)[0]
        with open(out_path + os.path.sep + name + ".csv", 'w') as out_file:
            count = 0
            last_index = indices[-1]

            for count, line in enumerate(in_file):
                out_array = []  # avoid immutable strings to improve performance

                for index, data in enumerate(line.split(delimiter_in)):
                    if index in indices:  # numerical data
                        out_array.append(data)
                        if index < last_index:  # line incomplete, add tabulator
                            out_array.append(delimiter_out)
                        else:  # line complete, add line feed and write line
                            out_array.append("\n")
                            out_file.write("".join(out_array))
                            break  # proceed to next line

    return count

#  constants & variables

DELIMITER_IN = "\t"  # tabulator-separated
DELIMITER_OUT = ","  # comma-separated
HEADER_INCLUDE = [""]  # include all with list of empty string: [""]
HEADER_EXLCUDE = []  # exclude none with empty list: []
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
    column_indices = get_column_indices(path=file, delimiter=DELIMITER_IN, \
                                        patterns=HEADER_INCLUDE, antipatterns=HEADER_EXLCUDE)
    println("\t\tCOLUMNS: " + str(len(column_indices)))
    line_count = txt_to_csv(in_path=file, delimiter_in=DELIMITER_IN, \
                            out_path=EXPORT_FOLDER, delimiter_out=DELIMITER_OUT, \
                            indices=column_indices)
    println("\t\tLINES: " + str(line_count))
    FILE_COUNT += 1

print("PREPARED FILES: " + str(FILE_COUNT) + ".")
println(os.linesep)


WAIT = input("Press ENTER to end this program.")
