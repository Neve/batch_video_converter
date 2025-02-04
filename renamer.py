#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  Version 0.0.1
  A script to rename movie files using defined pattern
  
  Usage:
  Run  - targeting the mkv file or mkv dir

"""

import sys
from lib import helper as Pathlib
import os
from os import path


def rename_files(file_list):
  for movie_file_path in file_list:
    print(f" original name is {movie_file_path} \n")
    movie_filename_full = os.path.basename(movie_file_path) # movie_file.2004.mp4
    movie_filename = os.path.splitext(movie_filename_full)[0]
    print(f"  DEBUG: The mp4 file full :\n    {movie_filename_full}")
    print(f"  DEBUG: The mp4 file name:\n    {movie_filename}")

    words = movie_filename.split('.')
    for word in words:
      

    # white_spacing = movie_filename.replace('.',' ')
    # print(f"  DEBUG: The mp4 file name:\n    {white_spacing}")

# The main part
def main():
  script_invocation_arguments = sys.argv
  print(f"invoked with {script_invocation_arguments}")
  path_to_convert = Pathlib.get_movie_path(script_invocation_arguments[1], 'rename')
  movie_list =      Pathlib.get_movie_list(path_to_convert,['.mp4'])
  Pathlib.get_user_grant_to_run()
  rename_files(movie_list)



if __name__ == '__main__':
  main()