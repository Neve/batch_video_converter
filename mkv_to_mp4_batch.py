#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  Version 1.0.2
  A script to convert or transcode movie files

  ffmpeg downloaded from https://ffmpeg.org/download.html#build-mac 
  
  Usage:
  Run  - targeting the mkv file or mkv dir
  /{PATH}/mkv_to_mp4_batch.py '/{PATH}/video.mkv'
  /{PATH}/mkv_to_mp4_batch.py '/PATH TO DIR WITH .mkv'
"""

import time
import sys
import os
from os import path


import subprocess
import concurrent.futures
from lib import helper as Pathlib

def ffmpeg_home():
    """simple ffmpeg path wrapper for future re-use"""
    ffmpeg_bin_path = os.path.join(path.dirname(__file__), 'ffmpeg/bin/')
    return ffmpeg_bin_path

# This method intended to resolve subtitle problem,
# ffmpeg could just copy subs - as is: -c:s copy
#              or move it: -c:s move_text
# sometimes move_text do not work properly, in this case its better to use 'copy'
# lets ask user and put right value into ffmpeg run cmd
def ask_user_about_sub_convert_type():
    """A method is intended to resolve subtitle conversion problem"""

    copy = 'copy'
    mov_text = 'mov_text'
    auto_detect = 'auto'
    msg = """  INFO: ffmpeg could just copy subs - as is: '-c:s copy' or move it: '-c:s move_text'.
      Sometimes, because of unsupported (subrip) subtitles type in mkv container, 'copy' method may not work properly  - (Fail with: 'codec frame size is not set'),
      In this case its better to use 'move_text' which is slower and sometimes corrupts subs names
      Enter:
        1 - for copy
        2 - for mov_text
        a - converter will detect if there is (subrip) subs and use 'move_text' for selected movies
      """

    print(msg)
    user_input = input(f"  Please confirm (1 - {copy} / 2- {mov_text} / a - {auto_detect}) [a]: ")

    if user_input == '2':
        return mov_text

    if user_input == '1':
        return copy

    if user_input == 'a' or not user_input:
        return auto_detect

    print("  ERROR: Wrong input. Please enter 1 or 2 or 'a' ")
    sys.exit()

# Ask user if we want convert or transcode. In most cases its possible to do conversion.
# Which is slightly faster and less resource demanding then transcode
def ask_user_convert_or_transcode():
    """Ask user if we want convert or transcode."""

    msg = """  INFO: ffmpeg could Convert from one Container (MKV,MPV,MOV etc. ) to another
      if Video Stream is encoded  with the same video codec, usually MPEG. for example: .MKV->.MP4, .MOV-> .MP4
      Or ffmpeg could Transcode (with h264) - decoding MPEG and encoding with h264

      NOTE: Transcoding reduces the file size, but takes significantly more time (Good for screen recordings)

      Please select what we will do. Default would be to Convert, since its faster
        1 - for covert
        2 - for transcode
    """

    print(msg)
    convert = '1'
    transcode = '2'
    user_input = input(f"  Please select( Convert {convert}/ Transcode {transcode}) [{convert}]: ")

    if user_input == '1' or not user_input:
        return True

    if user_input == '2':
        return False

    print(f"  ERROR: Wrong input({user_input}). Please enter 1 or 2  ")
    sys.exit()


def rename_mkv_file_to_mp4(mkv_movie_path):
    """ Renaming .mkv to .mp4
        mkv_movie_path - string with a path to mkv movie
        return : string with a path to mp4 movie """

    mp4 = os.path.splitext(mkv_movie_path)[0]+".mp4"
    # print(f"  DEBUG: The mp4 file full path:\n    {mp4}")
    return mp4


def delete_zero_sized_mp4_present(mp4_movie_path):
    """ method to delete zero sized mp4
        files from previous unsuccessful attempts"""

    if path.exists(mp4_movie_path) and path.getsize(mp4_movie_path) == 0:
        print(f"  WARNING: we have found empty {mp4_movie_path} file.")
        print("  WARNING: Removing before conversion.")
        os.remove(mp4_movie_path)

# Autodecting subtitle type for given mkv movie
# running: ffmpeg -i /path_to_the_.mkv
# looking for "" Subtitle: subrip" markers in output,
# if we have found any  - using move_text instead of copy
def detect_srt_subrip_subtitles(ffmpeg_bin_path, mkv_path, thread_counter):
    """Autodecting subtitle type for given mkv movie"""

    mkv_path = f"\"{mkv_path}\""
    movie_data = subprocess.getoutput(f"{ffmpeg_bin_path}ffprobe {mkv_path} ")
    print(f"  Thread {thread_counter} INFO:  RUNNING {ffmpeg_bin_path}ffprobe {mkv_path} ")
    # print (f"  DEBUG: {movie_data} \n ")
    subrip_subs = "'subrip' subtitles type detected! 'mov_text' option will be used"
    copy_option_note = "  NOTE: Doesn't contain 'subrip' subtitles, 'copy' option will be used"
    if movie_data.find('subrip') != -1:
        print(f"  Thread {thread_counter} INFO:    {subrip_subs}")
        return True
    print(f"  Thread {thread_counter} INFO:\n    {mkv_path} \n   {copy_option_note}")
    return False



# Actual ffmpeg convert sequence
# mkv_movie_path - string with a path to mkv movie
# return : null (executes ffmpeg cmd)
def ffmpeg_convert(
        ffmpeg_bin_path,
        mkv_movie_path,
        c_s_sub_convert_type,
        mp4_full_path,
        thread_counter = 0):
    """Converter method"""

    if mkv_movie_path == '':
        print(f"  Thread {thread_counter} INFO: Movie path is empty! exit!")
        sys.exit()

    print(f"  Thread {thread_counter} INFO: {mkv_movie_path} All set! Ready to Rock!")

    # Autodetection srt presence if auto_detect option given
    if c_s_sub_convert_type == 'auto':
        if detect_srt_subrip_subtitles(ffmpeg_bin_path, mkv_movie_path, thread_counter):
            sub_convert_type = 'mov_text -ignore_unknown'
        else:
            sub_convert_type = 'copy -ignore_unknown'
    else:
        sub_convert_type   = c_s_sub_convert_type

    cmd_options = [
        f"{ffmpeg_bin_path}ffmpeg -i ",
        f"\"{mkv_movie_path}\"",
        ' -map 0 -c copy -c:s ',
        sub_convert_type,
        f" \"{mp4_full_path}\""
    ]
    cmd = ''.join(cmd_options)
    print(f"  Thread {thread_counter} INFO: Executing: \n    {cmd} \n\n")

    movie_data = subprocess.getoutput(cmd)
    print(f"  Thread {thread_counter} INFO: Output: \n {movie_data} \n")


# Very similar converter of MOV files to mp4
# A Wrapper for  ffmpeg -i ~/file.mov -vcodec h264 -acodec mp2 ~/file.mp4
def ffmpeg_transcode(ffmpeg_bin_path, mov_movie_path, mp4_full_path, thread_counter = 0):
    """Transcoder method"""

    if mov_movie_path == '':
        print(f"  Thread {thread_counter} INFO: Movie path is empty! exit!")
        sys.exit()

    print(f"  Thread {thread_counter} INFO: {mov_movie_path} - All set! Ready to Rock!")

    cmd_options = [
      f"{ffmpeg_bin_path}ffmpeg -i ",
      f"\"{mov_movie_path}\"",
      ' -vcodec h264 -acodec mp2',
      ' ',
      f"\"{mp4_full_path}\""
    ]
    cmd = ''.join(cmd_options)
    print(f"  Thread {thread_counter} INFO: Executing: \n    {cmd} \n\n")


    movie_data = subprocess.getoutput(cmd)
    print(f"  Thread {thread_counter} INFO: Output: \n {movie_data} \n")



def convert_with_threads(ffmpeg_bin_path, mkv_movies, do_convert, thread_worker_number):
    """ Initializing threads """
    thread_count = 0

    # Current approach 1 thread per movie, which could hurt you cpu ))
    # Creating a number of threads equal to number of movies found
    # mkv_number = int(mkv_movies.count)
    # 21 - kills mbp 2021
    with concurrent.futures.ThreadPoolExecutor(max_workers = thread_worker_number) as executor:
        print(f"  INFO: The Thread worker number is: {thread_worker_number}")
        # we need to ask user about subs conversion  only once
        if do_convert:
            user_subtitle_convert_type = ask_user_about_sub_convert_type()

        # Processing the list
        for movie_file in mkv_movies:
            mp4_movie_name = rename_mkv_file_to_mp4(movie_file)
            delete_zero_sized_mp4_present(mp4_movie_name)
            if do_convert:
                executor.submit(ffmpeg_convert,
                                  ffmpeg_bin_path,
                                  movie_file,
                                  user_subtitle_convert_type,
                                  mp4_movie_name,
                                  thread_count)
            else:
                executor.submit(ffmpeg_transcode,
                                  ffmpeg_bin_path,
                                  movie_file,
                                  mp4_movie_name,
                                  thread_count)
            thread_count+=1


def main():
    """The main part"""
    start_time = time.time()
    thread_workers_max = 4
    ffmpeg_bin_path = ffmpeg_home()
    script_invocation_arguments = sys.argv
    path_to_convert = Pathlib.get_movie_path(script_invocation_arguments[1], 'convert')
    mkv_movie_list =  Pathlib.get_movie_list(path_to_convert,['.mkv','.mov'])
    Pathlib.get_user_grant_to_run()
    do_convert = ask_user_convert_or_transcode()

    convert_with_threads(ffmpeg_bin_path, mkv_movie_list, do_convert, thread_workers_max)

    elapsed_time = time.time() - start_time
    print(f"  INFO: Conversion time: {elapsed_time}")


    if __name__ == '__main__':
        main()




# ISSUE 1: Add HW accelerated encoding
# For hardware accelerated video encoding on macOS use:
# Format 	Encoder
# H.264 	-c:v h264_videotoolbox
# HEVC/H.265 	-c:v hevc_videotoolbox

# Example:

# ffmpeg -i input.mov -c:v h264_videotoolbox output.mp4

#  For options specific to these encoders see
#      ffmpeg -h encoder=h264_videotoolbox
#  and ffmpeg -h encoder=hevc_videotoolbox.

#  These encoders do not support -crf so you must use -b:v to set the bitrate, such as -b:v 6000k.

# Duration: 01:45:04.77, start: 0.000000, bitrate: 18744 kb/s
# Stream #0:0(eng): Video: hevc (Main 10), yuv420p10le(tv, bt2020nc/bt2020/smpte2084), /n
# 3840x2160 [SAR 1:1 DAR 16:9], 23.98 fps, 23.98 tbr, 1k tbn, 23.98 tbc (default)

# ISSUE 2: Test dynamic workers number
# ISSUE 3:  Add automatic run, no CMD entries
