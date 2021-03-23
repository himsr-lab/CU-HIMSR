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

Title:      phenoptrreports_mergefile_splitter
Summary:    Reverse the merging process and split merge data
            by channel (folder) and sample name (file)

URL:        https://github.com/christianrickert/CU-HIMSR/

Description:

We split merge files into individual files by using the sample name
(without coordinates) as a reference. Unmerged files can then be
re-merged and consolidated separately in order to avoid
prohibitive peak memory usage by phenoptrReports.
Please organize your data in the following file system structure:

/import/
    ./Channel_A Merge_cell_seg_data.txt
    ./Channel_B Merge_cell_seg_data.txt
    ./Channel_C Merge_cell_seg_data.txt

The single space between the channel label and the merge file is
used to sort the output files into their corresponding folders:

/export/
    ./Channel_A/
        ./Merge_cell_seg_data - *.txt
    ./Channel_B/
        ./Merge_cell_seg_data - *.txt
    ./Channel_C/
        ./Merge_cell_seg_data - *.txt

The header lines are preserved for each of the unmerged files.
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
                if fileobject.is_file() and pattern in fileobject.name:  # match pattern
                    files.append(fileobject.path)
                elif recursive and fileobject.is_dir():
                    files.append( \
                        get_files(path=fileobject.path, pattern=pattern, recursive=recursive))
    return flatten(files)

def println(string=""):
    """ Prints a string and forces immediate output. """
    print(string)
    sys.stdout.flush()

def unmerge_data(in_path='/home/user/', out_path='/home/user'):
    """ Imports data from a text file and writes out all columns on a per-file basis
        using the first column's data for labeling of individual export files. """
    with open(in_path, 'r') as in_file:
        channel, name = os.path.splitext(os.path.basename(in_path))[0].split(" ")
        if not channel:
            channel = "NA"
        folder = out_path + os.path.sep + channel
        println("\tFOLDER: \"" + folder + "\"")
        if not os.path.exists(folder):
            os.mkdir(folder)
        println("\t\tSAMPLES:")

        for in_index, in_line in enumerate(in_file):
            if in_index == 0:  # header
                file_data = []
                header = in_line
                file_data.append(header)
                current_sample = ""
                previous_sample = ""
            else:  # data
                current_sample = in_line.split("\t")[1].split("_")[0]  # without coordinates
                if current_sample != previous_sample and previous_sample:  # sample changed
                    with open(folder + os.path.sep +\
                              name + " - " + previous_sample + ".txt", 'a') as out_file:
                        for _out_index, out_line in enumerate(file_data):
                            out_file.write(out_line)
                    println("\t\t\t\t\"" + current_sample + "\"")  # prepare next sample
                    file_data = []
                    file_data.append(header)
                previous_sample = current_sample
                file_data.append(in_line)

        # write last sample before opening a new input file
        with open(folder + os.path.sep + name + " - " + previous_sample + ".txt", 'a') as out_file:
            for _out_index, out_line in enumerate(file_data):
                out_file.write(out_line)

#  constants & variables

EXPORT_FOLDER = r".\export"
FILE_TARGET = "Merge_cell_seg_data.txt"
IMPORT_FOLDER = r".\import"
VERSION = "phenoptrreports_mergefile_splitter 1.0 (2021-03-22)"

#  main program

println(VERSION)
println(os.linesep)
println("UNMERGING files in folder:")
println("-----------------------")
println("FILE: \"*" + FILE_TARGET + "\"")
FILE_COUNT = 0

if not os.path.exists(EXPORT_FOLDER):
    os.mkdir(EXPORT_FOLDER)

for file in get_files(IMPORT_FOLDER, FILE_TARGET):
    println("\tNAME: \"" + file + "\"")
    unmerge_data(in_path=file, out_path=EXPORT_FOLDER)
    FILE_COUNT += 1

print("UNMERGED FILES: " + str(FILE_COUNT) + ".")
println(os.linesep)


WAIT = input("Press ENTER to exit this program.")
