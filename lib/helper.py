#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  Version 0.0.1
  Library helper, contains common methods for working with files and paths.

  Usage:
  from lib import helper as Pathlib
"""

import sys
import os
from os import path




# Ensure we have legit and accessible path target
# detect if it is a directory
# Detecting if user provided us with the path to a dir
# or to the specific file or just running in directory with movies
# do_action[String] - an argument to display action type, convert or rename
def get_movie_path(file_path, do_action):
    """Ensure we have legit and accessible path target"""

    # User defined path where mkvs reside
    if len(file_path) == 1:
        print("  WARNING: No path given as argument! will try to search in current directory")
        path_to_convert = path.dirname(__file__)
    else:
        path_to_convert = file_path

    # User could pass either a single file or directory
    # Checking that the path exists and it is a directory
    if path.exists(path_to_convert):
        if path.isdir(path_to_convert):
            print(f"  INFO: We will {do_action} in: {path_to_convert} Directory")
        else:
            print(f"  INFO: We will {do_action} {path_to_convert} File")
    else:
        print(f"  FATAL: {path_to_convert} Either do not exist or we have no permissions there")
        sys.exit()
    return path_to_convert

# Method forms the list of movies
# which which needs to be converted.
# path_to_convert - system path to directory or single file
# returns movie_list - list with movies to convert
def get_movie_list(path_to_convert,extensions):
    """ A Method to form the list of movies """

    # A List w mkv movies found in given directory
    movie_list = []

    # Adding to array only if it is mkv or mov file
    if path.isfile(path_to_convert) and path_to_convert.endswith(tuple(extensions)):
        movie_list.append(path_to_convert)

    # processing directory path, by walking through and adding files to movie_list array
    # os.walk works only with directories, passing files as argument returns nothing. Not optimal
    for root, directory, files in os.walk(path_to_convert):
        for file in files:
            # if file.endswith(".mkv") or file.endswith(".mov"):
            if file.endswith(tuple(extensions)):
                # Full path to mkv
                mkv_full_path = os.path.join(root, file)
                # appending to main list
                movie_list.append(mkv_full_path)
            else:
                print(f"  WARNING: Given File {file} is not supported by converter {directory}")

    if movie_list:
        print("  INFO: Script will convert following movies")
        for file_name in movie_list:
            print(f"  {file_name} \n")
        return movie_list
    print("  FATAL: The movie list is empty. Something went wrong with the file list. Terminating.")
    sys.exit()

def get_user_grant_to_run():
    """Get user confirm on the list of converted movies"""
    no_answer = 'n'
    yes_answer = 'y'
    user_input = input(f"  Please confirm ({yes_answer}/{no_answer}) [{yes_answer}]: ")

    if user_input.lower() == yes_answer or not user_input:
        print("  INFO: Confirmed. Ready to start...")
    elif user_input.lower() == no_answer:
        print('  EXIT: Terminating ...')
        sys.exit()
    else:
        print("  ERROR: Wrong argument. Please enter 'y' or 'n'. Exit. Try again please")
        sys.exit()
