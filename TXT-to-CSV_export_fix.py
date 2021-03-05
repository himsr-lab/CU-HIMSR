#!/usr/bin/env python3

"""
Copyright 2021 Regents of the University of Colorado

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

Title:      TXT-to-CSV_export_fix
Summary:    Removes non-numeric columns from inForm exports
            in preparation for a CSV-to-FCS export
Version:    1.0 (2021-03-05)

URL:        https://github.com/christianrickert/CU-HIMSR/

Description:

TODO
"""

#  imports

import math
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

def matching_columns(patterns='', numbers=''):
    """ Returns a list of column indices found in both the patterns list
        as well as the list of columns with numerical content """
    column = [(pattern and numerical) for pattern, numerical in zip(patterns, numbers)]
    return column

def matching_numbers(string='', nans=None):
    """ Checks if a string is numerical and returns the boolean value """
    number = False
    try:
        math.isnan(float(string))  # cast string to float and check for Python NaN
        number = True
    except ValueError:
        if string in nans:  # valid NaN
            number = True
    return number

def matching_patterns(patterns=None, antipatterns=None, string=''):
    """ Returns the matching status for a string string using
        lists of patterns and antipatterns. """
    pattern = bool(True in [(pattern in string) for pattern in patterns] and \
                 not True in [(antipattern in string) for antipattern in antipatterns])
    return pattern

def get_column_indices(path='', delimiter='', patterns=None, antipatterns=None, nans=None):
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

    patterns = [matching_patterns(patterns, antipatterns, header) for header in headers]
    numbers = [matching_numbers(datum, nans) for datum in data]

    for index, column in enumerate(matching_columns(patterns, numbers)):
        if column:
            indices.append(index)

    return indices

def txt_to_csv(in_path='', delimiter_in='', out_path='', delimiter_out='', indices=None, nans=None):
    """ Imports data from an inForm csv file and writes out all columns that contain
        numerical data and match a pattern, while not matching the antipattern. """
    columns = len(indices)
    count = 0
    if columns > 0:
        with open(in_path, 'r') as in_file:
            base = os.path.basename(in_path)
            name = os.path.splitext(base)[0]
            nan = "NaN"
            out_array = ["", delimiter_out] * columns  # preallocate to minimize memory overhead
            out_array[-1] = "\n"  # carriage return
            with open(out_path + os.path.sep + name + ".csv", 'w') as out_file:

                for count, line in enumerate(in_file):
                    column = -2  # export column index

                    for index, data in enumerate(line.split(delimiter_in)):
                        if index in indices:  # numerical data or nan
                            column += 2
                            if count == 0:  # fix header issues
                                out_array[column] = data.replace(delimiter_out, "")
                            else:
                                if data in nans:  # replace with default value
                                    data = nan
                                out_array[column] = data

                    out_file.write("".join(out_array))
    return count

#  constants & variables

DELIMITER_IN = "\t"  # tabulator-separated
DELIMITER_OUT = ","  # comma-separated
HEADER_INCLUDE = [""]  # include all with list of empty string: [""]
HEADER_EXLCUDE = []  # exclude none with empty list: []
IMPORT_FOLDER = r".\import"
EXPORT_FOLDER = r".\export"
FILE_TARGET = "_cell_seg_data.txt"
NANS = ["NA", "NaN", "N/A", "#N/A"]  # valid not-a-number strings

#  main program

println(os.linesep)
println("Preparing files for export:")
println("---------------------------")
println("FILE: \"*" + FILE_TARGET + "\"")
FILE_COUNT = 0

if not os.path.exists(EXPORT_FOLDER):
    os.mkdir(EXPORT_FOLDER)

for file in get_files(IMPORT_FOLDER, FILE_TARGET):
    println("\tNAME: \"" + file)
    column_indices = get_column_indices(path=file, delimiter=DELIMITER_IN, \
                                        patterns=HEADER_INCLUDE, antipatterns=HEADER_EXLCUDE, \
                                        nans=NANS)
    println("\t\tCOLUMNS: " + str(len(column_indices)))
    line_count = txt_to_csv(in_path=file, delimiter_in=DELIMITER_IN, \
                            out_path=EXPORT_FOLDER, delimiter_out=DELIMITER_OUT, \
                            indices=column_indices, nans=NANS)
    println("\t\tLINES: " + str(line_count))
    FILE_COUNT += 1

print("PREPARED FILES: " + str(FILE_COUNT) + ".")
println(os.linesep)


WAIT = input("Press ENTER to exit this program.")
