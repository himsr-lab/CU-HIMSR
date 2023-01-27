#!/usr/bin/env python3

"""
Copyright 2023 The Regents of the University of Colorado

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

Title:      write_tileconfig
Summary:    Write pixel coordinates from TIFFs to a TileConfig.txt for
            stitching with Fiji's "Grid/Collection stitching" plugin.

DOI:        https://doi.org/10.5281/zenodo.4741394
URL:        https://github.com/christianrickert/CU-HIMSR/

Description:

Please install the latest version of Christoph Gohlke's "tifffile" module
with "conda" ("conda install tifffile") or "pip" ("pip install tifffile").
Image data must be two-dimensional (no Z-stacks), but may contain multiple
pages - corresponding to multiple channels per acquisition.
The TIFF metadata is required for retrieving [X,Y] positions and resolutions.
Place all image data that you want to stitch in the same folder and place
this folder in the same location as the script. Alternatively, add multiple
folder paths (to be stitched separately) to the 'FOLDERS' list.
In the "Grid/Collection stitching" plugin, please choose the "Positions from
file" (Type) and "Defined by TileConfiguration" (Order) in the first dialog.
In the second dialog, you should only "Compute the overlap" if applicable,
otherwise the plugin will throw an exception.

See: https://imagej.net/plugins/image-stitching
"""


# imports
import os
import sys
import tifffile as tifff


# functions
def flatten(deep_list=None):
    """Flatten a nested list of lists and typles and return a single list.
    Keyword arguments:
    deep_list -- a nested list of lists and tuples
    """
    flat_list = []
    for item in deep_list:
        if isinstance(item, (list, tuple)):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


def get_files(path="", pats=None, antis=None, recurse=False):
    """Iterate through all files in a folder structure and
    return a list of matching files.
    Keyword arguments:
    path -- the path to a folder containing files (default "")
    patterns -- list of strings where one of the strings needs to be
                part of the file name (default "None")
    antipattern -- list of strings where none of the strings may be
                   part of the file name (default "None")
    recurse -- boolen that allows the function to recurse through
               the folder path (default "False")
    """
    files = []
    realpath = os.path.realpath(path)
    with os.scandir(realpath) as fileobject_iterator:
        for fileobject in fileobject_iterator:
            if not os.path.islink(fileobject.path):
                if fileobject.is_file() and matching_patterns(
                    pats=pats, antis=antis, string=fileobject.name
                ):
                    files.append(fileobject.path)
                elif recurse and fileobject.is_dir():
                    files.append(
                        get_files(
                            path=fileobject.path,
                            pats=pats,
                            antis=antis,
                            recurse=recurse,
                        )
                    )
    return flatten(files)


def get_folders(path="", pats=None, antis=None, recurse=False):
    """Iterate through a folder structure and return a list of matching folders.
    Keyword arguments:
    path -- the path to a folder containing folders (default "")
    patterns -- list of strings where one of the strings needs to be
                part of the folder name (default "None")
    antipattern -- list of strings where none of the strings may be
                   part of the folder name (default "None")
    recurse -- boolen that allows the function to recurse through
               the folder path (default "False")
    """
    folders = []
    realpath = os.path.realpath(path)
    with os.scandir(realpath) as fileobject_iterator:
        for fileobject in fileobject_iterator:
            if not os.path.islink(fileobject.path):
                if fileobject.is_dir():
                    if matching_patterns(
                        pats=pats, antis=antis, string=fileobject.name
                    ):
                        folders.append(fileobject.path)
                    elif recurse:
                        folders.append(
                            get_folders(
                                path=fileobject.path,
                                pats=pats,
                                antis=antis,
                                recurse=recurse,
                            )
                        )
    return flatten(folders)


def get_grid_layout(coordinates=None):
    """Sort a list of coordinates and return a tuple of set-like coordinate lists.
    The two lists will denote the X and Y coordinates for each grid column and row.
    coordinates -- the list with one or more coordinates (default "None")
    """
    sorted_set_locations = []
    for index in range(0, 2):  # create a list of X and Y coordinates
        locations_list = [coordinate[index] for coordinate in coordinates]
        locations_set = []
        _ = [
            locations_set.append(location)
            for location in locations_list
            if location not in locations_set
        ]  # prepare set with unique X or Y coordinates
        sorted_set_locations.append(sorted(locations_set))  # sort, slow
    return sorted_set_locations[0], sorted_set_locations[1]  # columns, rows


def get_tiff_pix(tiff=None):
    """Read a TiffFile object and return its dimensions as a (X,Y) tuple.
        X and Y are returned as int.
    Keyword arguments:
    tiff -- the TiffFile object (default None)
    """
    # get image dimensions [ ]
    x_pix = int(tiff.pages[0].tags["ImageWidth"].value)
    y_pix = int(tiff.pages[0].tags["ImageLength"].value)
    return (x_pix, y_pix)


def get_tiff_pos(tiff=None, unit=""):
    """Read a TiffFile object and return its position values as a (X,Y,unit) tuple.
        X and Y are returned as float, unit is returned as str.
    Keyword arguments:
    tiff -- the TiffFile object (default None)
    unit -- the TIFF's resolution unit as string (default "")
    """
    # get image positions [px, inch, cm]
    x_pos = float(
        tiff.pages[0].tags["XPosition"].value[0]
        / tiff.pages[0].tags["XPosition"].value[1]
    )
    y_pos = float(
        tiff.pages[0].tags["YPosition"].value[0]
        / tiff.pages[0].tags["YPosition"].value[1]
    )
    # convert unit from [inch] to [cm]
    if unit == "inch":
        x_pos *= IN_CM
        y_pos *= IN_CM
        unit = "cm"
    return (x_pos, y_pos, unit)


def get_tiff_res(tiff=None, unit=""):
    """Read a TiffFile object and return its resolution values as a (X,Y,unit) tuple.
        X and Y are returned as float, unit is returned as str.
    Keyword arguments:
    tiff -- the TiffFile object (default None)
    unit -- the TIFF's resolution unit as string (default "")
    """
    # get image resolutions [1, 1/inch, 1/cm]
    x_res = float(
        tiff.pages[0].tags["XResolution"].value[0]
        / tiff.pages[0].tags["XResolution"].value[1]
    )
    y_res = float(
        tiff.pages[0].tags["YResolution"].value[0]
        / tiff.pages[0].tags["YResolution"].value[1]
    )
    # convert unit to [cm]
    if unit == "inch":
        x_res *= IN_CM
        y_res *= IN_CM
        unit = "cm"
    return (x_res, y_res, unit)


def get_tiff_unit(tiff=None):
    """Read a TiffFile object and return its resolution unit as string.
    Keyword arguments:
    tiff -- the TiffFile object (default None)
    """
    unit = str(tiff.pages[0].tags["ResolutionUnit"].value).lower()
    if unit.endswith("centimeter"):
        return "cm"
    if unit.endswith("inch"):
        return "inch"
    return "px"


def matching_patterns(pats=None, antis=None, string=""):
    """Check for matching patterns and for non-matching antipatterns and
       return a match boolean.
    Keyword arguments:
    pats -- list of strings that need to be part of
            the input string (default None)
    antis -- list of strings that may not to be part of
             the input string (default None)
    string -- input string to look for matching patterns and
              non-matching antipatterns (default "")
    """
    match = bool(
        True in [(pattern in string) for pattern in pats]
        and not (True in [(antipattern in string) for antipattern in antis])
    )
    return match


def println(string=""):
    """Prints a string and forces immediate output.
    Keyword arguments:
    string -- string to be printed (default None)
    """
    sys.stdout.write(string + LINESEP)
    sys.stdout.flush()


# variables
FILE_TARGET = ".tif"  # file search pattern
FOLDER = os.path.abspath(os.getcwd())  # working directory
IN_CM = 2.54  # inch to centimeter
INVERT_Y_AXIS = False  # MIBIscope
LINESEP = "\n"  # newline character
OFFSETS = [0, 0]  # pixel offsets for tile locations
OUTPUT = "TileConfiguration.txt"  # name of output file
VERSION = "write_tileconfig 0.9 (2023-01-14)"


#  main program
println(os.linesep)
println(VERSION)
for folder in get_folders(path=FOLDER, pats=[""], antis=[], recurse=False):
    println(LINESEP + f"FOLDER: {folder}")

    # prepare list of files
    FILES = []
    for file in get_files(path=folder, pats=[FILE_TARGET], antis=[], recurse=False):
        FILES.append(file)

    # write tile configuration file
    with open(
        os.path.abspath(folder + os.sep + OUTPUT),
        "w",
        encoding="utf-8",
    ) as file_out:
        # write image dimensions
        file_out.write(
            "# Define the number of dimensions we are working on"
            + LINESEP
            + "dim = 2"
            + LINESEP
        )
        # write script variables
        file_out.write(
            f"# Inversion:\t{INVERT_Y_AXIS}"
            + LINESEP
            + f"# Offsets:\t\tX={OFFSETS[0]}, Y={OFFSETS[1]}"
            + LINESEP
        )
        # determine image locations
        locations = []
        file_out.write("# Define the image coordinates (in pixels)" + LINESEP)
        for file in FILES:
            name = os.path.basename(file)
            println(LINESEP + f"\tFILE: {name}")
            with tifff.TiffFile(file) as tif:
                UNIT = get_tiff_unit(tif)  # [px, inch, cm]
                resolutions = get_tiff_res(tif, UNIT)  # [px, cm]
                x, y, u = get_tiff_pos(tif, UNIT)  # [px, cm]
                location = (
                    round(resolutions[0] * float(x)),
                    round(resolutions[1] * float(y)),
                )  # [px]
                locations.append(location)
                println(
                    f"\t\tRES = {resolutions[0]},{resolutions[1]} (1/{u})"
                    + LINESEP
                    + f"\t\tPOS = [{x},{y}] ({u})"
                    + LINESEP
                    + f"\t\tLOC = [{locations[-1][0]},{locations[-1][1]}] (px)"
                )
        # determine row and column coordinates
        columns, rows = get_grid_layout(locations)
        # adjust coordinate system upon request
        if INVERT_Y_AXIS:
            y_max = max(rows)
            locations = [
                (location_x, -(location_y - y_max))
                for location_x, location_y in locations
            ]
            rows = [-(row - y_max) for row in rows]
            OFFSETS[1] = -OFFSETS[1]
        # write image locations from corrected image coordinates
        for idx, file in enumerate(FILES):
            location_x = locations[idx][0]
            location_y = locations[idx][1]
            file_out.write(
                os.path.basename(file)
                + "; ; ("
                + str(float(location_x + OFFSETS[0] * columns.index(location_x)))
                + ", "
                + str(float(location_y + OFFSETS[1] * rows.index(location_y)))
                + ")"
                + LINESEP
            )
