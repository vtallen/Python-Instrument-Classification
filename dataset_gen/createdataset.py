import subprocess
import os
import glob
import sys

download_cmd = 'python3 audiodl.py solo_instrument_video_links.csv full_audio'
split_mp3_cmd = 'python3 splitmp3.py -s'

def split_mp3s(filenames, split_mp3_path, seconds, max_processes):
    output_log_cmd = '>> librosa.log 2>&1'
    processes = []
    commands = []
    
    for filename in filenames:
        commands.append(split_mp3_cmd + ' ' + filename + ' ' + str(seconds) + ' ' + split_mp3_path + str(seconds) + output_log_cmd)
    
    num_commands = len(commands)
    conversion_num = 0
    while commands:
        while len(processes) < max_processes and commands:
            processes.append(subprocess.Popen(commands.pop(), shell=True))

        completed_processes = []     
        for process in processes:
            if process.poll() is not None:
                completed_processes.append(process)
                conversion_num += 1
                print('mp3 split ' + str(conversion_num) + '/' + str(num_commands) + ' has been completed')

        
        for process in completed_processes:
            processes.remove(process) 

    '''
    for filename in filenames:
        processes.append(subprocess.Popen(split_mp3_cmd + ' ' + filename + ' ' + str(seconds) + ' ' + split_mp3_path + str(seconds) + output_log_cmd, shell=True))    
    
    for i, p in enumerate(processes):
        p.wait()
        print(str(seconds) + ' seconds split for file #' + str(i), 'completed')
    '''

def convert_to_wav(filenames, split_wav_path, max_processes):
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
                print(split_wav_path + ' conversion #' + str(conversion_num), 'has been completed')
        
        for process in completed_processes:
            processes.remove(process) 

if __name__ == "__main__":
    full_audio_path = 'full_audio'
    split_mp3_path = 'split_mp3_'

    # download = subprocess.Popen(download_cmd, shell=True);
    # download.wait()
    
    full_audio_filenames = glob.glob(full_audio_path + '/*.mp4')
    convert_to_wav(full_audio_filenames, 'full_wav', 10) 
    # split_mp3s(full_audio_filenames, split_mp3_path, 1, 15)
    # split_mp3s(full_audio_filenames, split_mp3_path, 2)
    # split_mp3s(full_audio_filenames, split_mp3_path, 3)
    # split_mp3s(full_audio_filenames, split_mp3_path, 4)
    # split_mp3s(full_audio_filenames, split_mp3_path, 5)

    split1_filenames = glob.glob('split_mp3_1/*.mp4')
    # split2_filenames = glob.glob('split_mp3_2/*.mp3')
    # split3_filenames = glob.glob('split_mp3_3/*.mp3')
    # split4_filenames = glob.glob('split_mp3_4/*.mp3')
    # split5_filenames = glob.glob('split_mp3_5/*.mp3')

    # convert_to_wav(split2_filenames, 'split_wav_2', 20) 
    # convert_to_wav(split3_filenames, 'split_wav_3', 20) 
    # convert_to_wav(split4_filenames, 'split_wav_4', 20) 
    # convert_to_wav(split5_filenames, 'split_wav_5', 20) 
    # 

