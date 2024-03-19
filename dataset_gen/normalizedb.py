'''
**************************************************************************************************
* Filename:     normalizedb.py                                                                   *
*                                                                                                *
* Description:  Brings up the average dbfs of all samples in a directory to the target_dBFS.     *
*               This aims to make it easier to cross compare samples for the decision tree. I    *
*               need to do some more research to see if this is actually helping or if I need to *
*               do it a different way. Doing this did give me a slight bump in accuracy when     *
*               running decision trees in Weka                                                   *
*                                                                                                *
* Usage:       python3 normalizedb.py -s <dBFS> <filename> <outdir>                              *
*                   -s          - Flag to process a single file                                  * 
*                   <dBFS>      - The target db level                                            *
*                   <filename>  - The file to normalize                                          * 
*                   <outdir>    - Where to place the file                                        *
*                                                                                                *
*              python3 normalizedb.py -m <dBFS> <indir> <outdir> <maxprocesses>                  *
*                   -m              - Flag to prcoess a whole dir of files                       *
*                   <indir>         - The directory containging files to normalize               *
*                   <dBFS>          - The target db level                                        *
*                   <outdir>        - Where to place the file                                    *
*                   <max_processes> - The max number of subprocesses allowed to spawn            *
**************************************************************************************************
'''

import os
import glob
import subprocess
import sys
from math import ceil

from pydub import AudioSegment, effects
import tqdm

# TODO : Delete once the normalize_audio method is confirmed working
# def match_target_amplitude(sound, target_dBFS):
#     change_in_dBFS = target_dBFS - sound.dBFS
#     return sound.apply_gain(change_in_dBFS)

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             normalize_audio                                                              *
*                                                                                                *
* Parameters:       str file_path     - The file to be normalized                                *
*                   str outpath       - The path to place converted files in                     *
*                   int target_dBFS   - The target db level                                      *
*                                                                                                *
* Purpose:          Normalizes the db level of an audio file using pydub                         * 
*                                                                                                *
* ********************************************************************************************** *
'''
def normalize_audio(filename, outpath, target_dBFS=-20):
    split_file_path = os.path.split(filename)
    noext = split_file_path[1].split('.')

    sound = AudioSegment.from_file(filename) # Load the audio file
    change_in_dBFS = target_dBFS - sound.dBFS # Determine how much to bring the dbs up
    # normalized_sound = sound + change_in_dBFS # Adjust the 
    normalized_sound = sound.apply_gain(change_in_dBFS)
    # normalized_sound = match_target_amplitude(sound, target_dBFS)
    normalized_sound.export(outpath +  noext[0] + '_norm.' + noext[1], format='wav')
    
'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             append_cmd                                                                   *
*                                                                                                *
* Parameters:       str[] filenames - The filenames to be appended on to the normalize cmd       *
*                   str outdir      - The path to place normalized files in                      *
*                   int target_dBFS - The target db level                                        *
*                                                                                                *
* Purpose:          Takes in a list of filenames and returns a completed batch mode command for  *
*                   this script so that multithread_normalize can split up a massive list of     *
*                   files between threads.                                                       *
*                                                                                                *
* Returns:          str - the filled out command template                                        *
*                                                                                                *
* ********************************************************************************************** *
'''
def append_cmd(filenames, outdir, target_dBFS=-20):
    cmd = 'python3 normalizedb.py -b ' + str(target_dBFS) + ' ' + outdir 

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
*                   str outdir        - The path to place normalized files in                    *
*                   int max_processes - The maximum number of threads to be used at any one time *
*                   int target_dBFS   - The target db level                                      *
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
def make_cmds_arr(filenames, outdir, max_processes, target_dBFS=-20):
    numfiles = len(filenames)
    numrounds = 2 
    files_per_process = (numfiles // max_processes) // numrounds 
    # files_remainder = numfiles - ((max_processes * numrounds) * files_per_process)

    cmds = []
    start_idx = 0

    for idx in range(max_processes * numrounds):
        end_idx = start_idx + files_per_process
        process_files = filenames[start_idx:end_idx]
        
        process_cmd = append_cmd(process_files, outdir, target_dBFS) 
        
        cmds.append([process_cmd, len(process_files)])
        start_idx = end_idx
    
    leftover_filenames = filenames[start_idx:len(filenames)] 
    cmds.append([append_cmd(leftover_filenames, outdir, target_dBFS), len(leftover_filenames)])

    return cmds

def batch_normalize(filenames, outdir, target_dBFS=-20):
    for filename in filenames:
        normalize_audio(filename, outdir, target_dBFS)

def multithread_normalize(indir, outdir, max_processes, target_dBFS=-20):
    filenames = glob.glob(indir + '*.wav') # locate all wavfiles in the supplied dir
    cmds = make_cmds_arr(filenames, outdir, max_processes) # Generates all of the commands we need
    
    running_processes = []
    
    pbar = tqdm.tqdm(desc='Normalizing dbfs', total=len(filenames))

    while cmds:
        while len(running_processes) < max_processes:
            cmd_and_count = cmds.pop()
            # Pass on the selected process along with the number of files it will normalize 
            running_processes.append([subprocess.Popen(cmd_and_count[0], shell=True), cmd_and_count[1]])
        
        # See if any of the processes have completed, and remove them if they are
        completed_processes = []
        for cmd_and_count in running_processes:
            if cmd_and_count[0].poll() is not None:
                completed_processes.append(cmd_and_count)
                pbar.update(cmd_and_count[1])

        for process in completed_processes:
            running_processes.remove(process)
    
    # Wait for all processes to complete once all cmds have been run
    for cmd_and_count in running_processes:
        cmd_and_count[0].wait()
        pbar.update(cmd_and_count[1])

__USAGE__ = \
        'Normalizes a file or group of files to a target decible level\n'\
        'python3 normalizedb.py -s <dBFS> <filename> <outdir> - normalize the given wav file\n'\
        'python3 normalizedb.py -m <dBFS> <indir> <outdir> <maxprocesses> - normalize all files in outdir'\
        'python3 normalizedb.py -b <dBFS> <outdir> <file1 ... file2 ... filen> - Normalize all files passed on the command line'

if __name__ == "__main__":
    argc = len(sys.argv)
    argv = sys.argv
    
    if argv[1] == '-b' and argc > 4: # Batch normalization
        target_dBFS = int(argv[2])
        outdir = argv[3]

        filenames = [x for x in argv[4:argc]] # pulls in every argument after the outdir

        os.makedirs(outdir, exist_ok=True) # Make sure we have a dir to put everything into
        batch_normalize(filenames, outdir, target_dBFS)

    elif argv[1] == '-m' and argc == 6: # Multithreaded normalization
        target_dBFS = int(argv[2])
        indir = argv[3]
        outdir = argv[4]
        max_processes = int(argv[5])

        multithread_normalize(indir, outdir, max_processes, target_dBFS)
    elif argv[1] == '-s' and argc == 5: # Single file normalization
        target_dBFS = int(argv[2]) 
        filename = argv[3]
        outdir = argv[4]

        normalize_audio(filename, outdir, target_dBFS)
    else:
        print(__USAGE__)

    sys.exit()
    if argc == 5:
        normalize_audio(argv[3], argv[4], int(argv[2]))
    elif argc == 6:
        if not os.path.exists(argv[4]):
            os.mkdir(argv[4])
        
        norm_cmd = 'python3 normalizedb.py -s ' + argv[2] + ' '
        filenames = glob.glob(argv[3] + '*.wav')

        commands = []
        
        for filename in filenames:
            commands.append(norm_cmd + filename + ' ' + argv[4])

        pbar = tqdm.tqdm(desc='Normalizing dbfs', total=len(commands))
        
        processes = []

        conversion_num = 0
        while commands: 
            # Fill up the currently running processes to the max allowed
            while len(processes) < int(argv[5]) and commands:
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

    else:
        print(__USAGE__)
