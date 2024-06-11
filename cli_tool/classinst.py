MODEL = b''

import os
import sys
import pickle
import glob
from statistics import mode
import shutil
import warnings
import argparse
import zlib

from scipy.io import arff
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
# Add the parent directory to sys.path
sys.path.append(parent_dir)
# Allow relative imports
from dataset_gen.converttowav import convert_to_wav #pyright: ignore 
from dataset_gen.splitaudio import split_audiofile # pyright: ignore 
from dataset_gen.normalizedb import normalize_audio #pyright:ignore 
from dataset_gen.extractFreqARFF import create_arff # pyright: ignore 
from dataset_gen.cleandata import clean_file # pyright : ignore

# Global constants, might add flag parsing later for this
DEFAULT_MODEL_LOC = './config/instrumentclassifier'
TEMP_DIR = 'audiotmp/'
SPLIT_LEN = 0.1
WAV_DIR = TEMP_DIR + 'wav/'
SPLIT_DIR = TEMP_DIR + 'split/'
NORMALIZE_DIR = TEMP_DIR + 'normalized/'
ARFF_DIR = TEMP_DIR + 'arff/'
NORMALIZE_DBFS = -20
NUM_HARMONICS = 32

# Put the model binary here

def predict(model, arff_filename):
    data, meta = arff.loadarff(arff_filename)
    df = pd.DataFrame(data)
    
    df.columns = meta.names()

    for column in df.columns:
        if df[column].dtype == object:
            df[column] = df[column].str.decode('utf-8')

    # print('Data head')
    # print('=================================')
    # print(df.head(10))
    # print() 

    attrib = df.iloc[:, :-1].values

    predicted_insts = model.predict(attrib)
    print('Instrument is:', mode(predicted_insts))
    # for inst in predicted_insts:
    #     print(inst)


__USAGE__ = 'python3 classinst.py <audiofile>'\
        'python3 classinst.py -m <model.pkl> <audiofile>'

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    # Case in which a model is supplied
    
   
    end_help = '''
        Put the audio file you would like to analyze as the last argument. It should be an mp3 or mp4
    '''

    parser = argparse.ArgumentParser(prog='classint.py',
                                     description='A program that takes in an audio file and determines what instrument is playing in it', epilog=end_help)
    
    parser.add_argument('-t', '--tempfolder', default='audiotmp/', help='The folder files will be kept in until the program finishes')
    parser.add_argument('-s', '--splitlen', type=float, default=0.1, help='The length of each segment of the audio file')
    parser.add_argument('-d', '--normalizedb', type=int, default=-20, help='The dbfs level to normalize the chopped up samples to. Default is -20') 
    parser.add_argument('-n', '--numharmonics', type=int, default=32, help='The number of harmonics kept from the FFT, should be same as model provided')
    parser.add_argument('-m', '--model', help='The model file used to predict the instrument')
    parser.add_argument('-k', '--keep', action='store_true', default=False, help='Tells the program if it should delete temp files. Setting this flag will keep temp files')
    
    parsed_args, unrecognized_args = parser.parse_known_args()

    if parsed_args.tempfolder:
        WAV_DIR = parsed_args.tempfolder + 'wav/'
        SPLIT_DIR = parsed_args.tempfolder + 'split/'
        NORMALIZE_DIR = parsed_args.tempfolder + 'normalized/'
        ARFF_DIR = parsed_args.tempfolder + 'arff/'

    audio_filename = unrecognized_args[0] 
    if audio_filename == None:
        parser.print_help()
        sys.exit(1)

    os.makedirs(WAV_DIR, exist_ok=True)
    wav_filename = convert_to_wav(audio_filename, WAV_DIR) 

    os.makedirs(SPLIT_DIR, exist_ok=True)

    split_audiofile(wav_filename, SPLIT_LEN, SPLIT_DIR)
    
    filenames = glob.glob(SPLIT_DIR + '/*.wav')
    os.makedirs(NORMALIZE_DIR, exist_ok=True)
    for filename in filenames:
        normalize_audio(filename, NORMALIZE_DIR, NORMALIZE_DBFS)

    # Analyze the audio file
    os.makedirs(ARFF_DIR, exist_ok=True) 

    with warnings.catch_warnings(action="ignore"):
        create_arff(NORMALIZE_DIR, NUM_HARMONICS, 'dataset', ARFF_DIR) 
    
    # Clean up the arff file
    clean_file(ARFF_DIR + 'datasetRaw.arff', ARFF_DIR + 'datasetRaw.arff')
    
    # load the model
    loadad_model = ''
    if parsed_args.model:
        with open(parsed_args.model, 'rb') as f:
            MODEL = pickle.load(f)
    else:
        loadad_model = pickle.loads(MODEL)

    predict(MODEL, ARFF_DIR + 'datasetRaw.arff')

    # Cleanup as long as the flag for keep has not been set
    if not parsed_args.keep:
        shutil.rmtree(parsed_args.tempfolder)
        
