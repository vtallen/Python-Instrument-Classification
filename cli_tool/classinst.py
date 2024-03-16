import os
import sys
import pickle
import glob
from statistics import mode
import shutil
import warnings

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
TEMP_DIR = 'audiotmp/'
SPLIT_LEN = 0.1
WAV_DIR = TEMP_DIR + 'wav/'
SPLIT_DIR = TEMP_DIR + 'split/'
NORMALIZE_DIR = TEMP_DIR + 'normalized/'
ARFF_DIR = TEMP_DIR + 'arff/'
NORMALIZE_DBFS = -20
NUM_HARMONICS = 32


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
    if argc == 4:
        model_filename = argv[2]
        audio_filename = argv[3]
        
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
        with open(model_filename, 'rb') as f:
            model = pickle.load(f)
        
        predict(model, ARFF_DIR + 'datasetRaw.arff')

        # Cleanup
        shutil.rmtree(TEMP_DIR)
        
    elif argc == 2:
        pass
    else:
        print(__USAGE__)
        sys.exit(1)
