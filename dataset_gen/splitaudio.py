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
*       splitaudio.py -s <file> <len> <output dir>                                               *
*           -s           - Flag for single file processing                                       *
*           <file>       - The audio file to split                                               *
*           <seconds>    - How long each split file should be                                    *
*           <output dir> - The directory to place split files into                               *
*                                                                                                *
*       splitaudio.py -b <seconds> <output dir> <files>                                          *
*           -b           - Flag for batch file processing                                        *
*           <seconds>    - How long each split file should be                                    *  
*           <output dir> - The directory to place split files into                               *
*           <files>      - A space delimited list of files to split                              *
*                                                                                                *
*       splitaudio.py -m <audio dir> <seconds> <output dir> <max_processes>                      *
*           -m           - Flag for multithreaded file processing                                *
*           <audio dir>  - Folder containting the files to split                                 *
*           <seconds>    - How long each split file should be                                    *  
*           <output dir> - The directory to place split files into                               *
*           <max_processes> - The maximum number of subprocess allowed to exist at once          *
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

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             batch_split                                                                  *
*                                                                                                *
* Parameters:       str[] filenames   - All the audio files to be split                          *
*                   int seconds       - The length each split audio file should be               *
*                   str outdir        - What the output directory to put split files in.         *
*                                       length of the split gets appended to this                *
*                                                                                                *
* Purpose:         Takes in a list of audio filenames, and splits each of those files into       *
*                  shorter files of length seconds. Runs on a single thread                      *
*                                                                                                *
* ********************************************************************************************** *
'''
def batch_split(filenames, seconds, outdir):
    for filename in filenames:
        split_audiofile(filename, seconds, outdir)

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             append_cmd                                                                   *
*                                                                                                *
* Parameters:       str[] filenames   - All the audio files to be split                          *
*                   int seconds       - The length each split audio file should be               *
*                   str outdir        - What the output directory to put split files in.         *
*                                       length of the split gets appended to this                *
*                                                                                                *
* Purpose:         Generates a batch mode command string that can be used to call this program   *
*                  appends all filenames onto the template cmd                                   *
*                                                                                                *
* Returns:         str - A filled out template command                                           *
*                                                                                                *
* ********************************************************************************************** *
'''
def append_cmd(filenames, seconds, outdir):
    cmd = 'python3 splitaudio.py -b ' + str(seconds) + ' ' + outdir

    process_cmd = cmd
    for file in filenames:
        process_cmd += ' ' + file

    return process_cmd

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             make_cmds_arr                                                                *
*                                                                                                *
* Parameters:       str[] filenames   - The filenames to create commands for                     *
*                   int seconds       - The length each split audio file should be               *
*                   str outdir        - The path to place normalized files in                    *
*                   int max_processes - The maximum number of threads to be used at any one time *
*                                                                                                *
* Purpose:          Takes in a list of filenames and returns a 2d array with each element        *
*                   containing a str in element zero, which is the command to process a          *
*                   chunk of files, and an int in element 1 which is how many files that cmd     *
*                   will process                                                                 *
*                                                                                                *
* Returns:          [[str, int]] - str - the filled out command template                         *
*                                  int - the number of files that command will process           *
*                                                                                                *
* ********************************************************************************************** *
'''
def make_cmds_arr(filenames, seconds, outdir, max_processes):
    numfiles = len(filenames)
     
    # No files to process
    if numfiles == 0:
        return [] 
    elif numfiles == 1: # This function would technically work with 1 file, it's just needlessly overcomplex
        split_audiofile(filenames[0], seconds, outdir)

    numrounds = 2 
    files_per_process = (numfiles // max_processes) // numrounds 
    # files_remainder = numfiles - ((max_processes * numrounds) * files_per_process)
         
    cmds = []
    start_idx = 0
    
    # If less files than there are max_processes * numrounds, just distribute the small number of files onto their own processes
    if files_per_process == 0:
        files_per_process = 1

    for _ in range(max_processes * numrounds):

        end_idx = start_idx + files_per_process

        if end_idx > numfiles:
            break

        process_files = filenames[start_idx:end_idx]
        
        # Happens if we have already distributed all files we have
        if len(process_files) == 0:
            continue

        process_cmd = append_cmd(process_files, seconds, outdir) 
        
        cmds.append([process_cmd, len(process_files)])
        start_idx = end_idx
    
    # Reached if the number of files is not evenly divisible by max_processes * numrounds
    leftover_filenames = filenames[start_idx:len(filenames)] 
    if len(leftover_filenames) > 0:
        cmds.append([append_cmd(leftover_filenames, seconds, outdir), len(leftover_filenames)])

    return cmds


'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             multithread_split                                                            *
*                                                                                                *
* Parameters:       str[] filenames   - All the audio files to be split                          *
*                   int seconds       - The length each split audio file should be               *
*                   str outdir        - What the output directory to put split files in.         *
*                                       length of the split gets appended to this                *
*                   int max_processes - The maximum number of subprocesses allowed to exist      *
*                                                                                                *
* Purpose:         Takes in a list of audio filenames, and splits each of those files into       *
*                  shorter files of length seconds. Subprocess is used to multithread the process*
*                                                                                                *
* ********************************************************************************************** *
'''
def multithread_split(indir, seconds, outdir, max_processes):
    filenames = glob.glob(indir + '*.wav')
    
    # If we're only doing 1 thread, then splitting up the workload is useless
    if max_processes == 1:
        batch_split(filenames, seconds, outdir)
        return

    cmds = make_cmds_arr(filenames, seconds, outdir, max_processes) 
    running_processes = []
    
    pbar = tqdm.tqdm(desc='Splitting Audio', total=len(filenames))

    while cmds:
        # Checking cmds as there is a chance we could try and pop off an empty list, and the outer check to cmds
        # will not prevent this
        while len(running_processes) < max_processes and cmds:
            cmd_and_count = cmds.pop()
            # Pass on the selected process along with the number of files it will normalize 
            running_processes.append([subprocess.Popen(cmd_and_count[0], shell=True), cmd_and_count[1]])
        
        # See if any of the processes have completed, and remove them if they are
        completed_processes = []
        for cmd_and_count in running_processes:
            if cmd_and_count[0].poll() is not None:
                completed_processes.append(cmd_and_count)
                pbar.update(cmd_and_count[1])
        
        # Remove any processes that have been completed
        for process in completed_processes: 
            running_processes.remove(process)
    
    # Wait for all processes to complete once all cmds have been run
    for cmd_and_count in running_processes:
        cmd_and_count[0].wait()
        pbar.update(cmd_and_count[1])

__USAGE__ = 'splitaudio.py -m <audio dir> <len(seconds)> <output dir> <max_processes>- splits all files contained in <audio dir> to files of <len> seconds. Is multithreaded'\
        'splitaudio.py -b <len(seconds)> <output dir> <file1 ... file2 ... filen> - splits all files passed in on the command line into <len> second files'\
        'splitaudio.py -s <file> <len(seconds)> <output dir> - splits a single file into <len> second files and places the output somewhere'

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    
    if argv[1] == '-s':
        split_audiofile(argv[2], float(argv[3]), argv[4])
    if argv[1] == '-b' and argc > 4:
        seconds = float(argv[2])
        
        outdir = argv[3]
        os.makedirs(outdir, exist_ok=True)

        filenames = [x for x in argv[4:argc]]

        batch_split(filenames, seconds, outdir) 
    if argv[1] == '-m':
        indir = argv[2]
        seconds = float(argv[3])
        
        outdir = argv[4]
        os.makedirs(outdir, exist_ok=True)
        
        max_processes = int(argv[5])
        multithread_split(indir, seconds, outdir, max_processes)

    # Run split_audiofile on a single file
