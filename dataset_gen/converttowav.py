'''
**************************************************************************************************
* Filename:    converttowav.py                                                                   *
*                                                                                                *
* Description: uses ffmpeg to convert all audio files in a folder to wav files.                  *
*              uses subprocess to multithread conversion.                                        *
*                                                                                                *
* Usage:       python3 converttowav.py <infolder> <outfolder> <max_processes>                    *
*                   <infolder>      - The folder to search for audiofiles                        *
*                   <outfolder>     - The folder to store the converted fils. Gets created if    *
*                                   it does not exist                                            *
*                   <max_processes> - The max number of subprocesses allowed to spawn            *
*                                                                                                *
**************************************************************************************************
'''

import sys
import os
import subprocess
import glob

import tqdm

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             convert_all_to_wav                                                           *
*                                                                                                *
* Parameters:       str[] filenames   - All the audio files to be converted                      *
*                   str outpath       - The path to place converted files in                     *
*                   int max_processes - The maximum number of subprocesses allowed to exist      *
*                                                                                                *
* Purpose:          Converts all audio files in the given directory to wav files. multithreaded  * 
*                   by using subprocess to repeatedly call ffmpeg                                *
*                                                                                                *
* ********************************************************************************************** *
'''
def convert_all_to_wav(filenames, outpath, max_processes):
    ffmpeg_cmd = 'ffmpeg -i'
    output_log_cmd = '>> ffmpeg.log 2>&1'
    # Make the output Directory if it does not exist
    if not os.path.exists(outpath):
        os.makedirs(outpath, exist_ok=True)
    
    split_filenames = [os.path.split(filename) for filename in filenames]

    processes = []
    commands = []

    for filename in split_filenames:
        no_ext = filename[1].split('.')
        commands.append(ffmpeg_cmd + ' ' + filename[0] + '/' + filename[1] + ' ' + outpath + '/' + no_ext[0] + '.wav' + ' ' + output_log_cmd)

    pbar = tqdm.tqdm(desc='Converting to wav', total=len(commands))

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

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             convert_to_wav                                                               *
*                                                                                                *
* Parameters:       str filenames     - The audio file to be converted                           *
*                   str outpath       - The path to place converted files in                     *
*                                                                                                *
* Purpose:          Converts the given audio file to wav using ffmpeg. Assumes outpath exists    * 
*                   This function is not used in dataset_gen, but is used by the cli_tool        * 
*                                                                                                *
* Returns:          str - The filename of the output file                                        *
* ********************************************************************************************** *
'''
def convert_to_wav(filename, outpath):
    ossplitfile = os.path.split(filename)
    noext = os.path.splitext(ossplitfile[1])
    
    outfilename = outpath + noext[0] + '.wav'

    output_log_cmd = '>> ffmpeg.log 2>&1'
    cmd = 'ffmpeg -i ' + filename + ' ' + outfilename + '>>' + outpath + 'ffmpeg.log 2>&1'
    
    convertpros = subprocess.Popen(cmd, shell=True)

    convertpros.wait()

    return outfilename

__USAGE__='USASGE:'\
        'python3 converttowav.py <infolder> <outfolder> <max_processes>'

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc != 4:
        print(__USAGE__)
        sys.exit(1)

    filenames = glob.glob(argv[1]+'/*.mp4')
    filenames.extend(glob.glob(argv[1] + '/*.mp3'))

    convert_all_to_wav(filenames, argv[2], int(argv[3]))
    

 
    
    




