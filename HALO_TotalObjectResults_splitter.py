#!/usr/bin/env python3

"""
Copyright 2024 The Regents of the University of Colorado

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

Title:      HALO_TotalObjectResults_splitter
Summary:    Reverse the merging process and split merge data
            by sample name and/or MSI coordinates

DOI:        https://doi.org/10.5281/zenodo.4741394
URL:        https://github.com/christianrickert/CU-HIMSR/

Description:

This script can be used to split merged Total_Object_Results.csv files
from Indica Labs' HALO and re-merge them into separate comma-separated
value files using a specific pattern (regular expression) to consolidate
the exported files.
For performance reasons, there is no validation of the number of columns
or order of column labels - the header and lines are written as-is, so
make sure to only split/re-merge compatible data.
Create an import folder (or have the script create one for you) at the
current location and place the TOTAL_Object_Results.csv into there.
The output will be written into only into an empyt (needs to be empty)
export folder.
"""

#  imports

import fnmatch
import io
import os
import re
import sys

#  functions


def get_files(path="", pat="*", anti="", recurse=False):
    """Iterate through all files in a directory structure and
       return a list of matching files.

    Keyword arguments:
    path -- the path to a directory containing files (default "")
    pat -- string pattern that needs to be part of the file name (default "None")
    anti -- string pattern that may not be part of the file name (default "None")
    recurse -- boolen that allows the function to work recursively (default "False")
    """
    FILES = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file = os.path.join(root, file)
            if fnmatch.fnmatch(file, pat) and not fnmatch.fnmatch(file, anti):
                FILES.append(file)
        if not recurse:
            break  # from `os.walk()`
    return FILES


def get_image_name(line="", pattern=""):
    """Uses a regular expression search to match a pattern against a text.

    Keyword arguments:
    line -- the line of text to find the pattern in
    pattern -- the regular expression used in the search
    """
    return re.search(pattern, line).group(1)


def unmerge_data(in_path="", out_path=""):
    """Imports data from a text file and writes out all columns on a per-file basis
    using the first column's data for labeling of individual export files."""
    with open(in_path, "r", encoding="utf-8-sig") as in_file:
        print('\tFOLDER: "' + out_path + '"', flush=True)
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        if os.listdir(out_path):
            print("OUTPUT PATH NOT EMPTY. EXITING.")
            sys.exit(0)
        out_file = io.StringIO("")
        header = in_file.readline()  # read and call `next()` on iterator
        for lines, in_line in enumerate(in_file, start=1):
            image_name = get_image_name(in_line, pattern=NAME_PATTERN)
            if image_name not in known_images:
                out_file.close()  # previous file
                out_file_path = os.path.abspath(
                    os.path.join(out_path, image_name + ".csv")
                )
                out_file = open(out_file_path, "a", encoding="utf-8")  # current file
                out_file.write(header)
                known_images.add(image_name)
            out_file.write(in_line)
        out_file.close()  # last file
        return (lines, len(known_images))


#  constants & variables

EXPORT_FOLDER = r".\export"
FILE_TARGET = "*Total_Object_Results.csv"
IMPORT_FOLDER = r".\import"
# NAME_PATTERN = re.compile(r"(\d{6}\s[\w#&\s\-_\.+]+)(?=_Scan)")  # Akoya Polaris
NAME_PATTERN = re.compile(r"\\([^\\]+?)\.[^\\.]+(?=" ")")  # generic
VERSION = "HALO_summaryfile_splitter 1.0 (2024-09-25)"

#  main program

print(VERSION)
print(os.linesep)
print("UNMERGING files in folder:")
print("-----------------------")
print('FILE: "' + FILE_TARGET + '"')
FILE_COUNT = 0

if not os.path.exists(EXPORT_FOLDER):
    os.mkdir(EXPORT_FOLDER)
if not os.path.exists(IMPORT_FOLDER):
    os.mkdir(IMPORT_FOLDER)

known_images = set()  # keep across multiple merge files
for index, file in enumerate(get_files(IMPORT_FOLDER, FILE_TARGET)):
    print("\tFILE: " + file)
    unmerged = unmerge_data(in_path=file, out_path=EXPORT_FOLDER)
    print("\tLINES: " + str(unmerged[0]), "MATCHES: " + str(unmerged[1]))
    FILE_COUNT += 1

print("FILES: " + str(FILE_COUNT))
print(os.linesep)


# WAIT = input("Press ENTER to exit this program.")
