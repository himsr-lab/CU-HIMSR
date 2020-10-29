#!/usr/bin/env python3

"""
    Name:       phenoptrReports_memory_fix
    Version:    1.0 (2020-10-28)
    Author:     Christian Rickert
    Group:      Human Immune Monitoring Shared Resource (HIMSR)
                University of Colorado, Anschutz Medical Campus
    Comment:    Reverse the merging process and split merge data
                by channel (folder) and slide-ID (file).
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

def unmerge_data(in_path='/home/user/', out_path='/home/user'):
    """ Imports data from a text file and writes out all columns on a per-file basis
        using the first column's data for labeling of individual export files. """
    slides = 0
    with open(in_path, 'r') as in_file:
        base = os.path.basename(in_path)
        channel = base.split(" ")[0]
        if not channel:
            channel = "Unk"
        folder = out_path + os.path.sep + channel
        println("\tFOLDER: \"" + folder + "\"")
        if not os.path.exists(folder):
            os.mkdir(folder)
        name = os.path.splitext(base)[0].replace("Merge_cell_seg_data ", "")
        current_slide = ""
        previous_slide = ""
        file_data = []
        println("\t\tSLIDES:")

        for in_index, in_line in enumerate(in_file):
            if in_index == 0: # header
                header = in_line
            elif in_index == 1:
                data = in_line.split("\t")
                current_slide = data[1][0:-7]  # first slide name
                println("\t\t\t\t\"" + current_slide + "\"")
                previous_slide = current_slide
            else: # data
                data = in_line.split("\t")
                current_slide = data[1][0:-7]  # new slide name
                if current_slide != previous_slide:  # slide changed
                    with open(folder + os.path.sep +\
                              name + " - " + previous_slide + ".txt", 'a') as out_file:
                        for _out_index, out_line in enumerate(file_data):
                            out_file.write(out_line)

                    println("\t\t\t\t\"" + current_slide + "\"")
                    file_data = []
                    file_data.append(header)
                    previous_slide = current_slide
                    slides += 1
                else:
                    file_data.append(in_line)

        # write last slide before opening a new file
        with open(folder + os.path.sep + name + " - " + previous_slide + ".txt", 'a') as out_file:
            for _out_index, out_line in enumerate(file_data):
                out_file.write(out_line)

    return slides

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
    SLIDE_COUNT = 0
    println("\tFILE: \"" + file + "\"")
    SLIDE_COUNT += unmerge_data(in_path=file, out_path=EXPORT_FOLDER)
    FILE_COUNT += 1
    println("\tSLIDES: " + str(SLIDE_COUNT))

print("UNMERGED FILES: " + str(FILE_COUNT) + ".")
println(os.linesep)


WAIT = input("Press ENTER to end this program.")
