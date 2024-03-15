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

def convert_all_to_wav(filenames, split_wav_path, max_processes):
    ffmpeg_cmd = 'ffmpeg -i'
    output_log_cmd = '>> ffmpeg.log 2>&1'
    # Make the output Directory if it does not exist
    if not os.path.exists(split_wav_path):
        os.mkdir(split_wav_path)
    
    split_filenames = [os.path.split(filename) for filename in filenames]

    processes = []
    commands = []

    for filename in split_filenames:
        no_ext = filename[1].split('.')
        commands.append(ffmpeg_cmd + ' ' + filename[0] + '/' + filename[1] + ' ' + split_wav_path + '/' + no_ext[0] + '.wav' + ' ' + output_log_cmd)

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

def single_convert():
    pass

def tester_func():
    print("Other module")

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
    

 
    
    




