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

from pydub import AudioSegment, effects
import tqdm

# TODO : Delete once the normalize_audio method is confirmed working
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

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
    

__USAGE__ = \
        'python3 normalizedb.py -s <dBFS> <filename> <outdir> - normalize the given wav file\n'\
        'python3 normalizedb.py -m <dBFS> <indir> <outdir> <maxprocesses>- normalize all files in outdir'
        
if __name__ == "__main__":
    argc = len(sys.argv)
    argv = sys.argv
    
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
