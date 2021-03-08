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

Title:      phenoptrreports_mergefile_splitter
Summary:    Reverse the merging process and split merge data
            by channel (folder) and slide-ID (file)
Version:    1.0 (2021-03-08)

URL:        https://github.com/christianrickert/CU-HIMSR/

Description:

We split merge files into individual files by using the sample name
(slide ID, first column) as a reference. Unmerged files can then be
merged and consolidated separately in order to avoid prohibitive
peak memory usage by phenoptrReports.
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
        channel = os.path.basename(in_path).split(" ")[0]
        if not channel:
            channel = "Unk"
        folder = out_path + os.path.sep + channel
        println("\tFOLDER: \"" + folder + "\"")
        if not os.path.exists(folder):
            os.mkdir(folder)
        name = os.path.splitext(os.path.basename(in_path))[0].replace("Merge_cell_seg_data ", "")
        println("\t\tSLIDES:")

        for in_index, in_line in enumerate(in_file):
            if in_index == 0:  # header
                file_data = []
                header = in_line
                file_data.append(header)
                current_slide = ""
                previous_slide = ""
            else:  # data
                current_slide = in_line.split("\t")[1][0:-7]
                if current_slide != previous_slide and previous_slide:  # slide changed
                    with open(folder + os.path.sep +\
                              name + " - " + previous_slide + ".txt", 'a') as out_file:
                        for _out_index, out_line in enumerate(file_data):
                            out_file.write(out_line)
                    println("\t\t\t\t\"" + current_slide + "\"")  # prepare next slide
                    file_data = []
                    file_data.append(header)
                previous_slide = current_slide
                file_data.append(in_line)

        # write last slide before opening a new input file
        with open(folder + os.path.sep + name + " - " + previous_slide + ".txt", 'a') as out_file:
            for _out_index, out_line in enumerate(file_data):
                out_file.write(out_line)

#  constants & variables

IMPORT_FOLDER = r".\import"
EXPORT_FOLDER = r".\export"
FILE_TARGET = "Merge_cell_seg_data.txt"

# The folder structure, i.e. the name of the channel and batch folders needs to be
# consistent across the project.

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
