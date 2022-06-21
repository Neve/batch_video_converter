#!/usr/bin/env python3
"""
  Set home ffmpeg dir  in  ffmpeg_home():
  and run targeting mkv file
  /{PATH}/mkv_to_mp4_batch.py '/{PATH}/video.mkv'
  or mkv dir
  /{PATH}/mkv_to_mp4_batch.py '/{PATH TO DIR WITH .mkv}'
"""
# -*- coding: utf-8 -*-
import sys
import os
from os import path
import subprocess
import concurrent.futures
import time



# simple ffmpeg path wapper for future re-use
def ffmpeg_home():
  ffmpeg_bin_path = "/Users/nst/Applications/ffmpeg/bin/"
  return ffmpeg_bin_path

# Ensure we have legit and acessible path target
# detect if it is a ditectory
# Detecting if user provided us with the path to a dir
# or to the specific file or just running in directory with movies
def get_movie_path(invocation_arguments):
  # User deffined path where mkvs reside
  if len(invocation_arguments) == 1:
    print("  WARNING: No path given as arument! will try to search in current directory")
    path_to_convert = path.dirname(__file__)
  else:
    path_to_convert = invocation_arguments[1]

  # User could pass either a single file or directory
  # Checking that the path exists and it is a directory
  if path.exists(path_to_convert):
    if path.isdir(path_to_convert):
      print(f"  INFO: We will convert in: {path_to_convert} Directory")
    else:
      print(f"  INFO: We will convert {path_to_convert} File")
  else:
    print(f"  FATAL: {path_to_convert} Either do not exist or we have no permissions there")
    sys.exit()
  return path_to_convert

# Method forms the list of movies
# which which needs to be onverted.
# path_to_convert - system path to directory or single file
# returns movie_list - list with movies to convert
def get_movie_list(path_to_convert):
  # A List w mkv movies found in given directory
  movie_list = []

  # Adding to array only if it is mkv or mov file
  if path.isfile(path_to_convert)  and (path_to_convert.endswith(".mkv") or path_to_convert.endswith(".mov")):
    movie_list.append(path_to_convert)

  # processing directory path, by walking through and adding files to movie_list array
  # os.walk works only with directories, passign files as argument returns nothing. Not optimal
  for root, directory, files in os.walk(path_to_convert):
    for file in files:
      if file.endswith(".mkv") or file.endswith(".mov"):
        # Full path to mkv
        mkv_full_path = os.path.join(root, file)
        # appending to main list
        movie_list.append(mkv_full_path)
      else:
        print(f"  WARNING: Given File {file} is not supported by converter {directory}")

  if movie_list:
    print(f"  INFO: Script will convert following movies :\n {movie_list}")
    return movie_list
  print("  FATAL: movie list to convert is empty. Something went very wrong in file detection method. Terminating.")
  sys.exit()


# Get user confirm on the list of converted movies
def get_user_grant_to_run():
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


# This method intended to resolve subtitle problem,
# ffmpeg could just copy subs - as is: -c:s copy
#              or move it: -c:s move_text
# sometimes move_text do not work properly, in this case its better to use 'copy'
# lets ask user and put right value into ffmpeg run cmd
def ask_user_about_sub_convert_type():
  copy = 'copy'
  mov_text = 'mov_text'
  auto_detect = 'auto'
  msg = """  INFO: ffmpeg could just copy subs - as is: '-c:s copy' or move it: '-c:s move_text'.
    Sometimes because of unsupported (subrip) subtitles type in mkv container, 'copy' method may do not work properly  - (Fail with: 'codec frame size is not set'),
    In this case its better to use 'move_text' which is slover and sometimes brakes subs names
    Enter:
      1 - for copy
      2 - for mov_text
      a - converter will detect if tere is (subrip) subs and use 'move_text' for affected movies
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
  msg = """  INFO: ffmpeg could Convert from one Container (MKV,MPV,MOV etc. ) to another container file
    if Video Stream is encoded  with the same video codec, usually MPEG. for example: .MKV->.MP4, .MOV-> .MP4
    Or ffmpeg could Transcode (with h264) - decoding MPEG and encoding with h264

    NOTE: Transcoding reduces the file size, but takes sugnificantly more time (Good for screen recordings)

    Please select what we will do. Default would be to Convert, since its faster
      1 - for covert
      2 - for transcode
  """

  print(msg)
  convert = '1'
  trancscode = '2'
  user_input = input(f"  Please select( Convert {convert}/ Transcode {trancscode}) [{convert}]: ")

  if user_input == '1' or not user_input:
    return True

  if user_input == '2':
    return False

  print(f"  ERROR: Wrong input({user_input}). Please enter 1 or 2  ")
  sys.exit()

# Renaming .mkv to .mp4
# mkv_movie_path - string with a path to mkv movie
# return : string with a path to mp4 movie
def rename_mkv_file_to_mp4(mkv_movie_path):
  mp4 = os.path.splitext(mkv_movie_path)[0]+".mp4"
  # print(f"  DEBUG: The mp4 file full path:\n    {mp4}")
  return mp4

# method to delete zero sized mp4
# files from previous unsucessful attempts
def delete_zero_sized_mp4_present(mp4_movie_path):
  if path.exists(mp4_movie_path) and path.getsize(mp4_movie_path) == 0:
    print(f"  WARNING: we have found empty {mp4_movie_path} file. \n  WARNING: Removing before conversion.")
    os.remove(mp4_movie_path)

# Autodecting subtitle type for given mkv movie
# running: ffmpeg -i /path_to_the_.mkv
# looking for "" Subtitle: subrip" markers in output,
# if we have found any  - using move_text instead of copy
def detect_srt_subrip_subtitles(ffmpeg_bin_path, mkv_path, thread_counter):
  mkv_path = f"\"{mkv_path}\""
  movie_data = subprocess.getoutput(f"{ffmpeg_bin_path}ffprobe {mkv_path} ")
  print(f"  Thread {thread_counter} INFO:  RUNNING {ffmpeg_bin_path}ffprobe {mkv_path} ")
  # print (f"  DEEBUG: {movie_data} \n ")
  subrip_subs = "'subrip' subtitles type detected! 'mov_text' option will be used"
  copy_option_note = "  NOTE: Doesn't contain 'subrip' subtitles, 'copy' option will be used"
  if movie_data.find('subrip') != -1:
    print(f"  Thread {thread_counter} ATTENTION:\n    {mkv_path} \n    {subrip_subs}")
    return True
  print(f"  Thread {thread_counter} INFO:\n    {mkv_path} \n   {copy_option_note}")
  return False



# Actual ffmpeg convert sequence
# mkv_movie_path - string with a path to mkv movie
# return : null (executes ffmpeg cmd)
def ffmpeg_convert(ffmpeg_bin_path, mkv_movie_path, c_s_sub_convert_type, mp4_full_path, thread_counter = 0):
  if mkv_movie_path == '':
    print(f"  Thread {thread_counter} INFO: Movie path is empty! exit!")
    sys.exit()

  print(f"  Thread {thread_counter} INFO: {mkv_movie_path} All set! Ready to Rock!")

  # Autodetecting srt presense if auto_detect option given
  if c_s_sub_convert_type == 'auto':
    if detect_srt_subrip_subtitles(ffmpeg_bin_path, mkv_movie_path, thread_counter):
      sub_convert_type = 'mov_text -ignore_unknown'
    else:
      sub_convert_type = 'copy -ignore_unknown'
  else:
    sub_convert_type = c_s_sub_convert_type


  cmd_options = [
    f"{ffmpeg_bin_path}ffmpeg -i ",
    f"\"{mkv_movie_path}\"",
    ' -map 0 -c copy -c:s ',
    sub_convert_type,
    ' ',
    f"\"{mp4_full_path}\""
  ]
  cmd = ''.join(cmd_options)
  print(f"  Thread {thread_counter} INFO: Executing: \n    {cmd} \n\n")



  movie_data = subprocess.getoutput(cmd)
  print(f"  Thread {thread_counter} INFO: Output: \n {movie_data} \n")



# Very similar converter of MOV files to mp4
#  Wrappper for  ffmpeg -i ~/file.mov -vcodec h264 -acodec mp2 ~/file.mp4
def ffmpeg_transcode(ffmpeg_bin_path, mov_movie_path, mp4_full_path, thread_counter = 0):
  if mov_movie_path == '':
    print(f"  Thread {thread_counter} INFO: Movie path is empty! exit!")
    sys.exit()

  print(f"  Thread {thread_counter} INFO: {mov_movie_path} All set! Ready to Rock!")

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


# Initializing threads
def convert_with_threads(ffmpeg_bin_path, mkv_movies, do_convert, thread_worker_number):
  thread_count = 0

  # Current approach 1 thread per movie, which could hurt you cpu ))
  # Creating a number of threads equal to number of movies found
  # mkv_number = int(mkv_movies.count)
  # 21 - kills mbp 2021
  print(f"  INFO: The Thread worker number is: {thread_worker_number}")
  with concurrent.futures.ThreadPoolExecutor(max_workers = thread_worker_number) as executor:
    # we need to ask user about subs conversion  only once
    if do_convert:
      user_subtitle_convert_type = ask_user_about_sub_convert_type()

    # Proccessing the list
    for movie_file in mkv_movies:
      mp4_movie_name = rename_mkv_file_to_mp4(movie_file)
      delete_zero_sized_mp4_present(mp4_movie_name)
      if do_convert:
        print("  INFO: READY TO CONVERT")
        executor.submit(ffmpeg_convert,
                          ffmpeg_bin_path,
                          movie_file,
                          user_subtitle_convert_type,
                          mp4_movie_name,
                          thread_count)
      else:
        print("  INFO: READY TO TRANSCODE")
        executor.submit(ffmpeg_transcode,
                          ffmpeg_bin_path,
                          movie_file,
                          mp4_movie_name,
                          thread_count)
      thread_count+=1


# main part
def main():
  thread_workers_max = 3
  ffmpeg_bin_path = ffmpeg_home()
  path_to_convert = get_movie_path(sys.argv)
  mkv_movie_list = get_movie_list(path_to_convert)
  get_user_grant_to_run()
  do_convert = ask_user_convert_or_transcode()

  start_time = time.process_time()

  convert_with_threads(ffmpeg_bin_path, mkv_movie_list, do_convert, thread_workers_max)

  elapsed_time = time.process_time() - start_time
  print(f"  INFO: Conversion time: {elapsed_time}")


if __name__ == '__main__':
  main()



# cat *.VOB > '/file/moviename.vob';
# do
#   /ffmpeg/bin/ffmpeg -i '/moviename.vob' -codec:a copy -codec:v libx264 '/file.mp4';
# done

# ffmpeg -i ~/file.mov -vcodec h264 -acodec mp2 ~/file.mp4
