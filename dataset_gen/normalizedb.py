import os
import glob
import subprocess
import sys

from pydub import AudioSegment
import tqdm

# Function to normalize audio file
def normalize_audio(file_path, out_folder, target_dBFS=-20):
    split_file_path = os.path.split(file_path)
    noext = split_file_path[1].split('.')

    sound = AudioSegment.from_file(file_path)
    change_in_dBFS = target_dBFS - sound.dBFS
    normalized_sound = sound + change_in_dBFS
    normalized_sound.export(out_folder + '/' + noext[0] + '_norm.' + noext[1], format='wav')

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
        filenames = glob.glob(argv[3] + '/*.wav')

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
    else:
        print(__USAGE__)
