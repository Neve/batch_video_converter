# MKV/MOV to MP4 video converter script

## DESCRIPTION

A script to convert MOV and MKV videos and records to mp4.

- Designed to run in the shell,  
- Has support of Python threading model,  
- Supports MKV and MOV files  
- Python 3 or greater is required.  

The idea behind the script is driven by a lack of MKV support on apple devices such as iPhones or AppleTV.  
Target is to be able to watch Plex movie using AppleTV app and be able to convert MOV recordings to MP4.  

MP4 and MKV are just containers; the video stream usually is MPEG, so it is relatively easy to convert MKV or MOV to MP4  
  
The script is designed to run on a personal laptop, since modern home NAS devices do not have much processing power.  
  
## USAGE

  Run the script targeting mkv/mov file or folder with mkv/mov.

```bash
/{PATH}/mkv_to_mp4_batch.py '/{PATH}/video.mkv'
```

  or mkv dir

```bash
/{PATH}/mkv_to_mp4_batch.py '/{PATH TO DIR WITH .mkv}'
```

Script uses threads; the thread worker number is currently set to 4. You can adjust using the `thread_workers_max` variable in the main block.  
There are several script run parameters, all of which have default options, so press ENTER for automatic detection of video container parameters.
