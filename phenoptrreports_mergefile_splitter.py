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
            by sample name and/or MSI coordinates

DOI:        https://doi.org/10.5281/zenodo.4741394
URL:        https://github.com/christianrickert/CU-HIMSR/

Description:

We split merge files into individual files by using the sample name
and, upon request, also the sample's MSI coordinates.
Unmerged files can either be used to convert sets of samples/MSIs
into flow cytometry standard files or to re-merge and consolidate
smaller data subsets.
The header lines are preserved for each of the unmerged files.
"""

#  imports

import os
import sys

#  functions

def export_data(out_path='/home/user', out_data=None):
    """ Writes data from an array to a file. """
    with open(out_path, 'w') as out_file:
        for out_line in out_data:
            out_file.write(out_line)

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

def get_name_index(path='', delimiter='', name=None):
    """ Returns the column index with the sample/MSI name. """
    with open(path, 'r') as textfile:
        for line_index, line in enumerate(textfile):
            if line_index == 0:  # read header for pattern matching
                headers = line.split(delimiter)
            else:  # stop iteration afterwards
                break

    for index, column in enumerate(headers):
        if column == name:
            return index  # index found

    return float("nan")  # no index found

def println(string=""):
    """ Prints a string and forces immediate output. """
    print(string)
    sys.stdout.flush()

def unmerge_data(in_path='', index=0, by_msi=False, out_path=''):
    """ Imports data from a text file and writes out all columns on a per-file basis
        using the first column's data for labeling of individual export files. """
    with open(in_path, 'r') as in_file:
        name = os.path.splitext(os.path.basename(in_path))[0]
        println("\tFOLDER: \"" + out_path + "\"")
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        println("\t\tSAMPLES:")
        for in_index, in_line in enumerate(in_file):
            if in_index == 0:  # header
                file_data = []
                header = in_line
                file_data.append(header)
                current_sample = ""
                previous_sample = ""
            else:  # data
                current_sample = in_line.split("\t")[index].rsplit(sep=".", maxsplit=1)[0]
                if not by_msi:  # ignore MSI coordinates
                    current_sample = current_sample.rsplit(sep="_", maxsplit=1)[0]
                if current_sample != previous_sample:  # sample name or MSI coordinates changed
                    println("\t\t\t\t\"" + current_sample + "\"")
                    if previous_sample:  # save collected data
                        export_data(out_path=out_path + os.path.sep + name + \
                                             " - " + previous_sample + ".txt", out_data=file_data)
                    file_data = []  # prepare next sample
                    file_data.append(header)
                previous_sample = current_sample
                file_data.append(in_line)
        # write last sample before opening a new input file
        export_data(out_path=out_path + os.path.sep + name + \
                             " - " + previous_sample + ".txt", out_data=file_data)

#  constants & variables

EXPORT_FOLDER = r".\export"
FILE_TARGET = "Merge_cell_seg_data.txt"
IMPORT_FOLDER = r".\import"
SPLIT_BY_MSI = False  # split by name *and* MSI coordinates
VERSION = "phenoptrreports_mergefile_splitter 1.0 (2021-10-12)"

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
    name_index = get_name_index(path=file, delimiter='\t', name="Sample Name")
    unmerge_data(in_path=file, index=name_index, by_msi=SPLIT_BY_MSI, out_path=EXPORT_FOLDER)
    FILE_COUNT += 1

print("UNMERGED FILES: " + str(FILE_COUNT) + ".")
println(os.linesep)


WAIT = input("Press ENTER to exit this program.")
