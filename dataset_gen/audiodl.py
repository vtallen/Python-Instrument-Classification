'''
* ********************************************************************************************** *
*                                                                                                *
* Author:          Vincent Allen                                                                 *
* Creation Date:   02/17/2024                                                                    *
* Filename:        audiodl.py                                                                    *
*                                                                                                *
* Purpose:         Takes links to YouTube videos in a csv file that have been tagged with an     *
*                  instrument type, downloads the audio files, and saves them in the format      *
*                  <instrument>_<slug> where slug is a base64 encoded string of the video title  *
*                                                                                                *
* Usage:                                                                                         *
*   python3 audiodl.py <csv_filename> <output_dir>                                               *
*                                                                                                *
*   <csv_filename>  -   csv containing instrument tagged YouTube links                           *
*   <output_dir>    -   Directory where the downloaded audio files should be placed              *
*                                                                                                *
* CSV format: 2 columns called Instrument and Link. This is pretty self explanetory              *
*                                                                                                *
* ********************************************************************************************** *
'''
from pytube import YouTube
import tqdm

import csv
import base64
import os
import sys
import subprocess
import datetime

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             download_audio                                                               *
*                                                                                                *
* Parameters:       str link - YouTube link to download audio for                                *
*                   str instrument - The instrument contained within the audio. Used to tag files*
*                   str outdir - The folder to place the download file in                        *
*                                                                                                *
* Purpose:          Downloads the audio of a YouTube video, and tags the filename with the passed*
*                   in instrument name                                                           *
*                                                                                                *
* ********************************************************************************************** *
'''
def download_audio(link, instrument, outdir):
    try: # Catches an error where a video is age restricted and needs a logged in account
        yt = YouTube(link)
        # grab only audio files
        video = yt.streams.filter(only_audio=True, file_extension='mp4').first()
        #print('Downloading:', row[0], video.title) #type: ignore
        
        outfilename = instrument + '_' + base64.urlsafe_b64encode(video.title.encode()).decode('UTF-8') #type: ignore 
        video.download(filename=outfilename + '.mp4', output_path=outdir) #type: ignore 
    except:
        print('Failed to download ', link)

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             download_audios                                                              *
*                                                                                                *
* Parameters:       csv.reader csv    - csv containg 2 columns: Instrument, the tagged instrument*
*                                       and Link, the YouTube link                               *
*                   str outdir        - The folder to place the download file in                 *
*                   int max_processes - The maximum number of subprocesses allowed to exist      *
*                                                                                                *
* Purpose:          Downloads the audio of all YouTube videos in the csv, then tags all of their *
*                   filenames.                                                                   *
*                                                                                                *
*                   Filenames are in the format instrument_title.mp4 where title is a BASE64     *
*                   encoded string. This is done to ensure it is a valid filename and is unique  *
*                                                                                                *
*                   Multithreaded with subprocess                                                *
*                                                                                                *
* ********************************************************************************************** *
'''
def download_audios(csv, outdir, max_processes):

    dl_cmd = 'python3 audiodl.py -s'
    # Make the output Directory if it does not exist
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    processes = []
    commands = []

    for row in csv:
        commands.append(dl_cmd + " " + '"' + row[1] + '"' + " " + row[0] + " " + outdir)

    pbar = tqdm.tqdm(desc='Downloading audio', total=len(commands))

    conversion_num = 0
    while commands: 
        # Fill up the currently running processes to the max allowed
        while len(processes) < max_processes and commands:
            processes.append(subprocess.Popen(commands.pop(), shell=True))
        
        completed_processes = []     
        for process in processes:
            if process.poll() is not None:
                completed_processes.append(process)
                conversion_num += 1
                pbar.update(1)
        
        for process in completed_processes:
            processes.remove(process) 
    
    for process in processes:
        process.wait()


__USAGE__ = 'python3 audiodl.py <csv> <outdir> <max_proccesses>'\
        'python3 audiodl.py -s <link> <instrument> <outdir>'

if __name__ == "__main__":
    # Get cmd line args
    argv = sys.argv
    argc = len(sys.argv)
    
    # Single download case 
    if argv[1] == '-s':
        download_audio(argv[2], argv[3], argv[4])
    elif argc == 4:
        infile = open(argv[1], 'r')
        incsv = csv.reader(infile, delimiter=',', quotechar='"')

        inheader = incsv.__next__();
        # inst_i = inheader.index('Instrument')
        # link_i = inheader.index('Link')
        download_audios(incsv, argv[2], int(argv[3]))

        infile.close()
    else:
        print(__USAGE__)
