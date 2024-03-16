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

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             split_all_files                                                              *
*                                                                                                *
* Parameters:       str[] filenames   - All the audio files to be split                          *
*                   str outpath_start - What the output directory name should start with. The    *
*                                       length of the split gets appended to this                *
*                   int seconds       - The length each split audio file should be               *
*                   int max_processes - The maximum number of subprocesses allowed to exist      *
*                                                                                                *
* Purpose:         Takes in a list of audio filenames, and splits each of those files into       *
*                  shorter files of length seconds. Subprocess is used to multithread the process*
*                                                                                                *
* ********************************************************************************************** *
'''
def split_all_files(filenames, outpath_start, seconds, max_processes):
    split_audio_cmd = 'python3 splitaudio.py -s'
    # Constructs the final output path
    outpath = outpath_start + str(seconds) + '/' 

   # Make the output Directory if it does not exist
    if not os.path.exists(outpath):
        os.makedirs(outpath, exist_ok=True)
    
    # This variable is appended to each command, it redirects all output of the command into a log file
    # Otherwise, the screen gets clogged with librosa's output that we do not care about
    output_log_cmd = '>> librosa.log 2>&1'
    processes = []
    commands = []
    
    # Create all of the commands
    for filename in filenames:
        commands.append(split_audio_cmd + ' ' + filename + ' ' + str(seconds) + ' ' + outpath + output_log_cmd)
    
    num_commands = len(commands)
    conversion_num = 0

    pbar = tqdm.tqdm(desc=str(seconds) + ' second split',total=num_commands);

    while commands:
        while len(processes) < int(max_processes) and commands:
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

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             split_audiofile                                                              *
*                                                                                                *
* Parameters:       str filename    - The audio file to be split                                 *
*                   int seconds     - The length each split audio file should be                 *
*                   str outdir      - The directory to place the final file in. Assumes it       *
*                                     already exists                                             *
*                                                                                                *
* Purpose:          Splits the given audio file into shorter files of length seconds             * 
*                                                                                                *
* ********************************************************************************************** *
'''
def split_audiofile(filename, seconds, outdir):
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

        sf.write(outdir + noext[0] +  '_' + str(fileno) + '.' + noext[1], newdata, samplerate)

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

