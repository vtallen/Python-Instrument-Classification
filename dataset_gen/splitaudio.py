'''
* ********************************************************************************************** *
*                                                                                                *
* Author:          Vincent Allen                                                                 *
* Creation Date:   02/17/2024                                                                    *
* Filename:        splitmp3.py                                                                   *
*                                                                                                *
* Purpose:         Takes a file or directory and then splits the audio file(s) in clips of a     *
*                  certain number of seconds long.                                               *
*                                                                                                *
* Usage:                                                                                         *
*       splitmp3.py <audio dir> <len> <output dir>                                               *
*       splitmp3.py -s <audio file> <len> <output dir>                                           *
*                                                                                                *
*       len is in seconds                                                                        *
*                                                                                                *
*                                                                                                *
* ********************************************************************************************** *
'''
import sys
import os
import subprocess
import glob
import math

import librosa
import soundfile as sf
import tqdm

split_audio_cmd = 'python3 splitaudio.py -s'

def split_all_files(filenames, outpath, seconds, max_processes):
    output_log_cmd = '>> librosa.log 2>&1'
    processes = []
    commands = []
    
    for filename in filenames:
        commands.append(split_audio_cmd + ' ' + filename + ' ' + str(seconds) + ' ' + outpath + str(seconds) + '/' + output_log_cmd)
    
    num_commands = len(commands)
    conversion_num = 0

    pbar = tqdm.tqdm(desc=str(seconds) + ' second split',total=num_commands);

    while commands:
        while len(processes) < max_processes and commands:
            processes.append(subprocess.Popen(commands.pop(), shell=True))

        completed_processes = []     
        for process in processes:
            if process.poll() is not None:
                completed_processes.append(process)
                conversion_num += 1
                pbar.update(1)
                # print(str(seconds) + ' second audio split ' + str(conversion_num) + '/' + str(num_commands) + ' has been completed')

        for process in completed_processes:
            processes.remove(process) 

def split_audiofile(filename, seconds, outdir):
    # Make the output Directory if it does not exist
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # Gets the filename into a path and a filename
    split_filename = os.path.split(filename)

    # Creates a np array of samples and the sampling rate of the file

    samples, samplerate = librosa.load(filename, sr=None)

    # The number of samples that will be in each second
    samples_per_split = math.ceil(seconds * samplerate)

    # iterate over each range of samples for the correct number of seconds
    for fileno, idx in enumerate(range(0, len(samples), samples_per_split)):
        newdata = samples[idx : idx + samples_per_split]

        # The filename split into
        noext = split_filename[1].split('.')

        sf.write(outdir + noext[0] +  '_' + str(fileno) + '.' +noext[1], newdata, samplerate)
        # sf.write(outdir + '/' + noext[0] +  '_' + str(fileno) + '.' +noext[1], newdata, samplerate)

def get_audio_files(folder_path, valid_extensions):
    # List to store valid files
    valid_files = []

    # Iterate through all files in the folder
    for file_name in os.listdir(folder_path):
        # Get file extension
        _, extension = os.path.splitext(file_name)
        # Check if the extension is in the valid extensions list
        if extension.lower() in valid_extensions:
            # If it is, append the file path to the list
            valid_files.append(os.path.join(folder_path, file_name))

    return valid_files

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc != 4 and argc != 5:
        print('USAGE:')
        print('\tsplitaudio.py <audio dir> <len(seconds)> <output dir> <max_processes>- splits all files contained in <audio dir> to files of <len> seconds')
        print('\tsplitaudio.py -s <file> <len(seconds)> <output dir> - splits a single file into <len> second files and places the output somewhere')
        sys.exit(1)
    
    # Run split_audiofile on a single file
    if argv[1] == '-s':
        split_audiofile(argv[2], float(argv[3]), argv[4])
    else:
        wavs = glob.glob(argv[1] + '*.wav')
        mp3 = glob.glob(argv[1] + '*.mp3')
        mp4 = glob.glob(argv[1] + '*.mp4')
        
        valid_files = []
        valid_files.extend(wavs)
        valid_files.extend(mp3)
        valid_files.extend(mp4)
        
        split_all_files(valid_files, argv[3], float(argv[2]), int(argv[4]))

        

